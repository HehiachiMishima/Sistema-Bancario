import { ChangeDetectionStrategy, Component, afterNextRender, computed, input, signal } from '@angular/core';

@Component({
  selector: 'ui-gauge',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div
      class="position-relative w-100 mx-auto gauge"
      [style.max-width.px]="tamano()"
      style="aspect-ratio: 1"
    >
      <svg viewBox="0 0 42 42" class="w-100 h-100" role="img" [attr.aria-label]="etiqueta() + ': ' + valor() + '%'">
        <circle class="gauge-track" cx="21" cy="21" r="15.9155" />
        <g transform="rotate(-90 21 21)">
          <circle
            class="gauge-value"
            cx="21"
            cy="21"
            r="15.9155"
            [attr.stroke-dasharray]="dash()"
            [style.stroke]="color()"
          />
        </g>
      </svg>
      <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column align-items-center justify-content-center">
        <span class="fw-semibold" style="font-size: clamp(1.7rem, 2.6vw, 2.2rem); line-height: 1; font-variant-numeric: tabular-nums">
          {{ valor() }}<span class="text-body-secondary" style="font-size: 0.5em; vertical-align: super">%</span>
        </span>
        <span
          class="text-uppercase text-body-secondary fw-semibold small mt-2 text-center"
          style="letter-spacing: 0.08em"
        >
          {{ etiqueta() }}
        </span>
      </div>
    </div>
  `,
  styles: `
    :host {
      display: block;
    }

    .gauge {
      animation: gauge-in 900ms cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .gauge-track {
      fill: none;
      stroke: var(--bs-secondary-bg);
      stroke-width: 3.6;
    }

    .gauge-value {
      fill: none;
      stroke-width: 4.4;
      stroke-linecap: round;
      transition: stroke-dasharray 1000ms cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes gauge-in {
      from {
        opacity: 0;
        transform: scale(0.85);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }
  `,
})
export class GaugeChart {
  readonly valor = input<number>(0);
  readonly etiqueta = input<string>('Progreso');
  readonly color = input<string>('var(--brand)');
  readonly tamano = input<number>(220);

  private readonly listo = signal(false);

  constructor() {
    afterNextRender(() => this.listo.set(true));
  }

  readonly porcentaje = computed(() => Math.min(100, Math.max(0, Math.round(this.valor()))));

  readonly dash = computed(() => {
    const valor = this.listo() ? this.valor() : 0;
    return `${Math.min(100, Math.max(0, valor))} ${100 - Math.min(100, Math.max(0, valor))}`;
  });
}
