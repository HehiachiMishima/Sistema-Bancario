import { Routes } from '@angular/router';
import { PERMISOS } from './core/config/permisos';
import { authGuard } from './core/guards/auth.guard';
import { guestGuard } from './core/guards/guest.guard';
import { permisoGuard } from './core/guards/permiso.guard';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./features/auth/login/login').then((m) => m.Login),
  },
  {
    path: 'registro',
    canActivate: [guestGuard],
    loadComponent: () => import('./features/auth/registro/registro').then((m) => m.Registro),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./features/launcher/launcher').then((m) => m.Launcher),
  },
  {
    path: 'sin-acceso',
    canActivate: [authGuard],
    loadComponent: () => import('./features/sin-acceso/sin-acceso').then((m) => m.SinAcceso),
  },
  {
    path: 'admin',
    canActivate: [permisoGuard(PERMISOS.PANEL_ADMIN)],
    loadChildren: () => import('./features/panels/admin/admin.routes').then((m) => m.ADMIN_ROUTES),
  },
  {
    path: 'cuentas',
    canActivate: [permisoGuard(PERMISOS.PANEL_CUENTAS)],
    loadChildren: () => import('./features/panels/cuentas/cuentas.routes').then((m) => m.CUENTAS_ROUTES),
  },
  {
    path: 'transacciones',
    canActivate: [permisoGuard(PERMISOS.PANEL_TRANSACCIONES)],
    loadChildren: () =>
      import('./features/panels/transacciones/transacciones.routes').then((m) => m.TRANSACCIONES_ROUTES),
  },
  {
    path: 'analista',
    canActivate: [permisoGuard(PERMISOS.PANEL_ANALISTA)],
    loadChildren: () => import('./features/panels/analista/analista.routes').then((m) => m.ANALISTA_ROUTES),
  },
  { path: '**', redirectTo: '' },
];
