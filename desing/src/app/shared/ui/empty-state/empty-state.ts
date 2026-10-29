import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { Icon } from '../icon/icon';

@Component({
  selector: 'ui-empty',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Icon],
  template: `
    <div class="ui-empty">
      <span class="ui-empty__icon">
        <ui-icon [name]="icono()" [size]="28" />
      </span>
      <div class="ui-empty__title">{{ titulo() }}</div>
      @if (mensaje()) {
        <p class="ui-empty__text">{{ mensaje() }}</p>
      }
      <ng-content />
    </div>
  `,
  styles: `
    .ui-empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: var(--space-3);
      padding: var(--space-12) var(--space-6);
      color: var(--text-3);
    }

    .ui-empty__icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 64px;
      height: 64px;
      border-radius: var(--radius-lg);
      background: var(--surface-3);
      color: var(--text-2);
    }

    .ui-empty__title {
      color: var(--text);
      font-size: var(--fs-lg);
      font-weight: 600;
    }

    .ui-empty__text {
      max-width: 46ch;
      font-size: var(--fs-md);
    }
  `,
})
export class EmptyState {
  readonly icono = input<string>('layers');
  readonly titulo = input<string>('Sin datos');
  readonly mensaje = input<string>('');
}
