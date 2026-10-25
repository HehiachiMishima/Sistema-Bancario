import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { Transaccion } from '../../../../../core/models';
import { AnalistaApi } from '../../../../../core/services/analista.api';
import { soles } from '../../../../../core/utils/moneda';
import { ColumnasRedimensionables } from '../../../../../shared/directives/columnas-redimensionables.directive';
import { EmptyState } from '../../../../../shared/ui/empty-state/empty-state';
import { Icon } from '../../../../../shared/ui/icon/icon';
import { Modal } from '../../../../../shared/ui/modal/modal';
import { Paginador } from '../../../../../shared/ui/paginador/paginador';
import { ReglasEvaluacion } from '../../compartido/reglas-evaluacion';

@Component({
  selector: 'app-analista-transacciones',
  imports: [
    DatePipe,
    Icon,
    Modal,
    EmptyState,
    Paginador,
    ColumnasRedimensionables,
    ReglasEvaluacion,
  ],
  templateUrl: './transacciones.html',
  styleUrl: '../../compartido/tablas.scss',
})
export class AnalistaTransacciones {
  private readonly analistaApi = inject(AnalistaApi);

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly movimientos = signal<Transaccion[]>([]);
  readonly detalle = signal<Transaccion | null>(null);

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
          movimiento.cuentaOrigenTitular ?? '',
          movimiento.cuentaDestinoTitular ?? '',
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

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.analistaApi
      .transacciones()
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

  abrirDetalle(movimiento: Transaccion): void {
    this.detalle.set(movimiento);
  }

  reglasAprobadas(movimiento: Transaccion): number {
    return (movimiento.reglas ?? []).filter((regla) => regla.aprobada).length;
  }

  reglasTotal(movimiento: Transaccion): number {
    return (movimiento.reglas ?? []).length;
  }

  resumenReglas(movimiento: Transaccion): string {
    const total = this.reglasTotal(movimiento);
    if (total === 0) {
      return 'Sin evaluar';
    }
    const aprobadas = this.reglasAprobadas(movimiento);
    return `${aprobadas}/${total} pasan`;
  }

  resumenReglasClass(movimiento: Transaccion): string {
    const total = this.reglasTotal(movimiento);
    if (total === 0) {
      return 'rule-summary';
    }
    return this.reglasAprobadas(movimiento) === total
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
