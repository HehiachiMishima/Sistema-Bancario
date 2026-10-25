import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { PERMISOS } from '../../../../../core/config/permisos';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { CuentaBancaria, EstadoTransaccion, Transaccion } from '../../../../../core/models';
import { Auth } from '../../../../../core/services/auth';
import { CuentasApi } from '../../../../../core/services/cuentas.api';
import { Notificaciones } from '../../../../../core/services/notificaciones';
import { TransaccionesApi } from '../../../../../core/services/transacciones.api';
import { soles } from '../../../../../core/utils/moneda';
import { ColumnasRedimensionables } from '../../../../../shared/directives/columnas-redimensionables.directive';
import { EmptyState } from '../../../../../shared/ui/empty-state/empty-state';
import { Icon } from '../../../../../shared/ui/icon/icon';
import { Modal } from '../../../../../shared/ui/modal/modal';
import { Paginador } from '../../../../../shared/ui/paginador/paginador';

interface Decision {
  transaccion: Transaccion;
  estado: Extract<EstadoTransaccion, 'APROBADA' | 'RECHAZADA'>;
}

@Component({
  selector: 'app-movimientos',
  imports: [
    ReactiveFormsModule,
    DatePipe,
    Icon,
    Modal,
    EmptyState,
    ColumnasRedimensionables,
    Paginador,
  ],
  templateUrl: './movimientos.html',
  styleUrl: './movimientos.scss',
})
export class Movimientos {
  private readonly fb = inject(FormBuilder);
  private readonly transaccionesApi = inject(TransaccionesApi);
  private readonly cuentasApi = inject(CuentasApi);
  private readonly notificaciones = inject(Notificaciones);
  private readonly auth = inject(Auth);

  readonly permisos = PERMISOS;
  readonly permisosSesion = this.auth.permisos;
  readonly puedeCrear = computed(() => this.permisosSesion().includes(PERMISOS.CREAR_TRANSACCIONES));
  readonly puedeResolver = computed(() => this.permisosSesion().includes(PERMISOS.RESOLVER_CASO));

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly movimientos = signal<Transaccion[]>([]);

  readonly busqueda = signal('');
  readonly filtroEstado = signal('TODOS');
  readonly filtroTipo = signal('TODOS');

  readonly filtrados = computed(() => {
    const termino = this.busqueda().trim().toLowerCase();
    const estado = this.filtroEstado();
    const tipo = this.filtroTipo();
    return this.movimientos().filter((movimiento) => {
      const coincideTexto =
        !termino ||
        [
          movimiento.referencia,
          movimiento.descripcion ?? '',
          movimiento.cuentaOrigenNumero ?? '',
          movimiento.cuentaDestinoNumero ?? '',
        ].some((campo) => campo.toLowerCase().includes(termino));
      const coincideEstado = estado === 'TODOS' || movimiento.estado === estado;
      const coincideTipo = tipo === 'TODOS' || movimiento.tipoTransaccion === tipo;
      return coincideTexto && coincideEstado && coincideTipo;
    });
  });

  readonly pagina = signal(1);
  readonly porPagina = signal(10);

  readonly totalPaginas = computed(() =>
    Math.max(1, Math.ceil(this.filtrados().length / this.porPagina())),
  );

  readonly paginaActual = computed(() =>
    Math.min(Math.max(1, this.pagina()), this.totalPaginas()),
  );

  readonly paginados = computed(() => {
    const inicio = (this.paginaActual() - 1) * this.porPagina();
    return this.filtrados().slice(inicio, inicio + this.porPagina());
  });

  readonly formAbierto = signal(false);
  readonly editando = signal<Transaccion | null>(null);
  readonly guardando = signal(false);

  readonly tipoSeleccionado = signal('DEPOSITO');
  readonly requiereOrigen = computed(() => this.tipoSeleccionado() !== 'DEPOSITO');
  readonly requiereDestino = computed(() => this.tipoSeleccionado() !== 'RETIRO');
  readonly destinoManual = computed(() => this.tipoSeleccionado() === 'TRANSFERENCIA');

  readonly cuentas = signal<CuentaBancaria[]>([]);
  readonly cuentasCargadas = signal(false);
  readonly cargandoCuentas = signal(false);

  readonly cuentasDisponibles = computed(() =>
    [...this.cuentas()]
      .filter((cuenta) => cuenta.activo)
      .sort((a, b) => a.numeroCuenta.localeCompare(b.numeroCuenta)),
  );

  readonly formulario = this.fb.nonNullable.group({
    tipoTransaccion: ['DEPOSITO', [Validators.required]],
    cuentaOrigenId: [null as number | null],
    cuentaDestinoId: [null as number | null],
    cuentaDestinoNumero: ['', [Validators.maxLength(30)]],
    monto: [0, [Validators.required, Validators.min(0.01)]],
    estado: ['PENDIENTE', [Validators.required]],
    descripcion: ['', [Validators.maxLength(255)]],
  });

  readonly decision = signal<Decision | null>(null);
  readonly decidiendo = signal(false);

