# Sistema Bancario

Aplicación web para la gestión de cuentas y movimientos bancarios: autenticación con JWT, administración de usuarios y permisos, cuentas, transacciones con motor de reglas y una bandeja de resolución de casos para analistas.

> Proyecto demostrativo: los saldos y movimientos son simulados y **no procesa dinero real**.

---

## Funcionalidades

### Acceso y seguridad

- Inicio de sesión y autorregistro público. Los usuarios nuevos reciben el rol `USUARIO`.
- Sesión con JWT (HS256), permisos resueltos en el backend y renovación de la sesión vigente.
- Contraseñas cifradas con BCrypt, límite de intentos de login y autorización por permiso en cada endpoint.
- Menú y rutas filtrados por permisos; el backend vuelve a validar cada operación con `@PreAuthorize`.

### Paneles

| Panel | Ruta | Módulos |
| --- | --- | --- |
| Administración | `/admin` | Dashboard, usuarios, roles y permisos |
| Cuentas | `/cuentas` | Dashboard y gestión de cuentas |
| Transacciones | `/transacciones` | Dashboard y movimientos |
| Analista | `/analista` | Dashboard, todas las transacciones, cuentas y casos |

- `ADMINISTRADOR` accede a todo el sistema y es un rol protegido: no se puede eliminar ni modificar, solo ampliar con nuevos permisos.
- `ANALISTA` supervisa movimientos de usuarios, edita cuentas y resuelve casos.
- `USUARIO` opera sus propias cuentas y movimientos.

El layout de todos los paneles vive en un único componente, [`frontend/src/app/features/panels/panel-shell.ts`](frontend/src/app/features/panels/panel-shell.ts): sidebar, topbar, tema, menú responsive y cierre de sesión se mantienen en un solo lugar. Cada ruta solo aporta la definición del panel y sus módulos.

### Cuentas

- Creación de cuentas de tipo `AHORRO`, `CORRIENTE` o `EMPRESARIAL`, con número generado automáticamente o personalizado.
- Consulta, edición, activación/desactivación y eliminación según permisos.
- Un usuario normal solo ve y opera sus propias cuentas; administradores y analistas ven todas.
- Una cuenta con movimientos registrados no se puede eliminar: se desactiva para conservar el historial contable.

### Movimientos

Tipos disponibles: `DEPOSITO`, `RETIRO`, `TRANSFERENCIA` y `PAGO`.

- **Depósitos y retiros**: no pasan por el motor de reglas. Se autorizan confirmando la contraseña del usuario y quedan aprobados al instante.
- **Transferencias y pagos**: se evalúan con las reglas de negocio. Si las cumplen y hay saldo suficiente, se aprueban y aplican los saldos; si no, quedan `PENDIENTE` y abren un caso para el analista.
- Estados: `PENDIENTE`, `APROBADA` y `RECHAZADA`.
- Aprobar, rechazar, editar o eliminar un movimiento requiere el permiso `RESOLVER_CASO`. Al revertir una operación aprobada se restauran los saldos.
- Todo el flujo de aprobación y aplicación de saldos ocurre dentro de una transacción SQL con bloqueo pesimista de las cuentas implicadas.

### Motor de reglas

Las transferencias y pagos entre cuentas de usuarios con rol `USUARIO` se evalúan contra estas reglas:

| Regla | Descripción |
| --- | --- |
| R1 | Al menos el 20 % de los movimientos históricos de la cuenta origen van al mismo destino. |
| R2 | Al menos el 20 % de los movimientos históricos son del mismo tipo. |
| R3 | El monto no supera 2,5 veces el promedio histórico de la cuenta origen. |
| R4 | El movimiento no deja la cuenta prácticamente vacía (diferencia mayor al 1 % del saldo, mínimo S/ 0,01). |

Además se exige saldo suficiente. La operación solo se aprueba automáticamente si se cumplen todas las reglas; en caso contrario queda pendiente y se registra la evaluación de cada regla para el analista.

---

## Stack

- **Frontend**: Angular 22 standalone y zoneless, TypeScript, SCSS y signals.
- **Backend**: Spring Boot 4.1.1, Java 21, WebFlux (`Mono`) y virtual threads.
- **Base de datos**: MySQL 8.
- **Autenticación**: JWT HS256 + BCrypt.

---

## Estructura del proyecto

