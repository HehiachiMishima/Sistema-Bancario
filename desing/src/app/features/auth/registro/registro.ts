import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { mensajeDeError } from '../../../core/errors/error.util';
import { Auth } from '../../../core/services/auth';
import { Notificaciones } from '../../../core/services/notificaciones';
import { Icon } from '../../../shared/ui/icon/icon';
import { LightPillar } from '../../../shared/ui/light-pillar/light-pillar';

@Component({
  selector: 'app-registro',
  imports: [ReactiveFormsModule, RouterLink, Icon, LightPillar],
  templateUrl: './registro.html',
  styleUrl: '../login/login.scss',
})
export class Registro {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);
  private readonly notificaciones = inject(Notificaciones);

  readonly cargando = signal(false);
  readonly error = signal<string | null>(null);
  readonly verContrasena = signal(false);

  readonly formulario = this.fb.nonNullable.group({
    usuario: ['', [Validators.required, Validators.maxLength(50)]],
    nombre: ['', [Validators.required, Validators.maxLength(100)]],
    apellido: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email, Validators.maxLength(100)]],
    telefono: ['', [Validators.maxLength(20)]],
    contrasena: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(100)]],
    confirmar: ['', [Validators.required]],
  });

  campoInvalido(
    campo: 'usuario' | 'nombre' | 'apellido' | 'email' | 'telefono' | 'contrasena' | 'confirmar',
  ): boolean {
    const control = this.formulario.controls[campo];
    return control.touched && control.invalid;
  }

  toggleContrasena(): void {
    this.verContrasena.update((valor) => !valor);
  }

  enviar(): void {
    if (this.cargando()) {
      return;
    }
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const valores = this.formulario.getRawValue();
    if (valores.contrasena !== valores.confirmar) {
      this.error.set('Las contraseñas no coinciden.');
      return;
    }

    this.cargando.set(true);
    this.error.set(null);
    this.auth
      .registrar({
        usuario: valores.usuario,
        contrasena: valores.contrasena,
        nombre: valores.nombre,
        apellido: valores.apellido,
        email: valores.email,
        telefono: valores.telefono || null,
      })
      .subscribe({
        next: (usuario) => {
          this.cargando.set(false);
          this.notificaciones.exito(
            'Cuenta creada',
            `Bienvenido, ${usuario.nombre}. Ya puedes iniciar sesión.`,
          );
          void this.router.navigate(['/login']);
        },
        error: (err: unknown) => {
          this.cargando.set(false);
          this.error.set(mensajeDeError(err));
        },
      });
  }
}
