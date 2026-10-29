import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Notificaciones, TipoNotificacion } from '../../../core/services/notificaciones';
import { Icon } from '../icon/icon';

const ICONO_POR_TIPO: Record<TipoNotificacion, string> = {
  exito: 'checkCircleFilled',
  error: 'xCircle',
  info: 'info',
  advertencia: 'alertTriangle',
};

@Component({
  selector: 'ui-toast-host',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Icon],
  template: `
    <div
      class="toast-container position-fixed top-0 end-0 p-3 d-flex flex-column gap-2"
      aria-live="polite"
      aria-atomic="true"
    >
      @for (aviso of notificaciones.items(); track aviso.id) {
        <div
          class="toast show align-items-stretch border-0 border-start border-4 shadow-sm"
          [class.border-success]="aviso.tipo === 'exito'"
          [class.border-danger]="aviso.tipo === 'error'"
          [class.border-secondary]="aviso.tipo === 'info'"
          [class.border-warning]="aviso.tipo === 'advertencia'"
          role="status"
        >
          <div class="d-flex">
            <div class="toast-body d-flex align-items-start gap-3 flex-grow-1">
              <span
                class="flex-shrink-0 mt-1"
                [class.text-success]="aviso.tipo === 'exito'"
                [class.text-danger]="aviso.tipo === 'error'"
                [class.text-secondary]="aviso.tipo === 'info'"
                [class.text-warning]="aviso.tipo === 'advertencia'"
              >
                <ui-icon [name]="icono(aviso.tipo)" [size]="20" />
              </span>
              <div class="flex-grow-1" style="min-width: 0">
                <div class="fw-semibold">{{ aviso.titulo }}</div>
                @if (aviso.mensaje) {
                  <div class="small text-body-secondary">{{ aviso.mensaje }}</div>
                }
              </div>
            </div>
            <button
              type="button"
              class="btn-close me-2 mt-2"
              (click)="notificaciones.cerrar(aviso.id)"
              aria-label="Cerrar"
            ></button>
          </div>
        </div>
      }
    </div>
  `,
})
export class ToastHost {
  readonly notificaciones = inject(Notificaciones);

  icono(tipo: TipoNotificacion): string {
    return ICONO_POR_TIPO[tipo];
  }
}
