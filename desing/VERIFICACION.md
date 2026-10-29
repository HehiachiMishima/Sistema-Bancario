# Verificación de la réplica — `./desing`

Réplica de `./frontend` con Bootstrap 5.3.8. `./frontend` y `./backend` se usaron
solo como lectura. El proyecto es independiente y consume el mismo backend.

## Stack

| Elemento | Versión / decisión |
| --- | --- |
| Angular | 22.1.0 (misma versión que `./frontend`) |
| Angular CLI | 22.1.8 |
| Bootstrap | 5.3.8 vía npm; SCSS con `@use 'bootstrap/scss/bootstrap'` y bundle JS en `angular.json` |
| ng-bootstrap | No instalado: los modales, toasts, paginador y switch del original son componentes propios y se replicaron igual (la lógica se copió 1:1) |
| Bootstrap Icons | No instalado: el original usa el componente SVG propio `ui-icon`; se conservó |
| Node / npm | 24.21.0 / 11.19.0 |
| Backend | Spring Boot en `http://localhost:2003`, API bajo `/api` |

## Inventario

### Rutas

| Ruta | Pantalla | Guard / permiso | Carga |
| --- | --- | --- | --- |
| `/login` | Login | `guestGuard` | lazy |
| `/registro` | Registro | `guestGuard` | lazy |
| `/` | Launcher de paneles | `authGuard` | lazy |
| `/sin-acceso` | Acceso denegado | `authGuard` | lazy |
| `/admin` | Panel administración | `PANEL_ADMIN` | lazy + hijos |
| `/admin/dashboard` | Dashboard admin | `DASHBOARD_ADMIN` | lazy |
| `/admin/usuarios` | Usuarios | `VER_USUARIOS` | lazy |
| `/admin/roles` | Roles | `VER_ROLES` | lazy |
| `/admin/permisos` | Permisos | `VER_PERMISOS` | lazy |
| `/cuentas` | Panel cuentas | `PANEL_CUENTAS` | lazy + hijos |
| `/cuentas/dashboard` | Dashboard cuentas | `DASHBOARD_CUENTAS` | lazy |
| `/cuentas/cuentas` | Cuentas | `VER_CUENTAS` | lazy |
| `/transacciones` | Panel transacciones | `PANEL_TRANSACCIONES` | lazy + hijos |
| `/transacciones/dashboard` | Dashboard transacciones | `DASHBOARD_TRANSACCIONES` | lazy |
| `/transacciones/movimientos` | Movimientos | `VER_TRANSACCIONES` | lazy |
| `/analista` | Panel analista | `PANEL_ANALISTA` | lazy + hijos |
| `/analista/dashboard` | Dashboard analista | `DASHBOARD_TRANSACCIONES` | lazy |
| `/analista/transacciones` | Transacciones del analista | `VER_TRANSACCIONES` | lazy |
| `/analista/cuentas` | Cuentas (reutiliza página) | `VER_CUENTAS` | lazy |
| `/analista/casos` | Casos | `RESOLVER_CASO` | lazy |
| `**` | Redirección a `/` | — | — |

### Capa no visual

- **Servicios** (`core/services`): `Api`, `Auth`, `SesionStore`, `SesionVigilante`,
  `UsuariosApi`, `RolesApi`, `PermisosApi`, `CuentasApi`, `TransaccionesApi`,
  `AnalistaApi`, `Notificaciones`, `Carga`, `TemaService`, `DirectorioUsuarios`.
- **Modelos** (`core/models`): API, auth, usuario, rol, permiso, cuenta,
  transacción, caso, analista e índice de exportación.
- **Guards**: `authGuard`, `guestGuard`, `permisoGuard`.
- **Interceptors**: `authInterceptor` (Bearer token), `errorInterceptor`
  (normaliza errores y cierra sesión en 401).
- **Configuración**: `configuracion.ts`, `paneles.ts`, `permisos.ts`.
- **Utilidades**: `moneda.ts`, `error.util.ts`.
- **Directivas/pipes**: `appColumnasRedimensionables`, `appHasPermiso`, `actorLabel`.
- **UI compartida**: `ui-icon`, `ui-modal`, `ui-toast-host`, `ui-paginador`,
  `ui-empty`, `ui-loader`, `ui-light-pillar`, gráficos `bar`, `donut`, `gauge`
  y `app-reglas-evaluacion`.

Los 76 archivos `.ts` se copiaron desde `./frontend`. **61 son idénticos byte a
byte**; los otros 15 solo cambian plantillas inline, estilos inline, imports
sin uso y las cadenas de clases que devuelven los métodos de badge. Ningún
cambio afecta estado, validaciones, payloads ni llamadas HTTP.

### Endpoints (todos existen en `./backend`)

