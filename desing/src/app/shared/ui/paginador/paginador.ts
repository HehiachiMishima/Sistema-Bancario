import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';
import { Icon } from '../icon/icon';

@Component({
  selector: 'ui-paginador',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Icon],
  template: `
    @if (total() > 0) {
      <div class="d-flex justify-content-end align-items-center px-3 py-2 border-top bg-body-tertiary">
        @if (totalPaginas() > 1) {
          <nav aria-label="Paginación">
            <ul class="pagination pagination-sm mb-0">
              <li class="page-item" [class.disabled]="pagina() <= 1">
                <button
                  type="button"
                  class="page-link"
                  [disabled]="pagina() <= 1"
                  (click)="ir(pagina() - 1)"
                  aria-label="Página anterior"
                >
                  <ui-icon name="chevronLeft" [size]="16" />
                </button>
              </li>

              @for (p of paginas(); track $index) {
                @if (p === 'gap') {
                  <li class="page-item disabled">
                    <span class="page-link" aria-hidden="true">…</span>
                  </li>
                } @else {
                  <li class="page-item" [class.active]="p === pagina()">
                    <button
                      type="button"
                      class="page-link"
                      [attr.aria-current]="p === pagina() ? 'page' : null"
                      (click)="ir(p)"
                    >
                      {{ p }}
                    </button>
                  </li>
                }
              }

              <li class="page-item" [class.disabled]="pagina() >= totalPaginas()">
                <button
                  type="button"
                  class="page-link"
                  [disabled]="pagina() >= totalPaginas()"
                  (click)="ir(pagina() + 1)"
                  aria-label="Página siguiente"
                >
                  <ui-icon name="chevronRight" [size]="16" />
                </button>
              </li>
            </ul>
          </nav>
        }
      </div>
    }
  `,
})
export class Paginador {
  readonly pagina = input<number>(1);
  readonly total = input<number>(0);
  readonly porPagina = input<number>(10);
  readonly opciones = input<number[]>([10, 25, 50]);

  readonly paginaCambia = output<number>();
  readonly porPaginaCambia = output<number>();

  readonly totalPaginas = computed(() => Math.max(1, Math.ceil(this.total() / this.porPagina())));

  readonly desde = computed(() =>
    this.total() === 0 ? 0 : (this.pagina() - 1) * this.porPagina() + 1,
  );

  readonly hasta = computed(() => Math.min(this.total(), this.pagina() * this.porPagina()));

  readonly paginas = computed<(number | 'gap')[]>(() => {
    const total = this.totalPaginas();
    const actual = this.pagina();
    if (total <= 7) {
      return Array.from({ length: total }, (_, i) => i + 1);
    }

    const numeros = new Set<number>([1, actual - 1, actual, actual + 1, total]);
    const ordenados = [...numeros].filter((n) => n >= 1 && n <= total).sort((a, b) => a - b);

    const resultado: (number | 'gap')[] = [];
    let anterior = 0;
    for (const n of ordenados) {
      if (anterior && n - anterior > 1) {
        resultado.push('gap');
      }
      resultado.push(n);
      anterior = n;
    }
    return resultado;
  });

  ir(pagina: number): void {
    const destino = Math.min(Math.max(1, pagina), this.totalPaginas());
    if (destino !== this.pagina()) {
      this.paginaCambia.emit(destino);
    }
  }

  cambiarTamano(evento: Event): void {
    const valor = Number((evento.target as HTMLSelectElement).value);
    if (valor && valor !== this.porPagina()) {
      this.porPaginaCambia.emit(valor);
    }
  }
}
