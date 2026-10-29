import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

export interface BarraDato {
  etiqueta: string;
  valor: number;
  color: string;
}

@Component({
  selector: 'ui-bars',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="d-flex align-items-stretch gap-3 gap-md-4 pt-4" [style.height.px]="altura()">
      @for (barra of barras(); track barra.etiqueta; let i = $index) {
        <div class="flex-fill d-flex flex-column align-items-center gap-2" style="min-width: 0">
          <span class="fw-semibold" style="font-variant-numeric: tabular-nums">{{ barra.valor }}</span>
          <div
            class="flex-grow-1 w-100 d-flex align-items-end bg-body-secondary rounded-3 overflow-hidden"
            style="max-width: 68px"
          >
            <div
              class="w-100 rounded-3 bar-fill"
              [style.height.%]="barra.pct"
              [style.background]="barra.color"
              [style.animation-delay]="i * 90 + 'ms'"
            ></div>
          </div>
          <span class="small fw-semibold text-body-secondary text-center text-truncate w-100">
            {{ barra.etiqueta }}
          </span>
        </div>
      }
    </div>
  `,
  styles: `
    :host {
      display: block;
    }

    .bar-fill {
      transform-origin: bottom;
      animation: bar-grow 900ms cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    @keyframes bar-grow {
      from {
        transform: scaleY(0);
        opacity: 0.4;
      }
      to {
        transform: scaleY(1);
        opacity: 1;
      }
    }
  `,
})
export class BarChart {
  readonly datos = input<BarraDato[]>([]);
  readonly altura = input<number>(220);

  readonly barras = computed(() => {
    const datos = this.datos();
    const maximo = Math.max(1, ...datos.map((dato) => dato.valor));
    return datos.map((dato) => ({
      ...dato,
      pct: dato.valor <= 0 ? 0 : Math.max(6, (dato.valor / maximo) * 100),
    }));
  });
}
