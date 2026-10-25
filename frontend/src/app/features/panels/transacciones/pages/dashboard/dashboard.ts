import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { PANEL_TRANSACCIONES } from '../../../../../core/config/paneles';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { TransaccionDashboard } from '../../../../../core/models';
import { Auth } from '../../../../../core/services/auth';
import { TransaccionesApi } from '../../../../../core/services/transacciones.api';
import { soles } from '../../../../../core/utils/moneda';
import { BarChart, BarraDato } from '../../../../../shared/ui/charts/bar-chart';
import { DonutChart, SegmentoDonut } from '../../../../../shared/ui/charts/donut-chart';
import { GaugeChart } from '../../../../../shared/ui/charts/gauge-chart';
import { EmptyState } from '../../../../../shared/ui/empty-state/empty-state';
import { Icon } from '../../../../../shared/ui/icon/icon';

interface Metrica {
  id: string;
  etiqueta: string;
  icono: string;
  valor: string | null;
  detalle: string;
  acento: 'brand' | 'accent' | 'success' | 'danger';
}

@Component({
  selector: 'app-transacciones-dashboard',
  imports: [DatePipe, RouterLink, Icon, DonutChart, BarChart, GaugeChart, EmptyState],
  templateUrl: './dashboard.html',
  styleUrl: '../../../compartido/dashboard.scss',
})
export class TransaccionesDashboard {
  private readonly auth = inject(Auth);
  private readonly transaccionesApi = inject(TransaccionesApi);

  readonly usuario = this.auth.usuario;
  readonly panelRuta = PANEL_TRANSACCIONES.ruta;
  readonly permisos = this.auth.permisos;

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly datos = signal<TransaccionDashboard | null>(null);

  readonly kpis = computed(() => this.datos()?.kpis ?? null);

  readonly pctAprobadas = computed(() => {
    const kpis = this.kpis();
    if (!kpis) {
      return 0;
    }
    const resueltas = kpis.aprobadas + kpis.rechazadas;
    return resueltas === 0 ? 0 : Math.round((kpis.aprobadas / resueltas) * 100);
  });

  readonly metricas = computed<Metrica[]>(() => {
    const kpis = this.kpis();
    return [
      {
        id: 'total',
        etiqueta: 'Movimientos',
        icono: 'transfer',
        valor: kpis ? String(kpis.total) : null,
        detalle: kpis ? `${kpis.rechazadas} rechazados` : 'Sin datos',
        acento: 'brand',
      },
      {
        id: 'pendientes',
        etiqueta: 'Pendientes',
        icono: 'clock',
        valor: kpis ? String(kpis.pendientes) : null,
        detalle: kpis ? soles(kpis.montoPendiente) + ' por resolver' : 'Sin datos',
        acento: 'accent',
      },
      {
        id: 'aprobadas',
        etiqueta: 'Aprobadas',
        icono: 'checkCircleFilled',
        valor: kpis ? String(kpis.aprobadas) : null,
        detalle: kpis ? `${this.pctAprobadas()}% de los resueltos` : 'Sin datos',
        acento: 'success',
      },
      {
        id: 'monto',
        etiqueta: 'Monto aprobado',
        icono: 'money',
        valor: kpis ? soles(kpis.montoAprobado) : null,
        detalle: 'Volumen autorizado',
        acento: 'brand',
      },
    ];
  });

  readonly modulos = computed(() =>
    PANEL_TRANSACCIONES.modulos.filter((modulo) => this.permisos().includes(modulo.permiso)),
  );

  readonly hayDatos = computed(() => (this.kpis()?.total ?? 0) > 0);

  readonly segmentosEstado = computed<SegmentoDonut[]>(() => {
    const porEstado = this.datos()?.porEstado ?? [];
    return porEstado
      .filter((item) => item.valor > 0)
      .map((item) => ({
        etiqueta: this.estadoLabel(item.etiqueta),
        valor: item.valor,
        color: this.colorEstado(item.etiqueta),
      }));
  });

  readonly barrasTipo = computed<BarraDato[]>(() => {
    const porTipo = this.datos()?.porTipo ?? [];
    const colores = ['var(--brand)', 'var(--text-2)', 'var(--success)', 'var(--info)'];
    return porTipo.map((item, indice) => ({
      etiqueta: this.tipoLabel(item.etiqueta),
      valor: item.valor,
      color: colores[indice % colores.length],
    }));
  });

  readonly recientes = computed(() => this.datos()?.recientes ?? []);

  readonly saludo = computed(() => {
    const hora = new Date().getHours();
    if (hora < 12) {
      return 'Buenos días';
    }
    if (hora < 19) {
      return 'Buenas tardes';
    }
    return 'Buenas noches';
  });

  constructor() {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.transaccionesApi
      .dashboard()
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (datos) => this.datos.set(datos),
        error: (err: unknown) => this.error.set(mensajeDeError(err)),
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

  colorEstado(estado: string): string {
    switch (estado) {
      case 'APROBADA':
        return 'var(--success)';
      case 'RECHAZADA':
        return 'var(--danger)';
      case 'PENDIENTE':
        return 'var(--info)';
      default:
        return 'var(--text-3)';
    }
  }

  soles(valor: number): string {
    return soles(valor);
  }
}