  readonly eliminarAbierto = signal(false);
  readonly aEliminar = signal<Transaccion | null>(null);
  readonly eliminando = signal(false);

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.transaccionesApi
      .listar()
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (lista) => this.movimientos.set(lista),
        error: (err: unknown) => this.error.set(mensajeDeError(err)),
      });
  }

  buscar(valor: string): void {
    this.busqueda.set(valor);
    this.pagina.set(1);
  }

  cambiarFiltroEstado(valor: string): void {
    this.filtroEstado.set(valor);
    this.pagina.set(1);
  }

  cambiarFiltroTipo(valor: string): void {
    this.filtroTipo.set(valor);
    this.pagina.set(1);
  }

  cambiarPorPagina(valor: number): void {
    this.porPagina.set(valor);
    this.pagina.set(1);
  }

  campoInvalido(campo: 'monto' | 'descripcion'): boolean {
    const control = this.formulario.controls[campo];
    return control.touched && control.invalid;
  }

  abrirCrear(): void {
    if (!this.puedeCrear()) {
      return;
    }
    if (!this.permisosSesion().includes(PERMISOS.VER_CUENTAS)) {
      this.notificaciones.error(
        'Sin acceso a cuentas',
        'Necesitas el permiso VER_CUENTAS para elegir las cuentas del movimiento.',
      );
      return;
    }
    this.editando.set(null);
    this.tipoSeleccionado.set('DEPOSITO');
    this.formulario.reset({
      tipoTransaccion: 'DEPOSITO',
      cuentaOrigenId: null,
      cuentaDestinoId: null,
      cuentaDestinoNumero: '',
      monto: 0,
      estado: 'PENDIENTE',
      descripcion: '',
    });
    this.cargarCuentas();
    this.formAbierto.set(true);
  }

  abrirEditar(movimiento: Transaccion): void {
    this.editando.set(movimiento);
    this.formulario.reset({
      tipoTransaccion: movimiento.tipoTransaccion,
      cuentaOrigenId: movimiento.cuentaOrigenId,
      cuentaDestinoId: movimiento.cuentaDestinoId,
      cuentaDestinoNumero: movimiento.cuentaDestinoNumero ?? '',
      monto: movimiento.monto,
      estado: movimiento.estado,
      descripcion: movimiento.descripcion ?? '',
    });
    this.formAbierto.set(true);
  }

  cerrarForm(): void {
    this.formAbierto.set(false);
    this.editando.set(null);
  }

  cambiarTipo(tipo: string): void {
    this.tipoSeleccionado.set(tipo);
    if (tipo === 'DEPOSITO') {
      this.formulario.controls.cuentaOrigenId.setValue(null);
    }
    if (tipo === 'RETIRO') {
      this.formulario.controls.cuentaDestinoId.setValue(null);
      this.formulario.controls.cuentaDestinoNumero.setValue('');
    }
    if (tipo !== 'TRANSFERENCIA') {
      this.formulario.controls.cuentaDestinoNumero.setValue('');
    }
    if (tipo === 'TRANSFERENCIA') {
      this.formulario.controls.cuentaDestinoId.setValue(null);
    }
  }

  guardar(): void {
    if (this.guardando()) {
      return;
    }
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const valores = this.formulario.getRawValue();
    const editando = this.editando();

    if (editando) {
      this.guardando.set(true);
      this.transaccionesApi
        .actualizar(editando.id, {
          monto: Number(valores.monto),
          estado: valores.estado,
          descripcion: valores.descripcion.trim() || null,
        })
        .pipe(finalize(() => this.guardando.set(false)))
        .subscribe({
          next: (movimiento) => {
            this.notificaciones.exito('Movimiento actualizado', movimiento.referencia);
            this.cerrarForm();
            this.cargar();
          },
          error: (err: unknown) =>
            this.notificaciones.error('No se pudo actualizar', mensajeDeError(err)),
        });
      return;
    }

    const tipo = valores.tipoTransaccion;
    const cuentaDestinoNumero = valores.cuentaDestinoNumero.trim();
    if (this.requiereOrigen() && !valores.cuentaOrigenId) {
      this.notificaciones.error('Cuenta origen requerida', 'Selecciona la cuenta de origen.');
      return;
    }
    if (tipo === 'TRANSFERENCIA' && !cuentaDestinoNumero) {
      this.notificaciones.error(
        'Cuenta destino requerida',
        'Ingresa el número de cuenta del destinatario.',
      );
      return;
    }
    if (tipo !== 'TRANSFERENCIA' && this.requiereDestino() && !valores.cuentaDestinoId) {
      this.notificaciones.error('Cuenta destino requerida', 'Selecciona la cuenta de destino.');
      return;
    }
    const cuentaOrigen = this.cuentas().find((cuenta) => cuenta.id === valores.cuentaOrigenId);
    if (
      tipo === 'TRANSFERENCIA' &&
      cuentaOrigen &&
      cuentaOrigen.numeroCuenta === cuentaDestinoNumero
    ) {
      this.notificaciones.error(
        'Cuentas repetidas',
        'La cuenta origen y la cuenta destino deben ser distintas.',
      );
      return;
    }
    if (tipo === 'PAGO' && valores.cuentaOrigenId === valores.cuentaDestinoId) {
      this.notificaciones.error(
        'Cuentas repetidas',
        'La cuenta origen y la cuenta destino deben ser distintas.',
      );
      return;
    }

    this.guardando.set(true);
    this.transaccionesApi
      .crear({
        tipoTransaccion: tipo,
        cuentaOrigenId: tipo === 'DEPOSITO' ? null : valores.cuentaOrigenId,
        cuentaDestinoId:
          tipo === 'RETIRO' || tipo === 'TRANSFERENCIA' ? null : valores.cuentaDestinoId,
        cuentaDestinoNumero: tipo === 'TRANSFERENCIA' ? cuentaDestinoNumero : null,
        monto: Number(valores.monto),
        descripcion: valores.descripcion.trim() || null,
      })
      .pipe(finalize(() => this.guardando.set(false)))
      .subscribe({
        next: (movimiento) => {
          if (movimiento.estado === 'APROBADA') {
            this.notificaciones.exito(
              'Movimiento aprobado',
              `${movimiento.referencia} · aprobado automáticamente por las reglas.`,
            );
          } else {
            this.notificaciones.exito(
              'Movimiento registrado',
              `${movimiento.referencia} · pendiente de resolución.`,
            );
          }
          this.cerrarForm();
          this.cargar();
        },
        error: (err: unknown) =>
          this.notificaciones.error('No se pudo registrar', mensajeDeError(err)),
      });
  }

  private cargarCuentas(): void {
    if (this.cuentasCargadas() || this.cargandoCuentas()) {
      return;
    }
    this.cargandoCuentas.set(true);
    this.cuentasApi
      .listar()
      .pipe(finalize(() => this.cargandoCuentas.set(false)))
      .subscribe({
        next: (lista) => {
          this.cuentas.set(lista);
          this.cuentasCargadas.set(true);
        },
        error: (err: unknown) =>
          this.notificaciones.error('No se pudieron cargar las cuentas', mensajeDeError(err)),
      });
  }

  pedirDecision(
    transaccion: Transaccion,
    estado: Extract<EstadoTransaccion, 'APROBADA' | 'RECHAZADA'>,
  ): void {
    if (!this.puedeResolver()) {
      return;
    }
    this.decision.set({ transaccion, estado });
  }

  cerrarDecision(): void {
    if (!this.decidiendo()) {
      this.decision.set(null);
    }
  }

  confirmarDecision(): void {
    const decision = this.decision();
    if (!decision || this.decidiendo()) {
      return;
    }
    this.decidiendo.set(true);
    this.transaccionesApi
      .actualizar(decision.transaccion.id, { estado: decision.estado })
      .pipe(finalize(() => this.decidiendo.set(false)))
      .subscribe({
        next: (movimiento) => {
          this.movimientos.update((lista) =>
            lista.map((item) => (item.id === movimiento.id ? movimiento : item)),
          );
          this.notificaciones.info(
            decision.estado === 'APROBADA' ? 'Movimiento aprobado' : 'Movimiento rechazado',
            movimiento.referencia,
          );
          this.decision.set(null);
        },
        error: (err: unknown) =>
          this.notificaciones.error('No se pudo resolver el movimiento', mensajeDeError(err)),
      });
  }

  confirmarEliminar(movimiento: Transaccion): void {
    this.aEliminar.set(movimiento);
    this.eliminarAbierto.set(true);
  }

  eliminar(): void {
    const movimiento = this.aEliminar();
    if (!movimiento || this.eliminando()) {
      return;
    }
    this.eliminando.set(true);
    this.transaccionesApi
      .eliminar(movimiento.id)
      .pipe(finalize(() => this.eliminando.set(false)))
      .subscribe({
        next: () => {
          this.movimientos.update((lista) => lista.filter((item) => item.id !== movimiento.id));
          this.notificaciones.exito('Movimiento eliminado', movimiento.referencia);
          this.eliminarAbierto.set(false);
          this.aEliminar.set(null);
        },
        error: (err: unknown) =>
          this.notificaciones.error('No se pudo eliminar', mensajeDeError(err)),
      });
  }

  tipoLabel(tipo: string): string {
    switch (tipo) {
      case 'DEPOSITO':
        return 'Depósito';
      case 'RETIRO':
        return 'Retiro';
      case 'TRANSFERENCIA':
        return 'Transferencia';
      case 'PAGO':
        return 'Pago';
      default:
        return tipo;
    }
  }

  estadoLabel(estado: string): string {
    switch (estado) {
      case 'PENDIENTE':
        return 'Pendiente';
      case 'APROBADA':
        return 'Aprobada';
      case 'RECHAZADA':
        return 'Rechazada';
      default:
        return estado;
    }
  }

  badgeClass(estado: string): string {
    switch (estado) {
      case 'APROBADA':
        return 'ui-badge ui-badge--success';
      case 'RECHAZADA':
        return 'ui-badge ui-badge--danger';
      case 'PENDIENTE':
        return 'ui-badge ui-badge--info';
      default:
        return 'ui-badge ui-badge--neutral';
    }
  }

  soles(valor: number): string {
    return soles(valor);
  }
}