```text
.
├── Dockerfile                  # Imagen única: frontend + backend + nginx
├── render.yaml                 # Blueprint de despliegue en Render
├── backend/
│   ├── .env.example            # Plantilla de variables de entorno
│   ├── schema.sql              # Esquema, datos iniciales, triggers y vistas
│   ├── logica.sql              # Definiciones SQL de apoyo
│   └── src/main/java/oracle/
│       ├── auth/               # Login, registro, sesión y JWT
│       ├── admin/              # Usuarios, roles, permisos y resoluciones
│       ├── bancario/           # Cuentas, transacciones, reglas y casos
│       └── common/             # Seguridad, errores, respuestas y utilidades
└── frontend/src/app/
    ├── core/                   # Configuración, guards, interceptores, modelos y API
    ├── features/
    │   ├── auth/               # Login y registro
    │   ├── launcher/           # Selector de paneles según permisos
    │   └── panels/
    │       ├── panel-shell.*   # Shell único de todos los paneles
    │       ├── admin/
    │       ├── cuentas/
    │       ├── transacciones/
    │       └── analista/
    └── shared/                 # Componentes, gráficos, pipes y directivas
```

---

## Puesta en marcha

### Requisitos

- Java 21 y Node 22.
- MySQL 8 accesible.

### 1. Base de datos

Crea el esquema y los datos iniciales:

```bash
mysql -u root -p < backend/schema.sql
```

El esquema crea la base `sistema_bancario`. Si usas otro nombre, actualiza `DB_NAME` en `backend/.env`.

### 2. Backend

```bash
cp backend/.env.example backend/.env
```

Completa en `backend/.env`:

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_PARAMS`.
- `JWT_SECRET` (mínimo 32 caracteres) y `JWT_ISSUER`.
- `USER_ADMIN`, `USER_PASSWORD` y `USER_EMAIL` para el administrador semilla.
- `CORS_ALLOWED_ORIGINS=http://localhost:4200` en desarrollo.

El archivo `.env` no se sube al repositorio. El administrador semilla se crea al arrancar si no existe y se le asigna el rol indicado en `USER_ROL` (`ADMINISTRADOR`).

```bash
cd backend
./mvnw spring-boot:run
```

API en `http://localhost:2003/api`.

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

SPA en `http://localhost:4200` (usa `environment.development.ts`).

---

## API

Base: `/api`. Todas las rutas requieren `Authorization: Bearer <token>` salvo las públicas indicadas.

| Método | Ruta | Acceso |
| --- | --- | --- |
| `GET` | `/api/health` | Público |
| `POST` | `/api/auth/login` | Público |
| `POST` | `/api/auth/registro` | Público |
| `GET` | `/api/auth/sesion` | Autenticado |
| `PUT` | `/api/auth/contrasena` | Autenticado |
| CRUD | `/api/usuarios`, `/api/roles`, `/api/permisos` | Permisos de administración |
| CRUD | `/api/cuentas` + `/api/cuentas/dashboard` | Permisos de cuentas |
| CRUD | `/api/transacciones` + `/api/transacciones/dashboard` | Permisos de transacciones |
| `GET` | `/api/analista/transacciones`, `/api/analista/casos`, `/api/analista/dashboard` | `RESOLVER_CASO` |

La API responde con el sobre `ApiResponse<T>` (`ok`, `mensaje`, `datos`) y errores consistentes con `status`, `error`, `mensaje` y, en validaciones, `campos`.

---

## Seguridad

- Las contraseñas nunca se devuelven ni se registran en logs; se almacenan con BCrypt.
- Los permisos se resuelven en el backend y se exigen endpoint por endpoint. La interfaz solo oculta lo que el usuario no puede usar.
- Roles y permisos base están protegidos por triggers en la base de datos. El rol `ADMINISTRADOR` no puede eliminarse ni perder permisos.
- El login aplica rate limiting por IP y por combinación IP + usuario.
- Los cambios relevantes quedan auditados con usuario y fecha.
- `backend/.env` está ignorado por Git. No subas secretos ni el archivo de entorno.

---

## Docker y despliegue

El `Dockerfile` empaqueta **nginx + Spring Boot + Angular** en un único contenedor:

```text
navegador
    │  HTTP : PORT
    ▼
nginx (SPA + proxy /api)
    │  localhost:BACKEND_PORT
    ▼
Spring Boot ──► MySQL
```

- `PORT` (por defecto `10000`) es el único puerto publicado.
- `BACKEND_PORT` (por defecto `2003`) es interno y no se expone.
- nginx sirve el SPA y reenvía `/api` al backend, por lo que el navegador usa el mismo origen y no hay CORS en producción.
- `supervisord` arranca nginx y el backend dentro del contenedor.

En Render, `render.yaml` define un solo servicio web a partir del `Dockerfile`. El health check es `GET /api/health` (responde `204`). Los secretos se configuran en el dashboard de Render y nunca se escriben en el repositorio.

Para desplegar:

1. Sube el repositorio a GitHub o GitLab.
2. En Render: **New + → Blueprint** y selecciona el repositorio.
3. Completa las variables marcadas con `sync: false`.
4. Abre la URL del servicio al terminar el despliegue.

> En el plan gratuito el servicio se suspende tras 15 minutos de inactividad y tarda alrededor de un minuto en reactivarse.
