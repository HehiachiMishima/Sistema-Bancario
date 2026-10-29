import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  effect,
  inject,
  input,
  output,
  viewChild,
} from '@angular/core';

export type AnchoModal = 'sm' | 'md' | 'lg';

const ENFOCABLES =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

@Component({
  selector: 'ui-modal',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [],
  host: {
    '(document:keydown)': 'alTecla($event)',
  },
  template: `
    @if (abierto()) {
      <div class="modal show d-block" tabindex="-1" (click)="alClicFondo($event)">
        <div
          class="modal-dialog modal-dialog-centered modal-dialog-scrollable"
          [class.modal-sm]="ancho() === 'sm'"
          [class.modal-lg]="ancho() === 'lg'"
          [class.modal-compacto]="compacto()"
        >
          <section
            #dialogo
            class="modal-content"
            role="dialog"
            aria-modal="true"
            tabindex="-1"
            [attr.aria-label]="titulo()"
          >
            <header class="modal-header">
              <div class="me-3">
                <h2 class="modal-title fs-5">{{ titulo() }}</h2>
                @if (subtitulo()) {
                  <p class="text-body-secondary small mb-0">{{ subtitulo() }}</p>
                }
              </div>
              <button type="button" class="btn-close" (click)="cerrar.emit()" aria-label="Cerrar"></button>
            </header>

            <div class="modal-body">
              <ng-content />
            </div>

            <div class="modal-footer">
              <ng-content select="[modal-footer]" />
            </div>
          </section>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    }
  `,
  styles: `
    :host {
      display: contents;
    }
  `,
})
export class Modal {
  private readonly caja = viewChild<ElementRef<HTMLElement>>('dialogo');
  private focoPrevio: HTMLElement | null = null;

  readonly abierto = input(false);
  readonly titulo = input('');
  readonly subtitulo = input('');
  readonly ancho = input<AnchoModal>('md');
  readonly compacto = input(false);
  readonly cerrar = output<void>();

  constructor() {
    effect(() => {
      const caja = this.caja();
      if (caja && this.focoPrevio === null) {
        this.focoPrevio = document.activeElement as HTMLElement | null;
        this.enfocarPrimero(caja.nativeElement);
      } else if (!caja && this.focoPrevio !== null) {
        this.focoPrevio.focus();
        this.focoPrevio = null;
      }
    });
  }

  alClicFondo(evento: MouseEvent): void {
    if (evento.target === evento.currentTarget) {
      this.cerrar.emit();
    }
  }

  alTecla(evento: KeyboardEvent): void {
    const caja = this.caja();
    if (!caja) {
      return;
    }
    if (evento.key === 'Escape') {
      evento.preventDefault();
      this.cerrar.emit();
      return;
    }
    if (evento.key === 'Tab') {
      this.atraparFoco(evento, caja.nativeElement);
    }
  }

  private enfocarPrimero(raiz: HTMLElement): void {
    const lista = this.enfocables(raiz);
    (lista[0] ?? raiz).focus();
  }

  private atraparFoco(evento: KeyboardEvent, raiz: HTMLElement): void {
    const lista = this.enfocables(raiz);
    if (lista.length === 0) {
      evento.preventDefault();
      raiz.focus();
      return;
    }
    const primero = lista[0];
    const ultimo = lista[lista.length - 1];
    const activo = document.activeElement;
    if (evento.shiftKey && (activo === primero || activo === raiz)) {
      evento.preventDefault();
      ultimo.focus();
    } else if (!evento.shiftKey && activo === ultimo) {
      evento.preventDefault();
      primero.focus();
    }
  }

  private enfocables(raiz: HTMLElement): HTMLElement[] {
    return Array.from(raiz.querySelectorAll<HTMLElement>(ENFOCABLES)).filter(
      (el) => el.getClientRects().length > 0,
    );
  }
}
