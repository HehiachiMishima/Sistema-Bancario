import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { Caso, EstadoTransaccion } from '../../../../../core/models';
import { AnalistaApi } from '../../../../../core/services/analista.api';
import { Notificaciones } from '../../../../../core/services/notificaciones';
import { TransaccionesApi } from '../../../../../core/services/transacciones.api';
import { soles } from '../../../../../core/utils/moneda';
import { ColumnasRedimensionables } from '../../../../../shared/directives/columnas-redimensionables.directive';
import { EmptyState } from '../../../../../shared/ui/empty-state/empty-state';
import { Icon } from '../../../../../shared/ui/icon/icon';
import { Modal } from '../../../../../shared/ui/modal/modal';
import { Paginador } from '../../../../../shared/ui/paginador/paginador';
import { ReglasEvaluacion } from '../../compartido/reglas-evaluacion';

interface DecisionCaso {
  caso: Caso;
  estado: Extract<EstadoTransaccion, 'APROBADA' | 'RECHAZADA'>;
}

@Component({
  selector: 'app-analista-casos',
  imports: [
    DatePipe,
    Icon,
    Modal,
    EmptyState,
    Paginador,
    ColumnasRedimensionables,
    ReglasEvaluacion,
  ],
  templateUrl: './casos.html',
  styleUrl: '../../compartido/tablas.scss',
})
export class AnalistaCasos {
  private readonly analistaApi = inject(AnalistaApi);
  private readonly transaccionesApi = inject(TransaccionesApi);
  private readonly notificaciones = inject(Notificaciones);

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly casos = signal<Caso[]>([]);
  readonly detalle = signal<Caso | null>(null);

  readonly busqueda = signal('');
  readonly filtroEstado = signal('ABIERTO');

  readonly filtrados = computed(() => {
    const termino = this.busqueda().trim().toLowerCase();
    return this.casos().filter((caso) => {
      const transaccion = caso.transaccion;
      if (!termino) {
        return true;
      }
      return [
        caso.numeroCaso,
        caso.estado,
        transaccion.referencia,
        transaccion.descripcion ?? '',
        transaccion.cuentaOrigenNumero ?? '',
        transaccion.cuentaDestinoNumero ?? '',
        transaccion.cuentaOrigenTitular ?? '',
        transaccion.cuentaDestinoTitular ?? '',
      ].some((campo) => campo.toLowerCase().includes(termino));
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

  readonly decision = signal<DecisionCaso | null>(null);
  readonly decidiendo = signal(false);

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.analistaApi
      .casos(this.estadoApi())
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (lista) => this.casos.set(lista),
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
    this.cargar();
  }

  cambiarPorPagina(valor: number): void {
    this.porPagina.set(valor);
    this.pagina.set(1);
  }

  abrirDetalle(caso: Caso): void {
    this.detalle.set(caso);
  }

  pedirDecision(
    caso: Caso,
    estado: Extract<EstadoTransaccion, 'APROBADA' | 'RECHAZADA'>,
  ): void {
    if (!this.puedeResolver(caso)) {
      return;
    }
    this.decision.set({ caso, estado });
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
      .actualizar(decision.caso.transaccion.id, { estado: decision.estado })
      .pipe(finalize(() => this.decidiendo.set(false)))
      .subscribe({
        next: () => {
          this.notificaciones.info(
            decision.estado === 'APROBADA' ? 'Caso aprobado' : 'Caso rechazado',
            `${decision.caso.numeroCaso} · ${decision.caso.transaccion.referencia}`,
          );
          this.decision.set(null);
          this.detalle.set(null);
          this.cargar();
        },
        error: (err: unknown) =>
          this.notificaciones.error('No se pudo resolver el caso', mensajeDeError(err)),
      });
  }

  puedeResolver(caso: Caso): boolean {
    return caso.transaccion.estado === 'PENDIENTE';
  }

  reglasAprobadas(caso: Caso): number {
    return (caso.transaccion.reglas ?? []).filter((regla) => regla.aprobada).length;
  }

  reglasTotal(caso: Caso): number {
    return (caso.transaccion.reglas ?? []).length;
  }

  reglasFallidas(caso: Caso): number {
    return this.reglasTotal(caso) - this.reglasAprobadas(caso);
  }

  resumenReglas(caso: Caso): string {
    const total = this.reglasTotal(caso);
    if (total === 0) {
      return 'Sin evaluar';
    }
    const fallidas = this.reglasFallidas(caso);
    return fallidas === 0 ? 'Todas pasan' : `${fallidas} no ${fallidas === 1 ? 'pasa' : 'pasan'}`;
  }

  resumenReglasClass(caso: Caso): string {
    const total = this.reglasTotal(caso);
    if (total === 0) {
      return 'rule-summary';
    }
    return this.reglasFallidas(caso) === 0
      ? 'rule-summary rule-summary--ok'
      : 'rule-summary rule-summary--falla';
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

  estadoCasoLabel(estado: string): string {
    switch (estado) {
      case 'ABIERTO':
        return 'Abierto';
      case 'EN_REVISION':
        return 'En revisión';
      case 'RESUELTO':
        return 'Resuelto';
      case 'CERRADO':
        return 'Cerrado';
      case 'RECHAZADO':
        return 'Rechazado';
      default:
        return estado;
    }
  }

  badgeCasoClass(estado: string): string {
    switch (estado) {
      case 'ABIERTO':
      case 'EN_REVISION':
        return 'ui-badge ui-badge--info';
      case 'RESUELTO':
        return 'ui-badge ui-badge--success';
      case 'RECHAZADO':
        return 'ui-badge ui-badge--danger';
      default:
        return 'ui-badge ui-badge--neutral';
    }
  }

  soles(valor: number): string {
    return soles(valor);
  }

  private estadoApi(): string | undefined {
    return this.filtroEstado() === 'TODOS' ? undefined : this.filtroEstado();
  }
}
