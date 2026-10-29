import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { PANEL_ANALISTA, primerModuloAccesible } from '../../../core/config/paneles';
import { PERMISOS } from '../../../core/config/permisos';
import { permisoGuard } from '../../../core/guards/permiso.guard';
import { SesionStore } from '../../../core/services/sesion';
import { PanelShell } from '../panel-shell';

function primerModuloAnalista(): string {
  try {
    const modulo = primerModuloAccesible(PANEL_ANALISTA, inject(SesionStore).permisos());
    return modulo ? `/analista/${modulo.ruta}` : '/sin-acceso';
  } catch {
    return '/analista/dashboard';
  }
}

export const ANALISTA_ROUTES: Routes = [
  {
    path: '',
    component: PanelShell,
    data: { panel: PANEL_ANALISTA },
    children: [
      { path: '', pathMatch: 'full', redirectTo: primerModuloAnalista },
      {
        path: 'dashboard',
        canActivate: [permisoGuard(PERMISOS.DASHBOARD_TRANSACCIONES)],
        loadComponent: () => import('./pages/dashboard/dashboard').then((m) => m.AnalistaDashboardPage),
      },
      {
        path: 'transacciones',
        canActivate: [permisoGuard(PERMISOS.VER_TRANSACCIONES)],
        loadComponent: () =>
          import('./pages/transacciones/transacciones').then((m) => m.AnalistaTransacciones),
      },
      {
        path: 'cuentas',
        canActivate: [permisoGuard(PERMISOS.VER_CUENTAS)],
        loadComponent: () =>
          import('../cuentas/pages/cuentas/cuentas').then((m) => m.Cuentas),
      },
      {
        path: 'casos',
        canActivate: [permisoGuard(PERMISOS.RESOLVER_CASO)],
        loadComponent: () => import('./pages/casos/casos').then((m) => m.AnalistaCasos),
      },
    ],
  },
];
