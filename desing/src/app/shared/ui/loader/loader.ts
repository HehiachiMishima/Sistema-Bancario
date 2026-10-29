import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Carga } from '../../../core/services/carga';

@Component({
  selector: 'ui-loader',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (carga.visible()) {
      <div class="app-loader" role="status" aria-live="polite">
        <div class="text-center">
          <div
            class="spinner-border text-primary"
            style="width: 3.5rem; height: 3.5rem"
            aria-hidden="true"
          ></div>
          <p class="mt-3 mb-0 fw-semibold text-body-secondary">{{ carga.texto() }}</p>
        </div>
      </div>
    }
  `,
  styles: `
    :host {
      display: contents;
    }

    .app-loader {
      position: fixed;
      inset: 0;
      z-index: 2000;
      display: grid;
      place-items: center;
      background: color-mix(in srgb, var(--bs-body-bg) 78%, transparent);
      backdrop-filter: blur(8px);
      animation: loader-fade 240ms ease both;
    }

    @keyframes loader-fade {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }
  `,
})
export class Loader {
  protected readonly carga = inject(Carga);
}
