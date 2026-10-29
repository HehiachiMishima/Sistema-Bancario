import { ChangeDetectionStrategy, Component, afterNextRender, computed, input, signal } from '@angular/core';

export interface SegmentoDonut {
  etiqueta: string;
  valor: number;
  color: string;
}

interface ArcoDonut {
  etiqueta: string;
  valor: number;
  pct: number;
  color: string;
  dash: string;
  offset: number;
}

@Component({
  selector: 'ui-donut',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="d-flex flex-column align-items-center gap-4 w-100">
      <div
        class="position-relative w-100 donut-ring"
        [style.max-width.px]="tamano()"
        style="aspect-ratio: 1"
      >
        <svg viewBox="0 0 42 42" role="img" class="w-100 h-100" style="transform: rotate(-90deg)" [attr.aria-label]="titulo()">
          <circle class="donut-track" cx="21" cy="21" r="15.9155" />
          @for (arco of arcos(); track arco.etiqueta) {
            <circle
              class="donut-arc"
              cx="21"
              cy="21"
              r="15.9155"
              [attr.stroke-dasharray]="arco.dash"
              [attr.stroke-dashoffset]="arco.offset"
              [style.stroke]="arco.color"
            />
          }
        </svg>
        <div class="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column align-items-center justify-content-center text-center">
          <span class="fw-semibold" style="font-size: clamp(1.7rem, 2.6vw, 2.2rem); line-height: 1">
            {{ total() }}
          </span>
          <span class="text-uppercase text-body-secondary fw-semibold small" style="letter-spacing: 0.08em">
            {{ centro() }}
          </span>
        </div>
      </div>

      <ul class="list-unstyled d-flex flex-column gap-2 w-100 mb-0">
        @for (arco of arcos(); track arco.etiqueta) {
          <li class="d-flex align-items-center gap-3 small">
            <span class="rounded-circle flex-shrink-0" [style.background]="arco.color" style="width: 10px; height: 10px"></span>
            <span class="text-body-secondary flex-grow-1">{{ arco.etiqueta }}</span>
            <span class="fw-semibold">{{ arco.valor }}</span>
            <span class="text-body-secondary text-end" style="min-width: 3ch; font-variant-numeric: tabular-nums">
              {{ arco.pct }}%
            </span>
          </li>
        }
      </ul>
    </div>
  `,
  styles: `
    :host {
      display: block;
    }

    .donut-ring {
      animation: donut-in 900ms cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .donut-track {
      fill: none;
      stroke: var(--bs-secondary-bg);
      stroke-width: 4.4;
    }

    .donut-arc {
      fill: none;
      stroke-width: 4.4;
      stroke-linecap: round;
      transition: stroke-dasharray 900ms cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes donut-in {
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
export class DonutChart {
  readonly segmentos = input<SegmentoDonut[]>([]);
  readonly centro = input<string>('Total');
  readonly titulo = input<string>('Distribución');
  readonly tamano = input<number>(220);

  private readonly listo = signal(false);

  constructor() {
    afterNextRender(() => this.listo.set(true));
  }

  readonly total = computed(() =>
    this.segmentos().reduce((acc, segmento) => acc + Math.max(0, segmento.valor), 0),
  );

  readonly arcos = computed<ArcoDonut[]>(() => {
    const segmentos = this.segmentos().filter((segmento) => segmento.valor > 0);
    const total = segmentos.reduce((acc, segmento) => acc + segmento.valor, 0);
    let acumulado = 0;

    return segmentos.map((segmento) => {
      const pct = total > 0 ? (segmento.valor / total) * 100 : 0;
      const offset = -acumulado;
      acumulado += pct;
      return {
        etiqueta: segmento.etiqueta,
        valor: segmento.valor,
        color: segmento.color,
        pct: Math.round(pct),
        dash: this.listo() ? `${pct} ${100 - pct}` : '0 100',
        offset,
      };
    });
  });
}
