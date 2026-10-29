import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { Icon } from '../icon/icon';

@Component({
  selector: 'ui-empty',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Icon],
  template: `
    <div class="text-center py-5 px-3">
      <span
        class="d-inline-flex align-items-center justify-content-center rounded-4 bg-body-secondary text-body-secondary mx-auto"
        style="width: 64px; height: 64px"
      >
        <ui-icon [name]="icono()" [size]="28" />
      </span>
      <div class="fs-5 fw-semibold mt-3">{{ titulo() }}</div>
      @if (mensaje()) {
        <p class="text-body-secondary mt-2 mb-0 mx-auto" style="max-width: 46ch">{{ mensaje() }}</p>
      }
      <ng-content />
    </div>
  `,
})
export class EmptyState {
  readonly icono = input<string>('layers');
  readonly titulo = input<string>('Sin datos');
  readonly mensaje = input<string>('');
}