| Servicio | Método y ruta | Controlador backend |
| --- | --- | --- |
| Auth | `POST /api/auth/login` | `AuthController` → `POST /login` |
| Auth | `POST /api/auth/registro` | `AuthController` → `POST /registro` |
| Usuarios | `GET /api/usuarios` | `UsuarioController` → `GET` |
| Usuarios | `GET /api/usuarios/buscar` | `UsuarioController` → `GET /buscar` |
| Usuarios | `GET /api/usuarios/{id}` | `UsuarioController` → `GET /{id}` |
| Usuarios | `POST /api/usuarios` | `UsuarioController` → `POST` |
| Usuarios | `PUT /api/usuarios/{id}` | `UsuarioController` → `PUT /{id}` |
| Usuarios | `DELETE /api/usuarios/{id}` | `UsuarioController` → `DELETE /{id}` |
| Usuarios | `PATCH /api/usuarios/{id}/activo` | `UsuarioController` → `PATCH /{id}/activo` |
| Usuarios | `GET/POST/DELETE /api/usuarios/{id}/roles[/{rolId}]` | `UsuarioRolController` |
| Usuarios | `GET /api/usuarios/{id}/permisos` | `UsuarioPermisoController` → `GET` |
| Usuarios | `GET /api/usuarios/{id}/permisos/denegados` | `UsuarioPermisoController` → `GET /denegados` |
| Usuarios | `GET /api/usuarios/{id}/permisos/con-override` | `UsuarioPermisoController` → `GET /con-override` |
| Usuarios | `PUT /api/usuarios/{id}/permisos` | `UsuarioPermisoController` → `PUT` |
| Usuarios | `DELETE /api/usuarios/{id}/permisos/{permisoId}` | `UsuarioPermisoController` → `DELETE /{permisoId}` |
| Resolución | `GET /api/resolucion/usuarios/{id}/efectivos` | `ResolucionController` → `GET /efectivos` |
| Resolución | `GET /api/resolucion/usuarios/{id}/finales` | `ResolucionController` → `GET /finales` |
| Roles | `GET /api/roles`, `GET /api/roles/buscar` | `RolController` |
| Roles | `GET/POST/PUT/DELETE /api/roles[/{id}]` | `RolController` |
| Roles | `PATCH /api/roles/{id}/activo` | `RolController` → `PATCH /{id}/activo` |
| Roles | `GET/POST/DELETE /api/roles/{id}/permisos[/{permisoId}]` | `RolPermisoController` |
| Roles | `GET /api/roles/{id}/usuarios` | `UsuarioRolController` → `GET /roles/{rolId}/usuarios` |
| Permisos | `GET /api/permisos`, `GET /api/permisos/buscar` | `PermisoController` |
| Permisos | `GET/POST/PUT/DELETE /api/permisos[/{id}]` | `PermisoController` |
| Permisos | `PATCH /api/permisos/{id}/activo` | `PermisoController` → `PATCH /{id}/activo` |
| Permisos | `GET /api/permisos/{id}/roles` | `RolPermisoController` → `GET /permisos/{permisoId}/roles` |
| Cuentas | `GET /api/cuentas`, `GET /api/cuentas/dashboard` | `CuentaController` |
| Cuentas | `GET/POST/PUT/DELETE /api/cuentas[/{id}]` | `CuentaController` |
| Cuentas | `PATCH /api/cuentas/{id}/activo` | `CuentaController` → `PATCH /{id}/activo` |
| Transacciones | `GET /api/transacciones`, `GET /api/transacciones/dashboard` | `TransaccionController` |
| Transacciones | `POST /api/transacciones`, `PUT/DELETE /api/transacciones/{id}` | `TransaccionController` |
| Analista | `GET /api/analista/transacciones` | `AnalistaController` → `GET /transacciones` |
| Analista | `GET /api/analista/casos` | `AnalistaController` → `GET /casos` |
| Analista | `GET /api/analista/dashboard` | `AnalistaController` → `GET /dashboard` |

La URL base se toma de `environment.apiUrl`, igual que en el original:
`http://localhost:2003/api` en desarrollo y `/api` en producción.

## Checklist por pantalla

| Pantalla | Funcionalidad replicada | Estructura / lógica | Runtime con datos |
| --- | --- | --- | --- |
| Login | Formulario reactivo, required, mostrar/ocultar contraseña, alerta de error, enlace a registro, `returnUrl` | ✅ | ✅ error 401 mostrado desde el backend |
| Registro | Usuario, nombre, apellido, email, teléfono, contraseña y confirmación, validaciones y alta pública | ✅ | ✅ renderizado |
| Launcher | Tarjetas de los 4 paneles, estado disponible/bloqueado, tema, usuario, logout | ✅ | ⏳ requiere sesión |
| Sin acceso | Mensaje, permiso requerido, volver e iniciar/cerrar sesión | ✅ | ⏳ requiere sesión |
| Dashboard admin | KPIs, gráficos, actividad reciente | ✅ | ⏳ requiere sesión |
| Usuarios | Búsqueda, tabla paginada, alta/edición, activo, roles y overrides (heredado/concedido/denegado), resolución efectiva/final | ✅ | ⏳ requiere sesión |
| Roles | Búsqueda, tabla, alta/edición, activo, permisos del rol, usuarios del rol | ✅ | ⏳ requiere sesión |
| Permisos | Búsqueda, tabla, alta/edición, activo, roles que lo usan | ✅ | ⏳ requiere sesión |
| Dashboard cuentas | KPIs y gráficos de cuentas | ✅ | ⏳ requiere sesión |
| Cuentas | Búsqueda, tabla paginada, alta/edición, activo, eliminación y detalle | ✅ | ⏳ requiere sesión |
| Dashboard transacciones | KPIs, por estado/tipo, recientes | ✅ | ⏳ requiere sesión |
| Movimientos | Filtros, tabla, depósito/retiro/transferencia/pago con contraseña, edición, eliminación, detalle y decisión de casos | ✅ | ⏳ requiere sesión |
| Dashboard analista | KPIs y gráficos de casos | ✅ | ⏳ requiere sesión |
| Transacciones analista | Filtros por estado/tipo, tabla y detalle | ✅ | ⏳ requiere sesión |
| Casos | Búsqueda, filtro por estado, tabla, detalle con reglas evaluadas, aprobar/rechazar | ✅ | ⏳ requiere sesión |

