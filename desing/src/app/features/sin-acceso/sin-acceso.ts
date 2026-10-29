import { Component, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { Auth } from '../../core/services/auth';
import { Icon } from '../../shared/ui/icon/icon';

@Component({
  selector: 'app-sin-acceso',
  imports: [Icon],
  template: `
    <div class="min-vh-100 d-flex align-items-center justify-content-center bg-body-tertiary p-3">
      <div class="card border-0 shadow-sm text-center w-100" style="max-width: 460px">
        <div class="card-body p-4 p-md-5">
          <span
            class="d-inline-flex align-items-center justify-content-center rounded-4 bg-danger-subtle text-danger mb-4"
            style="width: 64px; height: 64px"
          >
            <ui-icon name="lock" [size]="30" />
          </span>
          <h1 class="h3">Acceso denegado</h1>
          <p class="text-body-secondary mt-3 mb-0">
            No tienes el permiso requerido para ver este contenido.
            @if (permiso()) {
              <span class="d-inline-block mt-3 px-3 py-1 rounded-pill bg-body-secondary font-monospace small">
                {{ permiso() }}
              </span>
            }
          </p>
          <div class="d-flex flex-wrap justify-content-center gap-2 mt-4">
            <button type="button" class="btn btn-primary d-inline-flex align-items-center gap-2" (click)="irInicio()">
              <ui-icon name="panel" [size]="18" />
              Volver al inicio
            </button>
            <button type="button" class="btn btn-outline-secondary" (click)="cerrarSesion()">Cerrar sesión</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: `
    :host {
      display: block;
    }
  `,
})
export class SinAcceso {
  private readonly router = inject(Router);
  private readonly auth = inject(Auth);

  readonly permiso = input<string>('');

  irInicio(): void {
    void this.router.navigateByUrl('/');
  }

  cerrarSesion(): void {
    this.auth.cerrarSesion();
  }
}
