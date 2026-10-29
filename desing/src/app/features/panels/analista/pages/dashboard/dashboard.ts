import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { PANEL_ANALISTA } from '../../../../../core/config/paneles';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { AnalistaDashboard } from '../../../../../core/models';
import { AnalistaApi } from '../../../../../core/services/analista.api';
import { Auth } from '../../../../../core/services/auth';
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
  selector: 'app-analista-dashboard',
  imports: [DatePipe, RouterLink, Icon, DonutChart, BarChart, GaugeChart, EmptyState],
  templateUrl: './dashboard.html',
  styleUrl: '../../../compartido/dashboard.scss',
})
export class AnalistaDashboardPage {
  private readonly auth = inject(Auth);
  private readonly analistaApi = inject(AnalistaApi);

  readonly usuario = this.auth.usuario;
  readonly panelRuta = PANEL_ANALISTA.ruta;

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly datos = signal<AnalistaDashboard | null>(null);

  readonly kpis = computed(() => this.datos()?.kpis ?? null);

  readonly pctAuto = computed(() => {
    const kpis = this.kpis();
    if (!kpis || kpis.total === 0) {
      return 0;
    }
    return Math.round((kpis.autoAprobadas / kpis.total) * 100);
  });

  readonly metricas = computed<Metrica[]>(() => {
    const kpis = this.kpis();
    return [
      {
        id: 'total',
        etiqueta: 'Movimientos',
        icono: 'transfer',
        valor: kpis ? String(kpis.total) : null,
        detalle: kpis ? `${kpis.pendientes} pendientes de revisión` : 'Sin datos',
        acento: 'brand',
      },
      {
        id: 'casos',
        etiqueta: 'Casos abiertos',
        icono: 'alertTriangle',
        valor: kpis ? String(kpis.casosAbiertos) : null,
        detalle: kpis ? `${soles(kpis.montoPendiente)} en revisión` : 'Sin datos',
        acento: 'danger',
      },
      {
        id: 'auto',
        etiqueta: 'Aprobadas por reglas',
        icono: 'checkCircleFilled',
        valor: kpis ? String(kpis.autoAprobadas) : null,
        detalle: kpis ? `${this.pctAuto()}% del total` : 'Sin datos',
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
    PANEL_ANALISTA.modulos.filter((modulo) => this.auth.permisos().includes(modulo.permiso)),
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

  readonly casosRecientes = computed(() => this.datos()?.casosRecientes ?? []);

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
    this.analistaApi
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
        return 'badge rounded-pill text-bg-info';
      case 'RESUELTO':
        return 'badge rounded-pill text-bg-success';
      case 'RECHAZADO':
        return 'badge rounded-pill text-bg-danger';
      default:
        return 'badge rounded-pill text-bg-secondary';
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
