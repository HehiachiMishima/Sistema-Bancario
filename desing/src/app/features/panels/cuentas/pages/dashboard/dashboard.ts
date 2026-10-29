import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { PANEL_CUENTAS } from '../../../../../core/config/paneles';
import { PERMISOS } from '../../../../../core/config/permisos';
import { mensajeDeError } from '../../../../../core/errors/error.util';
import { CuentaDashboard } from '../../../../../core/models';
import { Auth } from '../../../../../core/services/auth';
import { CuentasApi } from '../../../../../core/services/cuentas.api';
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
  selector: 'app-cuentas-dashboard',
  imports: [DatePipe, RouterLink, Icon, DonutChart, BarChart, GaugeChart, EmptyState],
  templateUrl: './dashboard.html',
  styleUrl: '../../../compartido/dashboard.scss',
})
export class CuentasDashboard {
  private readonly auth = inject(Auth);
  private readonly cuentasApi = inject(CuentasApi);

  readonly usuario = this.auth.usuario;
  readonly panelRuta = PANEL_CUENTAS.ruta;
  readonly permisos = this.auth.permisos;

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly datos = signal<CuentaDashboard | null>(null);

  readonly kpis = computed(() => this.datos()?.kpis ?? null);

  readonly pctActivas = computed(() => {
    const kpis = this.kpis();
    if (!kpis || kpis.total === 0) {
      return 0;
    }
    return Math.round((kpis.activas / kpis.total) * 100);
  });

  readonly metricas = computed<Metrica[]>(() => {
    const kpis = this.kpis();
    return [
      {
        id: 'total',
        etiqueta: 'Cuentas',
        icono: 'bank',
        valor: kpis ? String(kpis.total) : null,
        detalle: kpis ? `${kpis.activas} activas · ${kpis.inactivas} inactivas` : 'Sin datos',
        acento: 'brand',
      },
      {
        id: 'saldo',
        etiqueta: 'Saldo total',
        icono: 'money',
        valor: kpis ? soles(kpis.saldoTotal) : null,
        detalle: kpis ? 'Saldo consolidado' : 'Sin datos',
        acento: 'success',
      },
      {
        id: 'activas',
        etiqueta: 'Activas',
        icono: 'wallet',
        valor: kpis ? String(kpis.activas) : null,
        detalle: kpis ? `${this.pctActivas()}% del total` : 'Sin datos',
        acento: 'accent',
      },
      {
        id: 'inactivas',
        etiqueta: 'Inactivas',
        icono: 'lock',
        valor: kpis ? String(kpis.inactivas) : null,
        detalle: 'Cerradas o bloqueadas',
        acento: 'danger',
      },
    ];
  });

  readonly modulos = computed(() =>
    PANEL_CUENTAS.modulos.filter((modulo) => this.permisos().includes(modulo.permiso)),
  );

  readonly hayDatos = computed(() => (this.kpis()?.total ?? 0) > 0);

  readonly segmentosTipo = computed<SegmentoDonut[]>(() => {
    const porTipo = this.datos()?.porTipo ?? [];
    const colores = ['var(--brand)', 'var(--text-2)', 'var(--success)', 'var(--info)'];
    return porTipo
      .filter((item) => item.valor > 0)
      .map((item, indice) => ({
        etiqueta: this.tipoLabel(item.etiqueta),
        valor: item.valor,
        color: colores[indice % colores.length],
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
    this.cuentasApi
      .dashboard()
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (datos) => this.datos.set(datos),
        error: (err: unknown) => this.error.set(mensajeDeError(err)),
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