Verificación estructural: se compararon los bindings (`()`, `[]`, `formControlName`,
`routerLink`, `@if`, `@for`, `[class.*]`) de las 16 plantillas contra el original.
Las únicas diferencias son clases de Bootstrap (`is-invalid`, `btn-*`, `text-bg-*`,
etc.). El texto visible es idéntico salvo el separador `/` del breadcrumb, que
Bootstrap dibuja por CSS.

## Diferencias conocidas

1. **Sistema visual**: se sustituyó el design system propio por Bootstrap 5.3.
   La jerarquía, campos, acciones y textos se conservan; cambian radios, sombras,
   tamaños y espaciados propios de Bootstrap.
2. **Modales y toasts**: se mantienen los componentes propios (`ui-modal`,
   `ui-toast-host`) reestilizados con `.modal`, `.toast`, `.btn-close`, etc. No se
   instaló ng-bootstrap para no alterar el foco atrapado ni el comportamiento.
3. **Componentes sin equivalente Bootstrap**: switch de activo, paginador,
   redimensionado de columnas, loader y `ui-light-pillar` conservan su lógica y
   una capa mínima de CSS.
4. **Tema oscuro**: `TemaService` sigue escribiendo `data-theme`; `_tokens.scss`
   lo traduce a variables de Bootstrap. Se ajustaron las superficies de tarjetas,
   modales, sidebar y topbar a los valores del original (`#fff` / `#1d1d1f`).
5. **JS de Bootstrap**: se carga el bundle estándar en `angular.json` según lo
   pedido, pero no se usan atributos `data-bs-*`; toda la interacción es Angular.
6. **SCSS**: `styles.scss` importa Bootstrap y tres capas propias. Las páginas
   conservan solo estilos que Bootstrap no cubre (106 líneas en `panel-shell.scss`,
   22 en `launcher.scss`, 4 en login; el resto son archivos de una línea).
7. **Badges**: los métodos que devuelven clases ahora devuelven clases Bootstrap
   (`badge rounded-pill text-bg-*`); no cambian datos ni condiciones.

## Cómo arrancar

Requisitos: MySQL accesible con el `.env` del backend, JDK 25 para Spring Boot y
Node 24 / npm 11 para Angular.

```bash
# 1) Backend (puerto 2003)
cd backend
./mvnw spring-boot:run

# 2) Réplica (puerto 4200)
cd desing
npm install
npm start
```

Para comparar original y réplica a la vez, levanta la réplica en 4200 y el
original en 4300, permitiendo ambos orígenes en el backend:

```bash
cd backend
CORS_ALLOWED_ORIGINS="http://localhost:4200,http://localhost:4300" ./mvnw spring-boot:run

cd desing && npx ng serve --port 4200
cd frontend && npx ng serve --port 4300
```

El backend solo permite por defecto `http://localhost:4200`. Si abres la app
desde `127.0.0.1:4200`, añade ese origen a `CORS_ALLOWED_ORIGINS`.

## Estado de verificación

- `npx ng build` en `./desing`: **OK** (sin errores; bundle inicial 616 kB,
  130 kB transferidos, rutas lazy separadas).
- `ng serve` en `./desing`: **OK** en `http://127.0.0.1:4200`.
- Login contra backend real: **OK**; credenciales inválidas devuelven y muestran
  `Usuario o contrasena incorrectos.` (CORS, endpoint, payload y manejo de error).
- Registro: **OK** de renderizado y estructura de formulario.
- Paneles autenticados: **pendientes de un usuario de prueba**. No se creó ni
  modificó ningún usuario en la base de datos para no alterar datos del entorno.

## Integridad de `./frontend` y `./backend`

- `git status frontend`: **limpio**.
- `git status backend`: solo aparece
  `backend/src/main/java/oracle/common/config/SeedUsuarioAdmin.java`, una
  modificación que **ya existía antes de este trabajo** (mtime 2026-10-28 19:41,
  anterior al arranque de la verificación). No se tocó ni se revirtió.
- `./desing` es una carpeta nueva sin seguimiento (`?? desing/`).
