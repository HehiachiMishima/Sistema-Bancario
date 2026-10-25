import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { PANEL_TRANSACCIONES, primerModuloAccesible } from '../../../core/config/paneles';
import { PERMISOS } from '../../../core/config/permisos';
import { permisoGuard } from '../../../core/guards/permiso.guard';
import { SesionStore } from '../../../core/services/sesion';
import { PanelShell } from '../panel-shell';

function primerModuloTransacciones(): string {
  try {
    const modulo = primerModuloAccesible(PANEL_TRANSACCIONES, inject(SesionStore).permisos());
    return modulo ? `/transacciones/${modulo.ruta}` : '/sin-acceso';
  } catch {
    return '/transacciones/dashboard';
  }
}

export const TRANSACCIONES_ROUTES: Routes = [
  {
    path: '',
    component: PanelShell,
    data: { panel: PANEL_TRANSACCIONES },
    children: [
      { path: '', pathMatch: 'full', redirectTo: primerModuloTransacciones },
      {
        path: 'dashboard',
        canActivate: [permisoGuard(PERMISOS.DASHBOARD_TRANSACCIONES)],
        loadComponent: () => import('./pages/dashboard/dashboard').then((m) => m.TransaccionesDashboard),
      },
      {
        path: 'movimientos',
        canActivate: [permisoGuard(PERMISOS.VER_TRANSACCIONES)],
        loadComponent: () => import('./pages/movimientos/movimientos').then((m) => m.Movimientos),
      },
    ],
  },
];
