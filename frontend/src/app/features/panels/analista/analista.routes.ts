import { Routes } from '@angular/router';
import { PANEL_ANALISTA } from '../../../core/config/paneles';
import { PanelShell } from '../compartido/panel-shell';

/** Panel del analista: creado y accesible, sin modulos por ahora. */
export const ANALISTA_ROUTES: Routes = [
  {
    path: '',
    component: PanelShell,
    data: { panel: PANEL_ANALISTA },
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () => import('./pages/vacio/vacio').then((m) => m.AnalistaVacio),
      },
    ],
  },
];
