import { Component } from '@angular/core';
import { EmptyState } from '../../../../../shared/ui/empty-state/empty-state';

@Component({
  selector: 'app-analista-vacio',
  imports: [EmptyState],
  template: `
    <header class="page-head">
      <div>
        <h1 class="page-head__title">Analista</h1>
        <p class="page-head__sub">Espacio reservado para la resolución de casos.</p>
      </div>
    </header>

    <div class="vacio">
      <ui-empty
        icono="analytics"
        titulo="Panel en construcción"
        mensaje="Este panel todavía no tiene módulos. Aquí se gestionarán los casos y la resolución de transacciones."
      />
    </div>
  `,
  styles: `
    .vacio {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow-sm);
      padding: var(--space-6);
    }
  `,
})
export class AnalistaVacio {}
