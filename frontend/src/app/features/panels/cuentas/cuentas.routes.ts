import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { PANEL_CUENTAS, primerModuloAccesible } from '../../../core/config/paneles';
import { PERMISOS } from '../../../core/config/permisos';
import { permisoGuard } from '../../../core/guards/permiso.guard';
import { SesionStore } from '../../../core/services/sesion';
import { PanelShell } from '../compartido/panel-shell';

function primerModuloCuentas(): string {
  try {
    const modulo = primerModuloAccesible(PANEL_CUENTAS, inject(SesionStore).permisos());
    return modulo ? `/cuentas/${modulo.ruta}` : '/sin-acceso';
  } catch {
    return '/cuentas/dashboard';
  }
}

export const CUENTAS_ROUTES: Routes = [
  {
    path: '',
    component: PanelShell,
    data: { panel: PANEL_CUENTAS },
    children: [
      { path: '', pathMatch: 'full', redirectTo: primerModuloCuentas },
      {
        path: 'dashboard',
        canActivate: [permisoGuard(PERMISOS.DASHBOARD_CUENTAS)],
        loadComponent: () => import('./pages/dashboard/dashboard').then((m) => m.CuentasDashboard),
      },
      {
        path: 'cuentas',
        canActivate: [permisoGuard(PERMISOS.VER_CUENTAS)],
        loadComponent: () => import('./pages/cuentas/cuentas').then((m) => m.Cuentas),
      },
    ],
  },
];
