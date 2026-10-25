import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { PERMISOS } from '../../../../../core/config/permisos';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { CuentaBancaria } from '../../../../../core/models';
import { Auth } from '../../../../../core/services/auth';
import { CuentasApi } from '../../../../../core/services/cuentas.api';
import { Notificaciones } from '../../../../../core/services/notificaciones';
import { soles } from '../../../../../core/utils/moneda';
import { ColumnasRedimensionables } from '../../../../../shared/directives/columnas-redimensionables.directive';
import { HasPermiso } from '../../../../../shared/directives/has-permiso.directive';
import { EmptyState } from '../../../../../shared/ui/empty-state/empty-state';
import { Icon } from '../../../../../shared/ui/icon/icon';
import { Modal } from '../../../../../shared/ui/modal/modal';
import { Paginador } from '../../../../../shared/ui/paginador/paginador';

@Component({
  selector: 'app-cuentas',
  imports: [
    ReactiveFormsModule,
    DatePipe,
    Icon,
    Modal,
    EmptyState,
    HasPermiso,
    ColumnasRedimensionables,
    Paginador,
  ],
  templateUrl: './cuentas.html',
  styleUrl: './cuentas.scss',
})
export class Cuentas {
  private readonly fb = inject(FormBuilder);
  private readonly cuentasApi = inject(CuentasApi);
  private readonly notificaciones = inject(Notificaciones);
  private readonly auth = inject(Auth);

  readonly permisos = PERMISOS;
  readonly permisosSesion = this.auth.permisos;

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly cuentas = signal<CuentaBancaria[]>([]);

  readonly busqueda = signal('');
  readonly filtroTipo = signal('TODOS');
  readonly filtroEstado = signal('TODOS');

  readonly filtrados = computed(() => {
    const termino = this.busqueda().trim().toLowerCase();
    const tipo = this.filtroTipo();
    const estado = this.filtroEstado();
    return this.cuentas().filter((cuenta) => {
      const coincideTexto =
        !termino ||
        [cuenta.numeroCuenta, cuenta.titular, cuenta.tipoCuenta]
          .filter(Boolean)
          .some((campo) => campo.toLowerCase().includes(termino));
      const coincideTipo = tipo === 'TODOS' || cuenta.tipoCuenta === tipo;
      const coincideEstado =
        estado === 'TODOS' || (estado === 'ACTIVAS' ? cuenta.activo : !cuenta.activo);
      return coincideTexto && coincideTipo && coincideEstado;
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
  readonly editando = signal<CuentaBancaria | null>(null);
  readonly guardando = signal(false);

  readonly formulario = this.fb.nonNullable.group({
    numeroCuenta: ['', [Validators.maxLength(30), Validators.pattern(/^[0-9-]*$/)]],
    tipoCuenta: ['AHORRO', [Validators.required]],
    saldo: [0, [Validators.required, Validators.min(0)]],
  });

  readonly eliminarAbierto = signal(false);
  readonly aEliminar = signal<CuentaBancaria | null>(null);
  readonly eliminando = signal(false);

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.cuentasApi
      .listar()
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (lista) => this.cuentas.set(lista),
        error: (err: unknown) => this.error.set(mensajeDeError(err)),
      });
  }

  buscar(valor: string): void {
    this.busqueda.set(valor);
    this.pagina.set(1);
  }

  cambiarFiltroTipo(valor: string): void {
    this.filtroTipo.set(valor);
    this.pagina.set(1);
  }

  cambiarFiltroEstado(valor: string): void {
    this.filtroEstado.set(valor);
    this.pagina.set(1);
  }

  cambiarPorPagina(valor: number): void {
    this.porPagina.set(valor);
    this.pagina.set(1);
  }

  campoInvalido(campo: 'numeroCuenta' | 'tipoCuenta' | 'saldo'): boolean {
    const control = this.formulario.controls[campo];
    return control.touched && control.invalid;
  }

  abrirCrear(): void {
    this.editando.set(null);
    this.formulario.reset({ numeroCuenta: '', tipoCuenta: 'AHORRO', saldo: 0 });
    this.formAbierto.set(true);
  }

  abrirEditar(cuenta: CuentaBancaria): void {
    this.editando.set(cuenta);
    this.formulario.reset({
      numeroCuenta: cuenta.numeroCuenta,
      tipoCuenta: cuenta.tipoCuenta,
      saldo: cuenta.saldo,
    });
    this.formAbierto.set(true);
  }

  cerrarForm(): void {
    this.formAbierto.set(false);
    this.editando.set(null);
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
    const numero = valores.numeroCuenta.trim();
    const peticion = {
      numeroCuenta: numero || null,
      tipoCuenta: valores.tipoCuenta,
      saldo: Number(valores.saldo),
    };
    const editando = this.editando();
    this.guardando.set(true);

    const operacion = editando
      ? this.cuentasApi.actualizar(editando.id, peticion)
      : this.cuentasApi.crear(peticion);

    operacion.pipe(finalize(() => this.guardando.set(false))).subscribe({
      next: (cuenta) => {
        this.notificaciones.exito(
          editando ? 'Cuenta actualizada' : 'Cuenta creada',
          cuenta.numeroCuenta,
        );
        this.cerrarForm();
        this.cargar();
      },
      error: (err: unknown) => this.notificaciones.error('No se pudo guardar', mensajeDeError(err)),
    });
  }

  alternarActivo(cuenta: CuentaBancaria): void {
    if (!this.permisosSesion().includes(PERMISOS.CAMBIAR_ESTADO_CUENTAS)) {
      return;
    }
    this.cuentasApi.cambiarActivo(cuenta.id, !cuenta.activo).subscribe({
      next: (actualizada) => {
        this.cuentas.update((lista) =>
          lista.map((item) => (item.id === actualizada.id ? actualizada : item)),
        );
        this.notificaciones.info(
          actualizada.activo ? 'Cuenta activada' : 'Cuenta desactivada',
          actualizada.numeroCuenta,
        );
      },
      error: (err: unknown) => this.notificaciones.error('Error', mensajeDeError(err)),
    });
  }

  confirmarEliminar(cuenta: CuentaBancaria): void {
    this.aEliminar.set(cuenta);
    this.eliminarAbierto.set(true);
  }

  eliminar(): void {
    const cuenta = this.aEliminar();
    if (!cuenta || this.eliminando()) {
      return;
    }
    this.eliminando.set(true);
    this.cuentasApi
      .eliminar(cuenta.id)
      .pipe(finalize(() => this.eliminando.set(false)))
      .subscribe({
        next: () => {
          this.cuentas.update((lista) => lista.filter((item) => item.id !== cuenta.id));
          this.notificaciones.exito('Cuenta eliminada', cuenta.numeroCuenta);
          this.eliminarAbierto.set(false);
          this.aEliminar.set(null);
        },
        error: (err: unknown) =>
          this.notificaciones.error('No se pudo eliminar', mensajeDeError(err)),
      });
  }

  tipoLabel(tipo: string): string {
    switch (tipo) {
      case 'AHORRO':
        return 'Ahorro';
      case 'CORRIENTE':
        return 'Corriente';
      case 'EMPRESARIAL':
        return 'Empresarial';
      default:
        return tipo;
    }
  }

  soles(valor: number): string {
    return soles(valor);
  }
}
