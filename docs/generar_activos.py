"""Genera los diagramas y wireframes usados en la documentacion del Sistema Bancario."""
from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
IMG = BASE / "img"
IMG.mkdir(parents=True, exist_ok=True)

NAVY = (11, 37, 69)
NAVY_2 = (23, 58, 102)
TEAL = (16, 168, 158)
TEAL_DARK = (11, 128, 121)
GOLD = (212, 160, 23)
BG = (246, 248, 252)
WHITE = (255, 255, 255)
INK = (31, 41, 55)
MUTED = (100, 116, 139)
LINE = (203, 213, 225)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
AMBER = (217, 119, 6)
BLUE = (37, 99, 235)

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def canvas(w: int, h: int, color=BG) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (w, h), color)
    return im, ImageDraw.Draw(im)


def text(draw, xy, value, size=24, color=INK, bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def wrap(draw, value: str, fnt, max_width: int) -> list[str]:
    words = value.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def rounded(draw, box, radius=22, fill=WHITE, outline=LINE, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def box(draw, box, title, body="", fill=WHITE, outline=LINE, title_color=NAVY,
        body_color=INK, title_size=26, body_size=20, pad=24, radius=20, center=False):
    rounded(draw, box, radius=radius, fill=fill, outline=outline, width=2)
    x1, y1, x2, y2 = box
    y = y1 + pad
    if center:
        text(draw, ((x1 + x2) / 2, y), title, title_size, title_color, True, anchor="ma")
        y += title_size + 10
    else:
        text(draw, (x1 + pad, y), title, title_size, title_color, True)
        y += title_size + 10
    if body:
        for raw in body.split("\n"):
            for line in wrap(draw, raw, font(body_size), x2 - x1 - 2 * pad):
                text(draw, (x1 + pad, y), line, body_size, body_color)
                y += body_size + 8
    return y


def arrow(draw, start, end, color=TEAL_DARK, width=4, label=None, label_size=17, offset=(0, -16)):
    draw.line([start, end], fill=color, width=width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 14
    p1 = (end[0] - size * math.cos(ang - 0.45), end[1] - size * math.sin(ang - 0.45))
    p2 = (end[0] - size * math.cos(ang + 0.45), end[1] - size * math.sin(ang + 0.45))
    draw.polygon([end, p1, p2], fill=color)
    if label:
        mid = ((start[0] + end[0]) / 2 + offset[0], (start[1] + end[1]) / 2 + offset[1])
        tw = draw.textlength(label, font=font(label_size, True))
        draw.rounded_rectangle((mid[0] - tw / 2 - 8, mid[1] - 12, mid[0] + tw / 2 + 8, mid[1] + 12),
                               radius=8, fill=BG)
        text(draw, mid, label, label_size, color, True, anchor="mm")


def diamond(draw, center, w, h, label, fill=(255, 247, 224), outline=GOLD, size=20):
    x, y = center
    pts = [(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)]
    draw.polygon(pts, fill=fill, outline=outline, width=3)
    lines = wrap(draw, label, font(size, True), int(w * 0.72))
    total = len(lines) * (size + 4)
    for i, line in enumerate(lines):
        text(draw, (x, y - total / 2 + i * (size + 4) + size / 2), line, size, NAVY, True, anchor="mm")


def draw_check(draw, center, color=TEAL, size=9, width=3):
    x, y = center
    draw.line((x - size, y, x - size / 3, y + size * 0.7), fill=color, width=width)
    draw.line((x - size / 3, y + size * 0.7, x + size, y - size * 0.8), fill=color, width=width)


def pill(draw, xy, label, fill=TEAL, color=WHITE, size=18):
    x, y = xy
    tw = draw.textlength(label, font=font(size, True))
    draw.rounded_rectangle((x, y, x + tw + 32, y + size + 16), radius=(size + 16) // 2, fill=fill)
    text(draw, (x + 16, y + size / 2 + 8), label, size, color, True, anchor="lm")


def save(im, name):
    path = IMG / name
    im.save(path, quality=95)
    print("wrote", path)


# ------------------------------------------------------------------ arquitectura
def architecture():
    im, d = canvas(1700, 980, WHITE)
    d.rectangle((0, 0, 1700, 90), fill=NAVY)
    text(d, (48, 45), "Arquitectura de software — Sistema Bancario", 38, WHITE, True, anchor="lm")
    text(d, (1652, 45), "Vista de despliegue lógico", 20, (196, 214, 235), anchor="rm")

    # Cliente
    rounded(d, (60, 140, 360, 830), radius=26, fill=(239, 246, 255), outline=(191, 219, 254))
    text(d, (210, 185), "Cliente", 28, BLUE, True, anchor="mm")
    box(d, (82, 230, 338, 380), "Navegador web",
        "Angular 22\nStandalone + signals\nZoneless + SCSS", title_size=21, body_size=17)
    box(d, (82, 410, 338, 560), "SPA",
        "Login / registro\nSelector de paneles\n4 paneles por rol\nFormularios y tablas", title_size=21, body_size=17)
    box(d, (82, 590, 338, 750), "Seguridad de sesión",
        "JWT en localStorage\nInterceptor Bearer\nGuards por permiso\nCierre por expiración", title_size=21, body_size=17)

    # Nginx
    rounded(d, (430, 190, 710, 790), radius=26, fill=(236, 253, 245), outline=(167, 243, 208))
    text(d, (570, 232), "nginx", 28, TEAL_DARK, True, anchor="mm")
    box(d, (458, 275, 682, 435), "Contenido estático",
        "Angular compilado\nindex.html + assets\ngzip y caché", title_size=20, body_size=16)
    box(d, (458, 450, 682, 600), "Proxy inverso",
        "Spring Boot\nmismo origen\nX-Forwarded-Proto", title_size=20, body_size=16)
    box(d, (458, 615, 682, 755), "Puerto público",
        "PORT (10000)\nÚnico puerto expuesto\nDocker + Render", title_size=20, body_size=16)

    # Spring
    rounded(d, (780, 130, 1260, 860), radius=26, fill=(254, 252, 232), outline=(253, 224, 71))
    text(d, (1020, 172), "Spring Boot 4.1.2 · Java 21", 27, (133, 100, 4), True, anchor="mm")
    box(d, (808, 210, 1232, 330), "Capa web — Controllers REST",
        "@RestController · DTO · Validation\n@PreAuthorize por endpoint", title_size=21, body_size=16)
    box(d, (808, 345, 1232, 475), "Capa de seguridad",
        "JWT HS256 · BCrypt · rate limiting\nPermisosJwtConverter · AutorizacionCache", title_size=21, body_size=16)
    box(d, (808, 485, 1232, 650), "Capa de negocio — Services",
        "Auth · Usuarios · Roles · Cuentas\nTransacciones · Reglas R1–R4 · Casos\n@Transactional y bloqueo pesimista", title_size=21, body_size=16)
    box(d, (808, 665, 1232, 795), "Capa de persistencia — Repositories",
        "Spring Data JPA · consultas JPQL/SQL\nAuditoría creado_por / actualizado_por", title_size=21, body_size=17)

    # DB
    rounded(d, (1330, 200, 1640, 830), radius=26, fill=(245, 243, 255), outline=(196, 181, 253))
    text(d, (1485, 242), "MySQL 8", 28, (91, 33, 182), True, anchor="mm")
    box(d, (1355, 285, 1615, 430), "Esquema", "10 tablas\n2 vistas de permisos\n6 triggers de protección", title_size=22, body_size=17)
    box(d, (1355, 455, 1615, 625), "Integridad", "FK RESTRICT\nen cuentas y movimientos\nTransacciones ACID", title_size=22, body_size=17)
    box(d, (1355, 650, 1615, 800), "Datos", "Usuarios y permisos\nCuentas y movimientos\nCasos y evaluaciones", title_size=22, body_size=17)

    arrow(d, (360, 470), (430, 470), BLUE, 5, "HTTPS")
    arrow(d, (710, 500), (780, 500), TEAL_DARK, 5, "HTTP interno")
    arrow(d, (1260, 540), (1330, 540), (91, 33, 182), 5, "JDBC")
    arrow(d, (1330, 680), (1260, 680), (91, 33, 182), 4)

    text(d, (60, 890), "El navegador solo habla con nginx; nginx sirve el SPA y reenvía /api al backend. La base de datos nunca se expone.",
         19, MUTED)
    save(im, "arquitectura.png")


# ------------------------------------------------------------------ ER
def entity(d, box_xy, name, fields, header=NAVY):
    x1, y1, x2, y2 = box_xy
    rounded(d, box_xy, radius=16, fill=WHITE, outline=LINE, width=2)
    d.rounded_rectangle((x1, y1, x2, y1 + 48), radius=16, fill=header)
    d.rectangle((x1, y1 + 30, x2, y1 + 48), fill=header)
    text(d, (x1 + 18, y1 + 24), name, 23, WHITE, True, anchor="lm")
    y = y1 + 62
    for field in fields:
        text(d, (x1 + 18, y), field, 18, INK)
        y += 27


def er():
    im, d = canvas(1800, 1360, WHITE)
    d.rectangle((0, 0, 1800, 85), fill=NAVY)
    text(d, (44, 42), "Modelo entidad-relación (lógico)", 36, WHITE, True, anchor="lm")
    text(d, (1756, 42), "10 tablas · 2 vistas · 6 triggers", 19, (196, 214, 235), anchor="rm")

    entity(d, (60, 120, 430, 390), "usuarios", [
        "PK id BIGINT", "usuario VARCHAR(50) UNIQUE", "contrasena VARCHAR(100)",
        "email VARCHAR(100) UNIQUE", "activo BOOLEAN", "timestamps de auditoría"])
    entity(d, (60, 470, 430, 720), "roles", [
        "PK id BIGINT", "nombre VARCHAR(50) UNIQUE", "descripcion VARCHAR(200)",
        "activo BOOLEAN", "timestamps de auditoría"])
    entity(d, (60, 800, 430, 1050), "permisos", [
        "PK id BIGINT", "nombre VARCHAR(50) UNIQUE", "descripcion VARCHAR(200)",
        "activo BOOLEAN", "timestamps de auditoría"])

    entity(d, (710, 120, 1130, 400), "cuentas_bancarias", [
        "PK id BIGINT", "numero_cuenta VARCHAR(30) UNIQUE", "FK usuario_id → usuarios",
        "tipo_cuenta (AHORRO/CORRIENTE/EMPRESARIAL)", "saldo DECIMAL(18,2)", "activo BOOLEAN"])
    entity(d, (710, 480, 1160, 835), "transacciones", [
        "PK id BIGINT", "referencia VARCHAR(50) UNIQUE", "FK cuenta_origen_id → cuentas",
        "FK cuenta_destino_id → cuentas", "tipo_transaccion", "monto DECIMAL(18,2)",
        "estado (PENDIENTE/APROBADA/RECHAZADA)", "saldo_origen_post / saldo_destino_post",
        "creado_por / actualizado_por", "timestamps de auditoría"])
    entity(d, (710, 915, 1100, 1200), "casos", [
        "PK id BIGINT", "numero_caso VARCHAR(50) UNIQUE", "FK transaccion_id → transacciones",
        "cuenta_origen_numero (snapshot)", "cuenta_destino_numero (snapshot)", "estado"])
    entity(d, (1440, 480, 1770, 780), "transaccion_reglas", [
        "PK id BIGINT", "FK transaccion_id → transacciones", "orden TINYINT",
        "regla (R1/R2/R3/R4/SALDO)", "aprobada BOOLEAN", "detalle VARCHAR(255)"])

    # relaciones principales
    arrow(d, (430, 255), (710, 255), MUTED, 3)
    text(d, (540, 232), "1", 18, MUTED, True)
    text(d, (675, 232), "N", 18, MUTED, True)
    arrow(d, (245, 390), (245, 470), MUTED, 3)
    d.rounded_rectangle((150, 408, 340, 452), radius=10, fill=(236, 253, 245), outline=TEAL_DARK, width=2)
    text(d, (245, 430), "usuarios_roles", 15, TEAL_DARK, True, anchor="mm")
    text(d, (260, 400), "N:M", 15, TEAL_DARK, True)
    arrow(d, (245, 720), (245, 800), MUTED, 3)
    d.rounded_rectangle((150, 738, 340, 782), radius=10, fill=(236, 253, 245), outline=TEAL_DARK, width=2)
    text(d, (245, 760), "roles_permisos", 15, TEAL_DARK, True, anchor="mm")
    text(d, (260, 730), "N:M", 15, TEAL_DARK, True)
    arrow(d, (920, 400), (920, 480), MUTED, 3)
    text(d, (940, 440), "1..N", 16, MUTED, True)
    arrow(d, (920, 835), (920, 915), MUTED, 3)
    text(d, (940, 870), "1..N", 16, MUTED, True)
    arrow(d, (1160, 620), (1440, 620), MUTED, 3)
    text(d, (1260, 595), "1..N", 16, MUTED, True)

    d.rounded_rectangle((60, 1210, 1130, 1340), radius=14, fill=(255, 247, 224), outline=GOLD, width=2)
    text(d, (85, 1235), "Nota de lectura", 17, (133, 100, 4), True)
    text(d, (85, 1265), "usuarios_roles y roles_permisos materializan el RBAC; usuarios_permisos guarda overrides grant/deny por usuario.", 16, INK)
    text(d, (85, 1298), "La vista v_permisos_finales aplica deny-wins y alimenta el menú y los guards del frontend.", 16, INK)
    save(im, "modelo-er.png")


# ------------------------------------------------------------------ clases
def class_box(d, xy, name, attrs, methods, fill=WHITE, header=NAVY):
    x1, y1, x2, y2 = xy
    rounded(d, xy, radius=12, fill=fill, outline=LINE, width=2)
    d.rounded_rectangle((x1, y1, x2, y1 + 42), radius=12, fill=header)
    d.rectangle((x1, y1 + 24, x2, y1 + 42), fill=header)
    text(d, (x1 + 12, y1 + 21), name, 19, WHITE, True, anchor="lm")
    y = y1 + 54
    for a in attrs:
        text(d, (x1 + 12, y), a, 15, INK)
        y += 21
    d.line([(x1, y), (x2, y)], fill=LINE, width=1)
    y += 10
    for m in methods:
        text(d, (x1 + 12, y), m, 15, MUTED)
        y += 21


def classes():
    im, d = canvas(1750, 1050, WHITE)
    d.rectangle((0, 0, 1750, 85), fill=NAVY)
    text(d, (44, 42), "Diagrama de clases — dominio y capas", 36, WHITE, True, anchor="lm")

    # capa web
    rounded(d, (40, 110, 1710, 270), radius=20, fill=(239, 246, 255), outline=(191, 219, 254))
    text(d, (65, 140), "Capa web (controllers)", 20, BLUE, True)
    for i, n in enumerate(["AuthController", "UsuarioController", "RolController", "CuentaController", "TransaccionController", "AnalistaController"]):
        x = 70 + i * 272
        box(d, (x, 175, x + 245, 245), n, "@RestController\n@PreAuthorize", title_size=18, body_size=14, pad=12, center=True)

    # capa servicio
    rounded(d, (40, 300, 1710, 560), radius=20, fill=(236, 253, 245), outline=(167, 243, 208))
    text(d, (65, 330), "Capa de negocio (services)", 20, TEAL_DARK, True)
    for i, n in enumerate(["AuthService", "UsuarioService", "RolService", "CuentaService", "TransaccionService", "ReglasService", "AnalistaService"]):
        x = 60 + i * 238
        box(d, (x, 365, x + 220, 535), n, "Mono<ApiResponse>\n@Transactional\nvalidaciones\nauditoría", title_size=18, body_size=14, pad=12, center=True)

    # dominio
    rounded(d, (40, 590, 1710, 820), radius=20, fill=(254, 252, 232), outline=(253, 224, 71))
    text(d, (65, 620), "Modelo de dominio (JPA entities)", 20, (133, 100, 4), True)
    class_box(d, (60, 650, 300, 805), "Usuario", ["id, usuario", "contrasena, email", "activo"], ["getActivo()", "setContrasena()"], header=(133, 100, 4))
    class_box(d, (320, 650, 560, 805), "Rol", ["id, nombre", "descripcion", "activo"], ["getNombre()"], header=(133, 100, 4))
    class_box(d, (580, 650, 820, 805), "Permiso", ["id, nombre", "descripcion", "activo"], ["getNombre()"], header=(133, 100, 4))
    class_box(d, (840, 650, 1090, 805), "CuentaBancaria", ["numeroCuenta", "tipoCuenta, saldo", "usuario, activo"], ["aplicarMonto()"], header=(133, 100, 4))
    class_box(d, (1110, 650, 1390, 805), "Transaccion", ["referencia, tipo", "monto, estado", "cuentaOrigen/Destino"], ["getEstado()"], header=(133, 100, 4))
    class_box(d, (1410, 650, 1670, 805), "Caso / Regla", ["numeroCaso", "transaccion", "regla, aprobada"], ["getDetalle()"], header=(133, 100, 4))

    # persistencia
    rounded(d, (40, 850, 1710, 1010), radius=20, fill=(245, 243, 255), outline=(196, 181, 253))
    text(d, (65, 880), "Capa de persistencia (Spring Data JPA)", 20, (91, 33, 182), True)
    for i, n in enumerate(["UsuarioRepository", "RolRepository", "PermisoRepository", "CuentaBancariaRepository", "TransaccionRepository", "CasoRepository"]):
        x = 65 + i * 273
        box(d, (x, 915, x + 248, 985), n, "findBy… · save()\nconsultas JPQL", title_size=17, body_size=14, pad=10, center=True, outline=(196, 181, 253))

    for y1, y2 in [(270, 300), (560, 590), (820, 850)]:
        for x in (180, 520, 860, 1200, 1500):
            arrow(d, (x, y1), (x, y2), LINE, 2)
    save(im, "clases.png")


# ------------------------------------------------------------------ casos de uso
def stick(d, x, y, label, color=NAVY):
    d.ellipse((x - 18, y - 70, x + 18, y - 34), outline=color, width=3)
    d.line((x, y - 34, x, y + 10), fill=color, width=3)
    d.line((x - 30, y - 14, x + 30, y - 14), fill=color, width=3)
    d.line((x, y + 10, x - 24, y + 55), fill=color, width=3)
    d.line((x, y + 10, x + 24, y + 55), fill=color, width=3)
    text(d, (x, y + 80), label, 20, color, True, anchor="ma")


def usecase(d, cx, cy, label, w=265, h=78, fill=(224, 242, 254), outline=(147, 197, 253)):
    d.ellipse((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=fill, outline=outline, width=2)
    lines = wrap(d, label, font(17, True), int(w * 0.78))
    total = len(lines) * 21
    for i, line in enumerate(lines):
        text(d, (cx, cy - total / 2 + i * 21 + 10), line, 17, NAVY, True, anchor="mm")


def usecases():
    im, d = canvas(1800, 1160, WHITE)
    d.rectangle((0, 0, 1800, 85), fill=NAVY)
    text(d, (44, 42), "Diagrama de casos de uso", 36, WHITE, True, anchor="lm")
    rounded(d, (390, 115, 1750, 1110), radius=24, fill=(248, 250, 252), outline=(148, 163, 184))
    text(d, (1070, 145), "Sistema Bancario", 24, MUTED, True, anchor="mm")
    text(d, (650, 180), "Acceso y operación", 15, BLUE, True, anchor="mm")
    text(d, (1280, 180), "Supervisión", 15, GREEN, True, anchor="mm")
    text(d, (1470, 180), "Gobierno", 15, AMBER, True, anchor="mm")

    stick(d, 175, 320, "USUARIO", BLUE)
    stick(d, 175, 800, "ANALISTA", GREEN)
    stick(d, 175, 1025, "ADMINISTRADOR", AMBER)

    # usuario
    usuario = [("Iniciar sesión", 240), ("Registrarse", 325), ("Gestionar sus cuentas", 410),
               ("Registrar depósito / retiro", 495), ("Registrar transferencia / pago", 580),
               ("Consultar sus movimientos", 665)]
    for label, y in usuario:
        usecase(d, 650, y, label, w=330, fill=(224, 242, 254), outline=(147, 197, 253))
        d.line((220, 320, 485, y), fill=(148, 163, 184), width=1)

    # analista
    analista = [("Revisar todas las transacciones", 760), ("Resolver casos (aprobar / rechazar)", 855),
                ("Editar cuentas", 950)]
    for label, y in analista:
        usecase(d, 1280, y, label, w=360, fill=(220, 252, 231), outline=(134, 239, 172))
        d.line((220, 800, 1100, y), fill=(148, 163, 184), width=1)

    usecase(d, 1470, 1020, "Gestionar usuarios, roles y permisos", w=330, fill=(254, 249, 195), outline=(253, 224, 71))
    d.line((220, 1025, 1305, 1020), fill=(148, 163, 184), width=1)

    text(d, (60, 1135), "Los casos se agrupan por rol; el backend vuelve a validar cada permiso con @PreAuthorize.", 18, MUTED)
    save(im, "casos-uso.png")


# ------------------------------------------------------------------ procesos
def process_login():
    im, d = canvas(1500, 1050, WHITE)
    d.rectangle((0, 0, 1500, 85), fill=NAVY)
    text(d, (44, 42), "Proceso de inicio de sesión", 36, WHITE, True, anchor="lm")
    cx = 750
    box(d, (580, 120, 920, 185), "Inicio", "El usuario abre /login", fill=(219, 234, 254), outline=(147, 197, 253), center=True, title_size=22)
    arrow(d, (cx, 185), (cx, 235))
    box(d, (560, 235, 940, 305), "Ingresar credenciales", "usuario/email + contraseña", center=True, title_size=21)
    arrow(d, (cx, 305), (cx, 350))
    diamond(d, (cx, 405), 400, 110, "¿Rate limit excedido?")
    arrow(d, (cx, 460), (cx, 510), label="No")
    box(d, (560, 510, 940, 580), "Buscar usuario", "findByUsuarioOrEmail", center=True, title_size=21)
    arrow(d, (cx, 580), (cx, 625))
    diamond(d, (cx, 680), 400, 110, "¿Existe y BCrypt coincide?")
    arrow(d, (cx, 735), (cx, 790), label="Sí")
    diamond(d, (cx, 845), 400, 110, "¿Cuenta activa?")
    arrow(d, (cx, 900), (cx, 955), label="Sí")
    box(d, (545, 955, 955, 1025), "Cargar permisos + emitir JWT", "respuesta 200 con token y menú", fill=(220, 252, 231), outline=(134, 239, 172), center=True, title_size=20)

    # errores
    arrow(d, (950, 405), (1160, 405), RED, 3)
    box(d, (1160, 355, 1420, 455), "429", "Demasiados intentos\nRetry-After", fill=(254, 226, 226), outline=(252, 165, 165), title_size=20, body_size=16, center=True)
    arrow(d, (950, 680), (1160, 680), RED, 3)
    box(d, (1160, 630, 1420, 735), "401", "Credenciales inválidas\n(mismo mensaje)", fill=(254, 226, 226), outline=(252, 165, 165), title_size=20, body_size=16, center=True)
    arrow(d, (950, 845), (1160, 845), RED, 3)
    box(d, (1160, 795, 1420, 895), "401", "Cuenta desactivada", fill=(254, 226, 226), outline=(252, 165, 165), title_size=20, body_size=16, center=True)

    # lateral
    box(d, (70, 380, 430, 520), "BCrypt siempre", "Si el usuario no existe se compara\ncontra un hash ficticio para no\nfiltrar la existencia por tiempo.", title_size=20, body_size=16, fill=(255, 247, 224), outline=GOLD)
    box(d, (70, 650, 430, 790), "Permisos por petición", "El JWT solo lleva identidad;\nla vista v_permisos_finales\nresuelve el menú y los guards.", title_size=20, body_size=16, fill=(255, 247, 224), outline=GOLD)
    save(im, "proceso-login.png")


def process_transfer():
    im, d = canvas(1700, 1090, WHITE)
    d.rectangle((0, 0, 1700, 85), fill=NAVY)
    text(d, (44, 42), "Proceso de registro y resolución de un movimiento", 34, WHITE, True, anchor="lm")
    cx = 850
    box(d, (650, 115, 1050, 185), "Inicio", "El usuario registra un movimiento", center=True, title_size=21, fill=(219, 234, 254), outline=(147, 197, 253))
    arrow(d, (cx, 185), (cx, 230))
    diamond(d, (cx, 295), 470, 120, "¿Depósito o retiro?")

    # Rama izquierda: depósito / retiro
    arrow(d, (615, 295), (430, 295), label="Sí", offset=(0, -18))
    box(d, (170, 355, 670, 450), "Confirmar contraseña", "BCrypt contra el usuario actual", center=True, title_size=20)
    arrow(d, (420, 450), (420, 500))
    box(d, (170, 500, 670, 600), "Aprobar y aplicar saldo", "sin motor de reglas; estado APROBADA", fill=(220, 252, 231), outline=(134, 239, 172), center=True, title_size=20)

    # Rama derecha: transferencia / pago
    arrow(d, (1085, 295), (1270, 295), label="No", offset=(0, -18))
    box(d, (1080, 355, 1520, 450), "Transferencia o pago", "cuenta origen + destino + monto", center=True, title_size=20)
    arrow(d, (1300, 450), (1300, 500))
    box(d, (1080, 500, 1520, 600), "Evaluar R1–R4 + saldo", "historial, recurrencia, monto, vaciado", center=True, title_size=20)
    arrow(d, (1300, 600), (1300, 650))
    diamond(d, (1300, 715), 430, 120, "¿Cumple todas las reglas?")
    arrow(d, (1300, 775), (1300, 820), label="Sí")
    box(d, (1080, 820, 1520, 920), "APROBADA", "aplicar saldos y guardar evaluación", fill=(220, 252, 231), outline=(134, 239, 172), center=True, title_size=20)
    arrow(d, (1085, 715), (1020, 715), label="No", offset=(0, -18))

    # Caso pendiente y resolución del analista
    box(d, (620, 660, 1020, 760), "PENDIENTE + caso", "se abre un caso ABIERTO para el analista", fill=(254, 249, 195), outline=(253, 224, 71), center=True, title_size=20)
    arrow(d, (820, 760), (820, 810))
    box(d, (620, 810, 1020, 905), "Analista resuelve", "aprobar / rechazar / editar", center=True, title_size=20)
    arrow(d, (1020, 862), (1080, 862), label="aprobar")
    arrow(d, (820, 905), (820, 960), RED, 3, "rechazar", offset=(85, 0))
    box(d, (620, 960, 1020, 1045), "Rechazar o eliminar", "revertir saldos si estaba aprobada", fill=(254, 226, 226), outline=(252, 165, 165), center=True, title_size=19)

    text(d, (70, 1070), "Toda la operación ocurre en una transacción SQL con bloqueo pesimista de las cuentas implicadas (SELECT ... FOR UPDATE).",
         18, MUTED)
    save(im, "proceso-movimiento.png")


# ------------------------------------------------------------------ secuencias
def sequence_login():
    im, d = canvas(1700, 980, WHITE)
    d.rectangle((0, 0, 1700, 85), fill=NAVY)
    text(d, (44, 42), "Secuencia — inicio de sesión", 36, WHITE, True, anchor="lm")
    actors = [("Usuario", 90), ("Angular SPA", 350), ("AuthController", 620), ("AuthService", 900), ("Repositorios / BD", 1200), ("JwtService", 1510)]
    for name, x in actors:
        rounded(d, (x - 105, 115, x + 105, 175), radius=12, fill=NAVY_2, outline=NAVY_2)
        text(d, (x, 145), name, 17, WHITE, True, anchor="mm")
        d.line((x, 175, x, 900), fill=(148, 163, 184), width=2)

    steps = [
        (90, 350, 235, "1  POST /auth/login", BLUE),
        (350, 620, 300, "2  credenciales", BLUE),
        (620, 900, 365, "3  login(request)", BLUE),
        (900, 1200, 430, "4  buscar usuario + BCrypt", TEAL_DARK),
        (1200, 900, 495, "5  usuario / null", MUTED),
        (900, 1200, 560, "6  cargar permisos efectivos", TEAL_DARK),
        (1200, 900, 625, "7  lista de permisos", MUTED),
        (900, 1510, 690, "8  generar JWT", TEAL_DARK),
        (1510, 900, 755, "9  token + expiración", MUTED),
        (900, 620, 815, "10  AuthResponse", MUTED),
        (620, 350, 865, "11  200 OK + token", GREEN),
    ]
    for x1, x2, y, label, color in steps:
        arrow(d, (x1, y), (x2, y), color, 3, label, 15, offset=(0, -15))
    text(d, (90, 930), "Rate limit antes del paso 2 (429). Credenciales inválidas o cuenta inactiva terminan en 401 sin revelar cuál falló.",
         17, MUTED)
    save(im, "secuencia-login.png")


def sequence_transfer():
    im, d = canvas(1800, 1080, WHITE)
    d.rectangle((0, 0, 1800, 85), fill=NAVY)
    text(d, (44, 42), "Secuencia — transferencia y resolución de caso", 34, WHITE, True, anchor="lm")
    actors = [("Usuario", 85), ("Angular", 320), ("Transaccion\nController", 570), ("Transaccion\nService", 840), ("Reglas\nService", 1110), ("Cuenta /\nTransacción Repo", 1390), ("Caso\nRepo", 1660)]
    for name, x in actors:
        rounded(d, (x - 100, 110, x + 100, 180), radius=12, fill=NAVY_2, outline=NAVY_2)
        text(d, (x, 145), name, 16, WHITE, True, anchor="mm")
        d.line((x, 180, x, 980), fill=(148, 163, 184), width=2)

    def step(x1, x2, y, label, color=BLUE):
        arrow(d, (x1, y), (x2, y), color, 3, label, 14, offset=(0, -14))

    step(85, 320, 230, "1  POST /transacciones", BLUE)
    step(320, 570, 280, "2  request + JWT", BLUE)
    step(570, 840, 330, "3  crear(request)", BLUE)
    step(840, 1390, 380, "4  cargar y bloquear cuentas (FOR UPDATE)", TEAL_DARK)
    step(840, 1110, 440, "5  evaluar R1–R4 + saldo", TEAL_DARK)
    d.line((1110, 440, 1110, 510), fill=TEAL_DARK, width=3)
    d.line((1110, 510, 840, 510), fill=TEAL_DARK, width=3)
    arrow(d, (1110, 510), (840, 510), TEAL_DARK, 3)
    text(d, (975, 490), "6  resultado por regla", 14, TEAL_DARK, True, anchor="mm")
    step(840, 1390, 570, "7  guardar transacción + saldos", TEAL_DARK)
    step(840, 1660, 630, "8  abrir caso si PENDIENTE", AMBER)
    step(840, 570, 690, "9  respuesta", MUTED)
    step(570, 320, 735, "10  estado + evaluación", MUTED)
    step(320, 85, 780, "11  mensaje al usuario", GREEN)

    # analista
    d.line((80, 835, 1720, 835), fill=LINE, width=2)
    text(d, (90, 865), "Resolución posterior (analista con RESOLVER_CASO)", 18, NAVY, True)
    step(85, 320, 905, "12  PUT /transacciones/{id}", AMBER)
    step(320, 570, 940, "13  estado APROBADA / RECHAZADA", AMBER)
    text(d, (90, 1010), "El servicio revierte el efecto anterior si cambia una transacción ya aprobada y sincroniza el caso (RESUELTO / RECHAZADO).",
         15, MUTED)
    save(im, "secuencia-transferencia.png")


# ------------------------------------------------------------------ WBS
def wbs():
    im, d = canvas(1700, 950, WHITE)
    d.rectangle((0, 0, 1700, 85), fill=NAVY)
    text(d, (44, 42), "Estructura de desglose del trabajo (WBS)", 36, WHITE, True, anchor="lm")
    root = (710, 110, 990, 185)
    box(d, root, "Sistema Bancario", "1.0", fill=NAVY, outline=NAVY, title_color=WHITE, body_color=(196, 214, 235), center=True, title_size=23, body_size=18)

    groups = [
        ("1. Planificación", 215, ["1.1 Problema y objetivos", "1.2 Canvas y charter", "1.3 WBS y cronograma", "1.4 Requerimientos"]),
        ("2. Diseño", 615, ["2.1 Arquitectura", "2.2 Modelo ER", "2.3 Clases y DTO", "2.4 Wireframes"]),
        ("3. Desarrollo", 1015, ["3.1 Sprint 1: acceso", "3.2 Sprint 2: banco", "3.3 RBAC y permisos", "3.4 Motor de reglas"]),
        ("4. Pruebas y despliegue", 1415, ["4.1 Pruebas funcionales", "4.2 Manuales", "4.3 Docker / Render", "4.4 Conclusiones"]),
    ]
    d.line((850, 185, 850, 225), fill=MUTED, width=2)
    for title, x, children in groups:
        box(d, (x - 160, 270, x + 160, 345), title, "", fill=(224, 242, 254), outline=(147, 197, 253), center=True, title_size=19)
        d.line((x, 225, 850, 225), fill=MUTED, width=2)
        d.line((x, 225, x, 270), fill=MUTED, width=2)
        d.line((x, 345, x - 180, 345), fill=MUTED, width=2)
        d.line((x - 180, 345, x - 180, 390 + 3 * 125 + 35), fill=MUTED, width=2)
        for i, child in enumerate(children):
            y = 390 + i * 125
            box(d, (x - 155, y, x + 155, y + 70), child, "", title_size=17, body_size=14, center=True, pad=10)
            d.line((x - 180, y + 35, x - 155, y + 35), fill=MUTED, width=2)
    save(im, "wbs.png")


# ------------------------------------------------------------------ wireframes
def browser_frame(d, title="Sistema Bancario", url="localhost:4200"):
    d.rectangle((0, 0, 1440, 900), fill=(235, 239, 245))
    d.rounded_rectangle((45, 35, 1395, 865), radius=16, fill=WHITE, outline=(203, 213, 225), width=2)
    d.rectangle((45, 35, 1395, 78), fill=(226, 232, 240))
    for i, c in enumerate([(248, 113, 113), (251, 191, 36), (74, 222, 128)]):
        d.ellipse((65 + i * 22, 49, 77 + i * 22, 61), fill=c)
    d.rounded_rectangle((160, 47, 1280, 72), radius=12, fill=WHITE)
    text(d, (720, 59), url, 14, MUTED, anchor="mm")
    text(d, (1350, 835), "WIREFRAME", 13, (148, 163, 184), True, anchor="rm")


def sidebar(d, active="Dashboard", panel="Administración"):
    d.rectangle((45, 78, 285, 865), fill=NAVY)
    d.ellipse((68, 100, 112, 144), fill=TEAL)
    text(d, (90, 122), "SB", 18, WHITE, True, anchor="mm")
    text(d, (125, 110), panel, 17, WHITE, True)
    text(d, (125, 133), "Ana Torres", 13, (196, 214, 235))
    text(d, (68, 190), "MÓDULOS", 12, (148, 163, 184), True)
    items = ["Dashboard", "Usuarios", "Roles", "Permisos"] if panel == "Administración" else ["Dashboard", "Cuentas", "Movimientos", "Casos"]
    for i, item in enumerate(items):
        y = 215 + i * 52
        if item == active:
            d.rounded_rectangle((63, y, 267, y + 40), radius=9, fill=(30, 64, 105))
            d.rectangle((63, y, 68, y + 40), fill=TEAL)
        text(d, (82, y + 20), item, 15, WHITE if item == active else (203, 213, 225), item == active, anchor="lm")
    d.rounded_rectangle((63, 790, 267, 833), radius=9, outline=(71, 85, 105), width=1)
    text(d, (165, 812), "Cambiar de panel", 14, (203, 213, 225), anchor="mm")


def topbar(d, title="Dashboard"):
    d.rectangle((285, 78, 1395, 150), fill=WHITE)
    d.line((285, 150, 1395, 150), fill=LINE, width=1)
    text(d, (315, 114), f"Panel  /  {title}", 15, MUTED, anchor="lm")
    d.ellipse((1170, 100, 1204, 134), fill=(226, 232, 240))
    text(d, (1187, 117), "AT", 12, NAVY, True, anchor="mm")
    text(d, (1215, 108), "Ana Torres", 13, INK, True)
    text(d, (1215, 124), "ana@banco.pe", 11, MUTED)
    d.rounded_rectangle((1325, 100, 1360, 134), radius=8, outline=LINE)
    text(d, (1342, 117), "⏻", 14, MUTED, anchor="mm")


def kpi(d, x, y, label, value, delta="", color=TEAL):
    d.rounded_rectangle((x, y, x + 250, y + 105), radius=12, fill=WHITE, outline=LINE)
    text(d, (x + 18, y + 20), label.upper(), 11, MUTED, True)
    text(d, (x + 18, y + 48), value, 28, NAVY, True)
    if delta:
        text(d, (x + 18, y + 82), delta, 12, color, True)


def table(d, x, y, width, headers, rows, widths=None, row_h=34, header_color=NAVY):
    widths = widths or [width / len(headers)] * len(headers)
    d.rounded_rectangle((x, y, x + width, y + 38), radius=8, fill=header_color)
    cx = x + 12
    for h, w in zip(headers, widths):
        text(d, (cx, y + 19), h, 12, WHITE, True, anchor="lm")
        cx += w
    ry = y + 38
    for i, row in enumerate(rows):
        fill = WHITE if i % 2 == 0 else (248, 250, 252)
        d.rectangle((x, ry, x + width, ry + row_h), fill=fill)
        cx = x + 12
        for value, w in zip(row, widths):
            text(d, (cx, ry + row_h / 2), value, 12, INK, anchor="lm")
            cx += w
        d.line((x, ry + row_h, x + width, ry + row_h), fill=(241, 245, 249), width=1)
        ry += row_h
    d.rounded_rectangle((x, y, x + width, ry), radius=8, outline=LINE, width=1)


def wire_login():
    im, d = canvas(1440, 900, (235, 239, 245))
    browser_frame(d, url="localhost:4200/login")
    d.rectangle((45, 78, 700, 865), fill=NAVY)
    d.ellipse((90, 130, 138, 178), fill=TEAL)
    text(d, (114, 154), "SB", 20, WHITE, True, anchor="mm")
    text(d, (90, 250), "Sistema Bancario", 42, WHITE, True)
    text(d, (90, 330), "Bienvenido al sistema bancario, donde la", 18, (203, 213, 225))
    text(d, (90, 358), "seguridad y la eficiencia se unen para", 18, (203, 213, 225))
    text(d, (90, 386), "brindarte una experiencia confiable.", 18, (203, 213, 225))
    for i, item in enumerate(["Depósitos y retiros seguros", "Transferencias internas", "Informes detallados"]):
        d.ellipse((92, 480 + i * 44, 112, 500 + i * 44), outline=TEAL, width=2)
        draw_check(d, (102, 490 + i * 44), TEAL, 5, 2)
        text(d, (125, 490 + i * 44), item, 16, (226, 232, 240), anchor="lm")
    d.rounded_rectangle((770, 175, 1250, 770), radius=18, fill=WHITE, outline=LINE)
    text(d, (805, 225), "Iniciar sesión", 30, NAVY, True)
    text(d, (805, 265), "Ingresa tus credenciales para continuar.", 15, MUTED)
    text(d, (805, 330), "Usuario", 13, INK, True)
    d.rounded_rectangle((805, 355, 1215, 405), radius=8, fill=(248, 250, 252), outline=LINE)
    text(d, (825, 380), "tu.usuario", 15, (148, 163, 184), anchor="lm")
    text(d, (805, 440), "Contraseña", 13, INK, True)
    d.rounded_rectangle((805, 465, 1215, 515), radius=8, fill=(248, 250, 252), outline=LINE)
    text(d, (825, 490), "••••••••", 15, (148, 163, 184), anchor="lm")
    d.rounded_rectangle((805, 570, 1215, 625), radius=8, fill=TEAL)
    text(d, (1010, 597), "Ingresar  →", 16, WHITE, True, anchor="mm")
    text(d, (1010, 675), "¿No tienes cuenta?  Regístrate", 14, MUTED, anchor="mm")
    save(im, "wire-login.png")


def wire_launcher():
    im, d = canvas(1440, 900, (235, 239, 245))
    browser_frame(d, url="localhost:4200/")
    d.rectangle((45, 78, 1395, 145), fill=WHITE)
    d.line((45, 145, 1395, 145), fill=LINE)
    d.ellipse((70, 95, 108, 133), fill=TEAL)
    text(d, (89, 114), "SB", 14, WHITE, True, anchor="mm")
    text(d, (120, 114), "Bienvenido Ana", 16, NAVY, True, anchor="lm")
    text(d, (1175, 114), "Ana Torres  ·  ana@banco.pe", 14, MUTED, anchor="rm")
    d.rounded_rectangle((1290, 96, 1360, 132), radius=8, outline=LINE)
    text(d, (1325, 114), "Salir", 13, MUTED, anchor="mm")
    text(d, (75, 210), "PANEL DE ACCESO", 12, TEAL_DARK, True)
    text(d, (75, 245), "¿A dónde quieres ir?", 38, NAVY, True)
    text(d, (75, 300), "Tienes acceso a 4 de 4 módulos disponibles.", 16, MUTED)
    cards = [("Administración", "Identidades, accesos y trazabilidad.", "Disponible", NAVY),
             ("Cuentas", "Apertura y gestión de cuentas.", "Disponible", TEAL_DARK),
             ("Transacciones", "Registro y seguimiento de movimientos.", "Disponible", BLUE),
             ("Analista", "Supervisión y resolución de casos.", "Disponible", GREEN)]
    for i, (name, desc, status, color) in enumerate(cards):
        x = 75 + (i % 2) * 650
        y = 370 + (i // 2) * 235
        d.rounded_rectangle((x, y, x + 610, y + 205), radius=14, fill=WHITE, outline=LINE)
        d.ellipse((x + 25, y + 25, x + 67, y + 67), fill=color)
        text(d, (x + 46, y + 46), name[0], 18, WHITE, True, anchor="mm")
        text(d, (x + 85, y + 38), name, 21, NAVY, True)
        text(d, (x + 25, y + 100), desc, 14, MUTED)
        d.rounded_rectangle((x + 25, y + 145, x + 155, y + 175), radius=15, fill=(220, 252, 231))
        text(d, (x + 90, y + 160), status, 12, GREEN, True, anchor="mm")
        text(d, (x + 565, y + 160), "→", 26, color, True, anchor="mm")
    save(im, "wire-launcher.png")


def wire_admin():
    im, d = canvas(1440, 900, (235, 239, 245))
    browser_frame(d, url="localhost:4200/admin/dashboard")
    sidebar(d, "Dashboard", "Administración")
    topbar(d, "Dashboard")
    text(d, (315, 190), "Dashboard administrativo", 27, NAVY, True)
    text(d, (315, 225), "Resumen operativo del control de accesos.", 14, MUTED)
    kpi(d, 315, 270, "Usuarios", "4", "+1 este mes")
    kpi(d, 585, 270, "Roles activos", "3", "ADMIN · ANALISTA · USUARIO", BLUE)
    kpi(d, 855, 270, "Permisos", "29", "catálogo base protegido", GOLD)
    kpi(d, 1125, 270, "Cuentas", "22", "7 ahorro · 8 corriente", TEAL)
    d.rounded_rectangle((315, 410, 830, 700), radius=12, fill=WHITE, outline=LINE)
    text(d, (340, 440), "Altas por mes", 17, NAVY, True)
    bars = [32, 55, 44, 70, 62, 88, 74, 95, 80, 108, 96, 120]
    for i, h in enumerate(bars):
        x = 355 + i * 38
        d.rounded_rectangle((x, 660 - h, x + 22, 660), radius=5, fill=TEAL if i % 2 else NAVY)
    d.line((340, 670, 810, 670), fill=LINE)
    d.rounded_rectangle((855, 410, 1360, 700), radius=12, fill=WHITE, outline=LINE)
    text(d, (880, 440), "Distribución de roles", 17, NAVY, True)
    d.pieslice((910, 470, 1130, 690), 0, 330, fill=TEAL)
    d.pieslice((910, 470, 1130, 690), 330, 355, fill=GOLD)
    d.pieslice((910, 470, 1130, 690), 355, 360, fill=NAVY)
    d.ellipse((975, 535, 1065, 625), fill=WHITE)
    text(d, (1020, 580), "4", 24, NAVY, True, anchor="mm")
    for i, (label, color) in enumerate([("USUARIO", TEAL), ("ANALISTA", GOLD), ("ADMIN", NAVY)]):
        d.rectangle((1160, 490 + i * 34, 1180, 510 + i * 34), fill=color)
        text(d, (1192, 500 + i * 34), label, 13, INK, anchor="lm")
    text(d, (315, 710), "Actividad reciente", 17, NAVY, True)
    table(d, 315, 735, 1045, ["Usuario", "Acción", "Módulo", "Fecha"], [
        ["@hehiachi", "Asignó rol ANALISTA", "Usuarios", "Hoy 10:42"],
        ["ana.torres", "Creó cuenta EMPRESARIAL", "Cuentas", "Hoy 09:18"],
        ["carlos.r", "Registró transferencia", "Transacciones", "Ayer 18:05"],
    ], widths=[240, 330, 250, 225], row_h=25)
    save(im, "wire-admin.png")


def wire_cuentas():
    im, d = canvas(1440, 900, (235, 239, 245))
    browser_frame(d, url="localhost:4200/cuentas/cuentas")
    sidebar(d, "Cuentas", "Cuentas")
    topbar(d, "Cuentas")
    text(d, (315, 190), "Cuentas bancarias", 27, NAVY, True)
    text(d, (315, 225), "Apertura, edición y consulta de cuentas.", 14, MUTED)
    d.rounded_rectangle((1150, 190, 1250, 230), radius=8, fill=TEAL)
    text(d, (1200, 210), "+ Nueva cuenta", 12, WHITE, True, anchor="mm")
    d.rounded_rectangle((315, 260, 1360, 315), radius=10, fill=WHITE, outline=LINE)
    text(d, (335, 288), "Buscar por número o titular…", 13, (148, 163, 184), anchor="lm")
    for i, (label, val) in enumerate([("Total", "22"), ("Activas", "19"), ("Saldo total", "S/ 184,320")]):
        d.rounded_rectangle((315 + i * 350, 340, 640 + i * 350, 420), radius=12, fill=WHITE, outline=LINE)
        text(d, (335 + i * 350, 360), label, 12, MUTED, True)
        text(d, (335 + i * 350, 385), val, 24, NAVY, True)
    table(d, 315, 455, 1045, ["Número", "Titular", "Tipo", "Saldo", "Estado"], [
        ["001-1234567890", "Ana Torres", "AHORRO", "S/ 12,450.00", "Activa"],
        ["002-9876543210", "Carlos Ruiz", "CORRIENTE", "S/ 8,320.50", "Activa"],
        ["003-4567891230", "Empresa SAC", "EMPRESARIAL", "S/ 45,900.00", "Activa"],
        ["004-7891234560", "Lucía Pérez", "AHORRO", "S/ 2,100.00", "Inactiva"],
        ["005-3216549870", "Jorge Díaz", "CORRIENTE", "S/ 15,780.25", "Activa"],
        ["006-6549873210", "María Solís", "AHORRO", "S/ 6,430.10", "Activa"],
    ], widths=[240, 260, 190, 190, 165], row_h=43)
    text(d, (315, 790), "El botón de estado solo aparece con CAMBIAR_ESTADO_CUENTAS; una cuenta con movimientos no se elimina.",
         13, MUTED)
    save(im, "wire-cuentas.png")


def wire_movimientos():
    im, d = canvas(1440, 900, (235, 239, 245))
    browser_frame(d, url="localhost:4200/transacciones/movimientos")
    sidebar(d, "Movimientos", "Cuentas")
    topbar(d, "Movimientos")
    text(d, (315, 190), "Movimientos", 27, NAVY, True)
    text(d, (315, 225), "Altas y resolución de transacciones.", 14, MUTED)
    d.rounded_rectangle((1100, 190, 1250, 230), radius=8, fill=TEAL)
    text(d, (1175, 210), "+ Nuevo movimiento", 12, WHITE, True, anchor="mm")
    for i, label in enumerate(["Todos", "Pendientes", "Aprobadas", "Rechazadas"]):
        d.rounded_rectangle((315 + i * 125, 260, 425 + i * 125, 300), radius=16, fill=TEAL if i == 0 else WHITE, outline=LINE)
        text(d, (370 + i * 125, 280), label, 12, WHITE if i == 0 else MUTED, True, anchor="mm")
    table(d, 315, 335, 1045, ["Referencia", "Tipo", "Origen → Destino", "Monto", "Estado", "Fecha"], [
        ["TX-20261025-000842", "TRANSFERENCIA", "001-1234 → 002-9876", "S/ 1,250.00", "PENDIENTE", "25/10 10:42"],
        ["TX-20261025-000841", "DEPÓSITO", "— → 003-4567", "S/ 500.00", "APROBADA", "25/10 10:18"],
        ["TX-20261025-000840", "PAGO", "002-9876 → 005-3216", "S/ 320.00", "APROBADA", "25/10 09:55"],
        ["TX-20261024-000839", "RETIRO", "001-1234 → —", "S/ 200.00", "APROBADA", "24/10 18:30"],
        ["TX-20261024-000838", "TRANSFERENCIA", "004-7891 → 006-6549", "S/ 4,800.00", "RECHAZADA", "24/10 17:12"],
        ["TX-20261024-000837", "TRANSFERENCIA", "003-4567 → 001-1234", "S/ 2,100.00", "PENDIENTE", "24/10 16:40"],
    ], widths=[205, 145, 235, 145, 150, 165], row_h=44)
    d.rounded_rectangle((315, 680, 1360, 825), radius=12, fill=(255, 247, 224), outline=GOLD)
    text(d, (340, 705), "Evaluación del motor de reglas", 17, (133, 100, 4), True)
    for i, (code, label, ok, passed) in enumerate([
        ("R1", "Recurrencia hacia el destino", "12 de 48 (25 %)", True),
        ("R2", "Recurrencia del tipo", "9 de 48 (19 %)", False),
        ("R3", "Monto vs promedio x 2.5", "S/ 1,250 < S/ 2,400", True),
        ("R4", "Intento de vaciado", "diferencia > 1 %", True),
    ]):
        x = 340 + (i % 2) * 505
        y = 745 + (i // 2) * 35
        text(d, (x, y), code, 14, GREEN if passed else RED, True)
        text(d, (x + 40, y), f"{label}: {ok}  [{'OK' if passed else 'NO'}]", 12, INK)
    save(im, "wire-movimientos.png")


def wire_casos():
    im, d = canvas(1440, 900, (235, 239, 245))
    browser_frame(d, url="localhost:4200/analista/casos")
    sidebar(d, "Casos", "Analista")
    topbar(d, "Casos")
    text(d, (315, 190), "Bandeja de casos", 27, NAVY, True)
    text(d, (315, 225), "Transacciones pendientes de revisión y resolución.", 14, MUTED)
    for i, (label, val, color) in enumerate([("Abiertos", "5", AMBER), ("En revisión", "0", BLUE), ("Resueltos", "1", GREEN)]):
        d.rounded_rectangle((315 + i * 350, 265, 640 + i * 350, 345), radius=12, fill=WHITE, outline=LINE)
        text(d, (335 + i * 350, 285), label, 12, MUTED, True)
        text(d, (335 + i * 350, 310), val, 25, color, True)
    table(d, 315, 385, 1045, ["Caso", "Transacción", "Cuentas", "Monto", "Estado", "Acción"], [
        ["CASO-20261025-000042", "TX-…-000842", "001-1234 → 002-9876", "S/ 1,250.00", "ABIERTO", "Revisar"],
        ["CASO-20261025-000041", "TX-…-000837", "003-4567 → 001-1234", "S/ 2,100.00", "ABIERTO", "Revisar"],
        ["CASO-20261024-000040", "TX-…-000831", "004-7891 → 006-6549", "S/ 4,800.00", "ABIERTO", "Revisar"],
        ["CASO-20261024-000039", "TX-…-000828", "002-9876 → 005-3216", "S/ 900.00", "ABIERTO", "Revisar"],
        ["CASO-20261024-000038", "TX-…-000825", "001-1234 → 003-4567", "S/ 3,200.00", "ABIERTO", "Revisar"],
        ["CASO-20261023-000037", "TX-…-000819", "006-6549 → 002-9876", "S/ 750.00", "RESUELTO", "Ver"],
    ], widths=[235, 160, 220, 145, 130, 110], row_h=44)
    d.rounded_rectangle((315, 730, 1360, 820), radius=12, fill=WHITE, outline=LINE)
    text(d, (340, 755), "Detalle del caso seleccionado", 15, NAVY, True)
    text(d, (340, 785), "R2 incumplida: solo 19 % de los movimientos del origen son del mismo tipo. R1, R3 y R4 aprobadas; saldo suficiente.",
         13, MUTED)
    save(im, "wire-casos.png")


# ------------------------------------------------------------------ portada
def cover():
    im, d = canvas(1800, 760, NAVY)
    for y in range(760):
        t = y / 760
        c = (int(11 + 20 * t), int(37 + 60 * t), int(69 + 80 * t))
        d.line((0, y, 1800, y), fill=c)
    d.ellipse((1300, -260, 2050, 490), fill=(19, 80, 120))
    d.ellipse((1430, 380, 1980, 930), fill=(14, 62, 96))
    d.ellipse((110, 90, 190, 170), fill=TEAL)
    text(d, (150, 130), "SB", 28, WHITE, True, anchor="mm")
    text(d, (215, 110), "SISTEMA BANCARIO", 24, (148, 233, 226), True)
    text(d, (110, 235), "Documentación del proyecto", 58, WHITE, True)
    text(d, (112, 320), "Planificación, diseño, desarrollo, pruebas y despliegue", 28, (203, 213, 225))
    d.line((112, 390, 700, 390), fill=TEAL, width=5)
    text(d, (112, 440), "Aplicación web para la gestión de cuentas,", 22, (226, 232, 240))
    text(d, (112, 475), "movimientos y resolución de casos bancarios.", 22, (226, 232, 240))
    text(d, (112, 640), "Versión 1.0  ·  Octubre 2026", 18, (148, 163, 184))
    text(d, (112, 675), "Angular 22 · Spring Boot 4.1.2 · Java 21 · MySQL 8", 18, (148, 233, 226))
    save(im, "portada.png")


def cover_ppt():
    im, d = canvas(1600, 900, NAVY)
    for y in range(900):
        t = y / 900
        c = (int(8 + 18 * t), int(30 + 55 * t), int(58 + 78 * t))
        d.line((0, y, 1600, y), fill=c)
    d.ellipse((1120, -280, 1900, 500), fill=(17, 76, 114))
    d.ellipse((1280, 360, 1850, 930), fill=(13, 60, 94))
    d.ellipse((95, 80, 175, 160), fill=TEAL)
    text(d, (135, 120), "SB", 26, WHITE, True, anchor="mm")
    text(d, (205, 100), "SISTEMA BANCARIO", 22, (148, 233, 226), True)
    text(d, (95, 245), "DOCUMENTACIÓN DEL PROYECTO", 20, (148, 233, 226), True)
    text(d, (93, 300), "Sistema Bancario", 78, WHITE, True)
    text(d, (95, 420), "Planificación · Diseño · Desarrollo", 32, (226, 232, 240))
    text(d, (95, 470), "Pruebas, despliegue y mantenimiento", 32, (226, 232, 240))
    d.line((95, 560, 720, 560), fill=TEAL, width=5)
    text(d, (95, 610), "Aplicación web para la gestión de cuentas,", 23, (203, 213, 225))
    text(d, (95, 648), "movimientos y resolución de casos bancarios.", 23, (203, 213, 225))
    text(d, (95, 790), "Octubre 2026  ·  Angular 22  ·  Spring Boot 4.1.2  ·  Java 21  ·  MySQL 8", 19, (148, 163, 184))
    save(im, "ppt-cover.png")


if __name__ == "__main__":
    cover_ppt()
    architecture()
    er()
    classes()
    usecases()
    process_login()
    process_transfer()
    sequence_login()
    sequence_transfer()
    wbs()
    wire_login()
    wire_launcher()
    wire_admin()
    wire_cuentas()
    wire_movimientos()
    wire_casos()
    cover()
