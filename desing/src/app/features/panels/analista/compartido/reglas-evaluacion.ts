import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { ReglaEvaluada } from '../../../../core/models';
import { Icon } from '../../../../shared/ui/icon/icon';

@Component({
  selector: 'app-reglas-evaluacion',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Icon],
  template: `
    @if (reglas().length === 0) {
      <div class="d-flex align-items-start gap-2 p-3 border border-dashed rounded-3 bg-body-tertiary text-body-secondary small">
        <ui-icon name="info" [size]="18" class="flex-shrink-0 mt-1" />
        <p class="mb-0">
          Esta transacción no pasó por el motor de reglas porque no es una transferencia o pago
          entre cuentas de usuarios con rol USUARIO. Requiere revisión manual.
        </p>
      </div>
    } @else {
      <ul class="list-unstyled d-flex flex-column gap-2 mb-0">
        @for (regla of reglas(); track regla.regla) {
          <li
            class="d-flex align-items-start gap-3 p-3 border rounded-3"
            [class.bg-body-tertiary]="regla.aprobada"
            [class.border-danger-subtle]="!regla.aprobada"
            [class.bg-danger-subtle]="!regla.aprobada"
          >
            <span
              class="d-inline-flex align-items-center justify-content-center rounded-circle flex-shrink-0"
              style="width: 28px; height: 28px"
              [class.bg-success-subtle]="regla.aprobada"
              [class.text-success]="regla.aprobada"
              [class.bg-danger-subtle]="!regla.aprobada"
              [class.text-danger]="!regla.aprobada"
            >
              <ui-icon [name]="regla.aprobada ? 'check' : 'xCircle'" [size]="16" />
            </span>
            <div class="d-flex flex-column gap-1 flex-grow-1" style="min-width: 0">
              <span class="small fw-semibold">{{ regla.titulo }}</span>
              <span class="text-body-secondary" style="font-size: 0.78rem; line-height: 1.5">
                {{ regla.detalle }}
              </span>
            </div>
            <span
              class="badge rounded-pill flex-shrink-0 align-self-center"
              [class.text-bg-success]="regla.aprobada"
              [class.text-bg-danger]="!regla.aprobada"
            >
              {{ regla.aprobada ? 'Pasa' : 'No pasa' }}
            </span>
          </li>
        }
      </ul>
    }
  `,
  styles: `
    .border-dashed {
      border-style: dashed !important;
    }
  `,
})
export class ReglasEvaluacion {
  readonly reglas = input<ReglaEvaluada[]>([]);
}
