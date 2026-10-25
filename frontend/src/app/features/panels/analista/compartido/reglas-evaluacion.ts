import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { ReglaEvaluada } from '../../../../core/models';
import { Icon } from '../../../../shared/ui/icon/icon';

@Component({
  selector: 'app-reglas-evaluacion',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Icon],
  template: `
    @if (reglas().length === 0) {
      <div class="reglas-vacio">
        <ui-icon name="info" [size]="18" />
        <p>
          Esta transacción no pasó por el motor de reglas porque no es una transferencia o pago
          entre cuentas de usuarios con rol USUARIO. Requiere revisión manual.
        </p>
      </div>
    } @else {
      <ul class="reglas">
        @for (regla of reglas(); track regla.regla) {
          <li class="regla" [class.regla--falla]="!regla.aprobada">
            <span class="regla__icon">
              <ui-icon [name]="regla.aprobada ? 'check' : 'xCircle'" [size]="16" />
            </span>
            <div class="regla__text">
              <span class="regla__title">{{ regla.titulo }}</span>
              <span class="regla__detail">{{ regla.detalle }}</span>
            </div>
            <span
              class="ui-badge"
              [class.ui-badge--success]="regla.aprobada"
              [class.ui-badge--danger]="!regla.aprobada"
            >
              {{ regla.aprobada ? 'Pasa' : 'No pasa' }}
            </span>
          </li>
        }
      </ul>
    }
  `,
  styles: `
    .reglas {
      display: flex;
      flex-direction: column;
      gap: var(--space-2);
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .regla {
      display: flex;
      align-items: flex-start;
      gap: var(--space-3);
      padding: var(--space-3) var(--space-4);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--surface-2);
    }

    .regla--falla {
      border-color: color-mix(in srgb, var(--danger) 30%, var(--border));
      background: color-mix(in srgb, var(--danger-soft) 55%, var(--surface));
    }

    .regla__icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      flex: none;
      border-radius: 50%;
      background: var(--success-soft);
      color: var(--success);
    }

    .regla--falla .regla__icon {
      background: var(--danger-soft);
      color: var(--danger);
    }

    .regla__text {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
      flex: 1;
    }

    .regla__title {
      font-size: var(--fs-sm);
      font-weight: 600;
      color: var(--text);
    }

    .regla__detail {
      font-size: var(--fs-xs);
      color: var(--text-2);
      line-height: 1.5;
    }

    .regla .ui-badge {
      flex: none;
      align-self: center;
    }

    .reglas-vacio {
      display: flex;
      align-items: flex-start;
      gap: var(--space-3);
      padding: var(--space-4);
      border: 1px dashed var(--border-strong);
      border-radius: var(--radius);
      color: var(--text-2);
      font-size: var(--fs-sm);
      background: var(--surface-2);

      ui-icon {
        flex: none;
        margin-top: 2px;
        color: var(--text-3);
      }

      p {
        margin: 0;
        line-height: 1.55;
      }
    }
  `,
})
export class ReglasEvaluacion {
  readonly reglas = input<ReglaEvaluada[]>([]);
}
