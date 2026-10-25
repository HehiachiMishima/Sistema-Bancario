"""Genera la presentación PowerPoint del Sistema Bancario."""
from __future__ import annotations

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

BASE = Path(__file__).resolve().parent
IMG = BASE / "img"
OUT = BASE / "Sistema_Bancario_Presentacion.pptx"

NAVY = RGBColor(0x0B, 0x25, 0x45)
NAVY_2 = RGBColor(0x17, 0x3A, 0x66)
TEAL = RGBColor(0x10, 0xA8, 0x9E)
TEAL_DARK = RGBColor(0x0B, 0x80, 0x79)
GOLD = RGBColor(0xD4, 0xA0, 0x17)
BG = RGBColor(0xF6, 0xF8, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x64, 0x74, 0x8B)
LINE = RGBColor(0xCB, 0xD5, 0xE1)
GREEN = RGBColor(0x16, 0xA3, 0x4A)
RED = RGBColor(0xDC, 0x26, 0x26)
AMBER = RGBColor(0xD9, 0x77, 0x06)
BLUE = RGBColor(0x25, 0x63, 0xEB)
SOFT_BLUE = RGBColor(0xE0, 0xF2, 0xFE)
SOFT_GREEN = RGBColor(0xDC, 0xFC, 0xE7)
SOFT_GOLD = RGBColor(0xFF, 0xF7, 0xE0)
SOFT_RED = RGBColor(0xFE, 0xE2, 0xE2)

FONT = "Arial"
W = 13.333
H = 7.5
M = 0.58

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
SLIDE_NO = 0


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def new_slide(bg=BG, footer=True, logo=True):
    global SLIDE_NO
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = bg
    SLIDE_NO += 1
    if footer:
        footer_bar(slide)
    if logo:
        logo_mark(slide)
    return slide


def footer_bar(slide):
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(7.02), Inches(W - 2 * M), Pt(0.8))
    line.fill.solid()
    line.fill.fore_color.rgb = LINE
    line.line.fill.background()
    text(slide, "Sistema Bancario  ·  Documentación del proyecto  ·  Octubre 2026",
         M, 7.1, 8.4, 0.25, 8, MUTED)
    text(slide, f"{SLIDE_NO:02d}", W - M - 0.6, 7.08, 0.6, 0.25, 8, MUTED, align=PP_ALIGN.RIGHT)


def logo_mark(slide):
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(W - 1.05), Inches(0.38), Inches(0.38), Inches(0.38))
    circle.fill.solid()
    circle.fill.fore_color.rgb = TEAL
    circle.line.fill.background()
    tf = circle.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "SB"
    r.font.name = FONT
    r.font.size = Pt(9)
    r.font.bold = True
    r.font.color.rgb = WHITE


def text(slide, value, x, y, w, h, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, italic=False, line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = value
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return box


def rich(slide, runs, x, y, w, h, size=14, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for value, bold, col in runs:
        r = p.add_run()
        r.text = value
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = col or color
    return box


def slide_title(slide, kicker, title, subtitle=None):
    text(slide, kicker.upper(), M, 0.42, 9.5, 0.25, 9.5, TEAL_DARK, True)
    text(slide, title, M, 0.68, 11.6, 0.55, 28, NAVY, True, line_spacing=0.95)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(1.27), Inches(1.0), Pt(3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    if subtitle:
        text(slide, subtitle, M, 1.38, 12.0, 0.35, 12.5, MUTED)


def card(slide, x, y, w, h, fill=WHITE, line=LINE, radius=0.06, line_width=0.9):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.adjustments[0] = radius
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(line_width)
    shape.shadow.inherit = False
    return shape


def chip(slide, x, y, w, h, value, fill=SOFT_GREEN, color=GREEN, size=9, bold=True):
    shape = card(slide, x, y, w, h, fill=fill, line=None, radius=0.5)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = value
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


def pill(slide, x, y, w, h, value, fill=NAVY, color=WHITE, size=10):
    chip(slide, x, y, w, h, value, fill=fill, color=color, size=size)


def bullets(slide, items, x, y, w, h, size=14, color=INK, bullet_color=TEAL, gap=6, line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = "•  "
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.bold = True
        r.font.color.rgb = bullet_color
        r2 = p.add_run()
        r2.text = item
        r2.font.name = FONT
        r2.font.size = Pt(size)
        r2.font.color.rgb = color
    return box


def fit_image(slide, path, x, y, w, h):
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    nw, nh = iw * scale, ih * scale
    slide.shapes.add_picture(str(path), Inches(x + (w - nw) / 2), Inches(y + (h - nh) / 2),
                             Inches(nw), Inches(nh))


def notes(slide, value):
    slide.notes_slide.notes_text_frame.text = value


def table(slide, headers, rows, x, y, w, h, col_widths=None, font_size=10, header_size=10,
          first_col_bold=False):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h))
    table_obj = shape.table
    table_obj.first_row = True
    table_obj.horz_banding = False
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            table_obj.columns[i].width = Emu(int(Inches(w) * cw / total))
    for j, header in enumerate(headers):
        cell = table_obj.cell(0, j)
        cell.text = ""
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.margin_top = cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = header
        r.font.name = FONT
        r.font.size = Pt(header_size)
        r.font.bold = True
        r.font.color.rgb = WHITE
    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            cell = table_obj.cell(i, j)
            cell.text = ""
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 == 1 else RGBColor(0xF8, 0xFA, 0xFC)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(value)
            r.font.name = FONT
            r.font.size = Pt(font_size)
            r.font.bold = first_col_bold and j == 0
            r.font.color.rgb = INK
    return table_obj


# ------------------------------------------------------------------ 1 portada
def s_cover():
    slide = new_slide(bg=NAVY, footer=False, logo=False)
    slide.shapes.add_picture(str(IMG / "ppt-cover.png"), 0, 0, Inches(W), Inches(H))
    notes(slide, "Presentación del Sistema Bancario: planificación, diseño, desarrollo, pruebas y despliegue. "
                 "El proyecto es demostrativo y no procesa dinero real.")


# ------------------------------------------------------------------ 2 agenda
def s_agenda():
    slide = new_slide()
    slide_title(slide, "Recorrido", "Agenda de la presentación")
    items = [
        ("01", "Planificación y análisis", "Problema, objetivos, Canvas, alcance y requerimientos."),
        ("02", "Diseño", "Arquitectura, modelo entidad-relación y diagrama de clases."),
        ("03", "Desarrollo", "Sprint 1 de autenticación y Sprint 2 de cuentas y movimientos."),
        ("04", "Pruebas y despliegue", "Verificación, manuales, Docker/Render y mantenimiento."),
        ("05", "Cierre", "Conclusiones, recomendaciones y siguientes pasos."),
    ]
    y = 1.65
    for n, title, desc in items:
        card(slide, M, y, 0.72, 0.72, fill=NAVY, line=None, radius=0.18)
        text(slide, n, M, y + 0.16, 0.72, 0.35, 16, WHITE, True, PP_ALIGN.CENTER)
        text(slide, title, M + 0.95, y + 0.04, 4.2, 0.3, 17, NAVY, True)
        text(slide, desc, M + 0.95, y + 0.34, 11.0, 0.28, 11.5, MUTED)
        y += 0.94
    notes(slide, "La presentación sigue la estructura del documento: planificación, diseño, dos sprints, "
                 "pruebas/despliegue y conclusiones. Duración objetivo: 15–20 minutos.")


# ------------------------------------------------------------------ 3 problema
def s_problem():
    slide = new_slide()
    slide_title(slide, "Capítulo 1", "El problema: operar sin un sistema único",
                "La información, la autorización y las decisiones viven en lugares distintos.")
    cards = [
        ("Información dispersa", "Hojas de cálculo y registros manuales duplican cuentas y movimientos.", "01", SOFT_BLUE, BLUE),
        ("Poca trazabilidad", "No queda claro quién creó, modificó o aprobó cada operación.", "02", SOFT_GOLD, AMBER),
        ("Decisiones sin criterio", "No hay una regla uniforme para aprobar o derivar una transferencia.", "03", SOFT_RED, RED),
    ]
    for i, (title, desc, num, fill, color) in enumerate(cards):
        x = M + i * 4.08
        card(slide, x, 1.85, 3.85, 2.35, fill=WHITE)
        card(slide, x + 0.2, 2.05, 0.5, 0.5, fill=fill, line=None, radius=0.5)
        text(slide, num, x + 0.2, 2.15, 0.5, 0.25, 10, color, True, PP_ALIGN.CENTER)
        text(slide, title, x + 0.2, 2.65, 3.4, 0.3, 15, NAVY, True)
        text(slide, desc, x + 0.2, 3.05, 3.4, 0.9, 10.5, MUTED, line_spacing=1.05)
    card(slide, M, 4.55, 12.15, 1.75, fill=NAVY, line=None)
    text(slide, "¿Cómo centralizar cuentas y movimientos con seguridad,\ntrazabilidad y reglas explícitas?",
         M + 0.4, 4.72, 11.3, 0.78, 17, WHITE, True, line_spacing=1.0)
    text(slide, "La respuesta: una SPA + API REST, RBAC, JWT, motor R1–R4 y una bandeja de casos.",
         M + 0.4, 5.52, 11.3, 0.3, 11.5, RGBColor(0xC4, 0xD6, 0xEB))
    chip(slide, M + 0.4, 5.92, 1.2, 0.28, "Demostrativo", fill=RGBColor(0x1E, 0x40, 0x69), color=RGBColor(0xA7, 0xF3, 0xD0), size=8)
    notes(slide, "El problema no es solo 'hacer una app': es unificar identidad, operación y decisión. "
                 "El sistema es demostrativo: simula saldos, no procesa dinero real.")


# ------------------------------------------------------------------ 4 objetivos
def s_objectives():
    slide = new_slide()
    slide_title(slide, "Capítulo 1", "Objetivos del proyecto")
    card(slide, M, 1.75, 5.15, 3.75, fill=SOFT_BLUE, line=None)
    text(slide, "OBJETIVO GENERAL", M + 0.28, 1.98, 4.5, 0.25, 10, BLUE, True)
    text(slide, "Gestionar cuentas y movimientos con autenticación, permisos, reglas de aprobación y "
                "trazabilidad, manteniendo la consistencia de saldos.",
         M + 0.28, 2.35, 4.55, 2.6, 17, NAVY, True, line_spacing=1.08)
    text(slide, "Cuatro paneles, un solo shell y una API stateless.", M + 0.28, 5.0, 4.5, 0.3, 10.5, MUTED)
    text(slide, "OBJETIVOS ESPECÍFICOS", 6.15, 1.75, 5.5, 0.25, 10, TEAL_DARK, True)
    bullets(slide, [
        "Acceso seguro con JWT, BCrypt y límite de intentos.",
        "RBAC con roles, permisos y overrides por usuario.",
        "Cuentas de ahorro, corriente y empresarial.",
        "Depósitos, retiros, transferencias y pagos.",
        "Motor R1–R4 y bandeja de casos para el analista.",
        "Dashboards, auditoría y despliegue en un contenedor.",
    ], 6.15, 2.1, 6.4, 3.5, 13.5, gap=7)
    metrics = [("4", "paneles"), ("29", "permisos"), ("10", "tablas"), ("60", "endpoints")]
    for i, (value, label) in enumerate(metrics):
        x = M + i * 3.08
        card(slide, x, 5.75, 2.8, 0.85, fill=WHITE)
        text(slide, value, x + 0.16, 5.85, 0.7, 0.4, 21, TEAL_DARK, True)
        text(slide, label, x + 0.9, 5.95, 1.7, 0.25, 11, MUTED)
    notes(slide, "El objetivo general se descompone en acceso, gobierno, operación, reglas, casos y "
                 "despliegue. Las métricas provienen del repositorio verificado.")


# ------------------------------------------------------------------ 5 canvas
def s_canvas():
    slide = new_slide()
    slide_title(slide, "Capítulo 1", "Modelo Canvas", "Un proyecto académico con operación simulada.")
    blocks = [
        ("Socios clave", "Equipo, docente, hosting y MySQL local."),
        ("Actividades clave", "Análisis, sprints, pruebas y despliegue."),
        ("Propuesta de valor", "Cuentas + reglas + trazabilidad en un solo lugar."),
        ("Relación con clientes", "Autoservicio, analista y administrador."),
        ("Segmentos", "Usuarios, analistas y administradores."),
        ("Recursos clave", "Angular, Spring Boot, MySQL y Docker."),
        ("Canales", "SPA web responsive y API REST."),
        ("Costes", "Tiempo de desarrollo y hosting gratuito."),
        ("Ingresos", "No aplica: proyecto académico."),
    ]
    for i, (title, desc) in enumerate(blocks):
        col = i % 3
        row = i // 3
        x = M + col * 4.08
        y = 1.7 + row * 1.67
        card(slide, x, y, 3.85, 1.45, fill=WHITE)
        text(slide, title.upper(), x + 0.18, y + 0.14, 3.5, 0.22, 8, TEAL_DARK, True)
        text(slide, desc, x + 0.18, y + 0.46, 3.5, 0.75, 11.5, NAVY, line_spacing=1.02)
    text(slide, "El bloque de ingresos se deja explícito como «no aplica» para no presentar el prototipo como un producto comercial.",
         M, 6.75, 12.2, 0.25, 9.5, MUTED, italic=True)
    notes(slide, "Canvas adaptado a un proyecto académico. La propuesta de valor es la integración de "
                 "cuentas, movimientos, reglas y casos con trazabilidad.")


# ------------------------------------------------------------------ 6 alcance
def s_scope():
    slide = new_slide()
    slide_title(slide, "Capítulo 1", "Alcance y límites", "Lo que el sistema resuelve hoy y lo que queda fuera.")
    card(slide, M, 1.7, 5.95, 4.55, fill=SOFT_GREEN, line=None)
    text(slide, "INCLUYE", M + 0.3, 1.95, 3.0, 0.25, 10.5, GREEN, True)
    bullets(slide, [
        "Login, registro, sesión JWT y cambio de contraseña.",
        "Usuarios, roles, permisos y overrides.",
        "Cuentas de ahorro, corriente y empresarial.",
        "Depósitos, retiros, transferencias y pagos.",
        "Motor R1–R4, casos y resolución del analista.",
        "Dashboards, auditoría, Docker y Render.",
    ], M + 0.3, 2.35, 5.3, 3.5, 12.5, color=NAVY, bullet_color=GREEN, gap=7)
    card(slide, 6.78, 1.7, 5.95, 4.55, fill=SOFT_RED, line=None)
    text(slide, "NO INCLUYE", 7.08, 1.95, 3.0, 0.25, 10.5, RED, True)
    bullets(slide, [
        "Dinero real ni conexión con una red bancaria.",
        "MFA, recuperación por correo o revocación de tokens.",
        "Alta disponibilidad, réplica o backups automáticos.",
        "Suite E2E automatizada en el repositorio.",
        "Cumplimiento regulatorio, firma digital o multi-moneda.",
        "Cobros, tarjetas, préstamos o inversiones.",
    ], 7.08, 2.35, 5.3, 3.5, 12.5, color=NAVY, bullet_color=RED, gap=7)
    card(slide, M, 6.45, 12.15, 0.42, fill=WHITE, line=LINE)
    text(slide, "El alcance es suficiente para demostrar arquitectura, seguridad, modelado y verificación; no para operar un banco.",
         M + 0.22, 6.53, 11.7, 0.25, 9.5, MUTED, italic=True)
    notes(slide, "Importante ser explícito: es un prototipo académico. Los límites se documentan y se "
                 "convierten en recomendaciones al final.")


# ------------------------------------------------------------------ 7 requerimientos
def s_requirements():
    slide = new_slide()
    slide_title(slide, "Capítulo 1", "Requerimientos que guiaron el diseño")
    cols = [
        ("ACCESO Y SEGURIDAD", BLUE, SOFT_BLUE, [
            "Login y autorregistro con rol USUARIO.",
            "Sesión JWT y cierre por expiración.",
            "Contraseñas con BCrypt y rate limiting.",
            "Permisos validados en cada endpoint.",
        ]),
        ("OPERACIÓN BANCARIA", TEAL_DARK, SOFT_GREEN, [
            "Cuentas: ahorro, corriente y empresarial.",
            "Depósitos y retiros con contraseña.",
            "Transferencias y pagos con reglas.",
            "Casos, aprobación, rechazo y reversión.",
        ]),
        ("GOBIERNO Y TRAZABILIDAD", AMBER, SOFT_GOLD, [
            "CRUD de usuarios, roles y permisos.",
            "Asignaciones y overrides grant/deny.",
            "Auditoría de creador y última modificación.",
            "Dashboards y filtros por estado y tipo.",
        ]),
    ]
    for i, (title, color, fill, items) in enumerate(cols):
        x = M + i * 4.08
        card(slide, x, 1.75, 3.85, 3.95, fill=WHITE)
        card(slide, x, 1.75, 3.85, 0.12, fill=color, line=None, radius=0.2)
        text(slide, title, x + 0.2, 2.0, 3.4, 0.25, 9.5, color, True)
        bullets(slide, items, x + 0.2, 2.4, 3.45, 3.0, 11, gap=7)
    chips = ["JWT HS256", "BCrypt", "ACID", "Responsive", "Auditoría", "Docker"]
    x = M
    for c in chips:
        chip(slide, x, 6.05, 1.45, 0.35, c, fill=NAVY, color=WHITE, size=8.5)
        x += 1.55
    text(slide, "24 requerimientos funcionales y 12 no funcionales documentados en el Word.",
         M, 6.6, 11.8, 0.25, 9.5, MUTED, italic=True)
    notes(slide, "Los requerimientos se agruparon en tres bloques. Los RNF cubren seguridad, integridad, "
                 "rendimiento, usabilidad, mantenibilidad y portabilidad.")


# ------------------------------------------------------------------ 8 arquitectura
def s_architecture():
    slide = new_slide()
    slide_title(slide, "Capítulo 2", "Arquitectura de software", "SPA + API REST + MySQL en un solo contenedor.")
    fit_image(slide, IMG / "arquitectura.png", M, 1.68, 9.25, 4.75)
    card(slide, 10.0, 1.68, 2.75, 1.4, fill=SOFT_BLUE, line=None)
    text(slide, "CLIENTE", 10.18, 1.82, 2.2, 0.22, 8, BLUE, True)
    text(slide, "Angular 22\nStandalone + signals", 10.18, 2.08, 2.3, 0.72, 10.5, NAVY, True)
    card(slide, 10.0, 3.22, 2.75, 1.4, fill=SOFT_GREEN, line=None)
    text(slide, "API", 10.18, 3.36, 2.2, 0.22, 8, TEAL_DARK, True)
    text(slide, "Spring Boot 4.1.2\nJava 21 + JPA", 10.18, 3.62, 2.3, 0.72, 10.5, NAVY, True)
    card(slide, 10.0, 4.76, 2.75, 1.4, fill=SOFT_GOLD, line=None)
    text(slide, "DATOS", 10.18, 4.9, 2.2, 0.22, 8, AMBER, True)
    text(slide, "MySQL 8\n10 tablas · 2 vistas", 10.18, 5.16, 2.3, 0.72, 10.5, NAVY, True)
    chip(slide, 10.0, 6.42, 2.75, 0.35, "nginx · 1 puerto público", fill=NAVY, color=WHITE, size=8.5)
    notes(slide, "El navegador habla con nginx; nginx sirve el SPA y proxifica /api. El backend es "
                 "stateless y accede a MySQL. Docker y Render simplifican el despliegue.")


# ------------------------------------------------------------------ 9 datos
def s_data():
    slide = new_slide()
    slide_title(slide, "Capítulo 2", "Modelo de datos", "Identidad, operación y aseguramiento en 10 tablas.")
    fit_image(slide, IMG / "modelo-er.png", M, 1.68, 7.55, 5.0)
    card(slide, 8.4, 1.72, 4.35, 1.0, fill=SOFT_BLUE, line=None)
    text(slide, "RBAC + overrides", 8.58, 1.85, 3.9, 0.25, 12, NAVY, True)
    text(slide, "roles, permisos, usuarios_roles, roles_permisos y usuarios_permisos.", 8.58, 2.15, 3.95, 0.42, 9.5, MUTED)
    card(slide, 8.4, 2.87, 4.35, 1.0, fill=SOFT_GREEN, line=None)
    text(slide, "Operación", 8.58, 3.0, 3.9, 0.25, 12, NAVY, True)
    text(slide, "cuentas_bancarias, transacciones y casos con snapshot de cuentas.", 8.58, 3.3, 3.95, 0.42, 9.5, MUTED)
    card(slide, 8.4, 4.02, 4.35, 1.0, fill=SOFT_GOLD, line=None)
    text(slide, "Aseguramiento", 8.58, 4.15, 3.9, 0.25, 12, NAVY, True)
    text(slide, "transaccion_reglas guarda R1–R4 y saldo con su detalle.", 8.58, 4.45, 3.95, 0.42, 9.5, MUTED)
    chips = [("10", "tablas"), ("2", "vistas"), ("6", "triggers")]
    for i, (v, l) in enumerate(chips):
        card(slide, 8.4 + i * 1.45, 5.25, 1.28, 0.85, fill=WHITE)
        text(slide, v, 8.52 + i * 1.45, 5.33, 0.5, 0.35, 18, TEAL_DARK, True)
        text(slide, l, 8.52 + i * 1.45, 5.7, 1.0, 0.22, 8.5, MUTED)
    text(slide, "FK RESTRICT en cuentas y movimientos para preservar el historial contable.",
         8.4, 6.35, 4.3, 0.35, 9, MUTED, italic=True)
    notes(slide, "El modelo separa identidad de operación. Las tablas asociativas implementan RBAC y "
                 "overrides; las vistas aplican deny-wins. Las FK RESTRICT protegen el historial.")


# ------------------------------------------------------------------ 10 roles
def s_roles():
    slide = new_slide()
    slide_title(slide, "Capítulo 2", "Tres roles, un modelo de permisos",
                "El menú se filtra, pero el backend vuelve a validar cada operación.")
    roles = [
        ("USUARIO", "Opera sus propias cuentas", ["Deposita y retira", "Transfiere y paga", "Consulta sus movimientos"], SOFT_BLUE, BLUE),
        ("ANALISTA", "Supervisa y resuelve", ["Ve todos los movimientos", "Resuelve casos", "Edita cuentas"], SOFT_GREEN, GREEN),
        ("ADMINISTRADOR", "Gobierna accesos", ["Gestiona usuarios y roles", "Asigna permisos y overrides", "Acceso total"], SOFT_GOLD, AMBER),
    ]
    for i, (name, subtitle, items, fill, color) in enumerate(roles):
        x = M + i * 4.08
        card(slide, x, 1.65, 3.85, 3.15, fill=WHITE)
        card(slide, x, 1.65, 3.85, 0.12, fill=color, line=None, radius=0.2)
        text(slide, name, x + 0.22, 1.92, 3.4, 0.3, 15, NAVY, True)
        text(slide, subtitle, x + 0.22, 2.26, 3.4, 0.25, 10, color, True)
        bullets(slide, items, x + 0.22, 2.62, 3.4, 1.9, 10.5, gap=4)
    # flujo
    steps = [("Rol", "ADMIN / ANALISTA / USUARIO"), ("Permisos", "plantilla RBAC"), ("Override", "grant / deny"), ("Deny-wins", "v_permisos_finales")]
    for i, (title, sub) in enumerate(steps):
        x = M + i * 3.1
        card(slide, x, 5.2, 2.75, 0.95, fill=NAVY if i == 3 else WHITE, line=NAVY if i == 3 else LINE)
        text(slide, title, x + 0.16, 5.32, 2.4, 0.27, 11.5, WHITE if i == 3 else NAVY, True)
        text(slide, sub, x + 0.16, 5.62, 2.45, 0.25, 8.5, RGBColor(0xC4, 0xD6, 0xEB) if i == 3 else MUTED)
        if i < 3:
            text(slide, "→", x + 2.78, 5.45, 0.28, 0.3, 18, TEAL_DARK, True, PP_ALIGN.CENTER)
    text(slide, "El rol ADMINISTRADOR y los permisos base están protegidos por triggers: no se eliminan ni se modifican.",
         M, 6.45, 12.0, 0.3, 9.5, MUTED, italic=True)
    notes(slide, "El modelo es RBAC puro con overrides. La vista final aplica MIN(otorgado), de modo que un deny "
                 "individual gana. El frontend usa los permisos para el menú; el backend los exige con @PreAuthorize.")


# ------------------------------------------------------------------ 11 sprint 1
def s_sprint1():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 1", "Autenticación de usuarios",
                "Tres semanas para habilitar el acceso seguro y la base del gobierno de identidades.")
    # timeline
    milestones = [("Semana 1", "Login + JWT"), ("Semana 2", "RBAC + permisos"), ("Semana 3", "Usuarios, roles y pruebas")]
    for i, (week, desc) in enumerate(milestones):
        y = 1.8 + i * 1.25
        card(slide, M, y, 0.95, 0.95, fill=TEAL if i == 0 else NAVY, line=None, radius=0.2)
        text(slide, str(i + 1), M, y + 0.3, 0.95, 0.3, 16, WHITE, True, PP_ALIGN.CENTER)
        text(slide, week, M + 1.15, y + 0.08, 2.0, 0.28, 13, NAVY, True)
        text(slide, desc, M + 1.15, y + 0.4, 3.2, 0.3, 10.5, MUTED)
        if i < 2:
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M + 0.46), Inches(y + 0.95), Pt(1.5), Inches(0.3))
            line.fill.solid()
            line.fill.fore_color.rgb = LINE
            line.line.fill.background()
    text(slide, "HISTORIAS PRINCIPALES", 5.25, 1.72, 4.0, 0.25, 9.5, TEAL_DARK, True)
    stories = [
        "HU-01 Iniciar sesión y emitir JWT.",
        "HU-02 Autorregistro con rol USUARIO.",
        "HU-03 Sesión, expiración y cierre.",
        "HU-04 RBAC + overrides deny-wins.",
        "HU-05 Usuarios, roles y permisos.",
        "HU-06 Rate limiting por IP y usuario.",
    ]
    bullets(slide, stories, 5.25, 2.08, 7.2, 3.2, 12.5, gap=7)
    card(slide, 5.25, 5.45, 7.45, 1.1, fill=NAVY, line=None)
    text(slide, "RESULTADO", 5.45, 5.6, 1.4, 0.22, 8, RGBColor(0x94, 0xE8, 0xDF), True)
    text(slide, "JWT HS256  ·  BCrypt  ·  29 permisos  ·  3 roles  ·  menú filtrado", 5.45, 5.9, 6.9, 0.35, 12, WHITE, True)
    for i, c in enumerate(["401 sin token", "403 sin permiso", "200 con sesión"]):
        chip(slide, 5.25 + i * 2.0, 6.65, 1.85, 0.32, c, fill=SOFT_GREEN, color=GREEN, size=8)
    notes(slide, "El Sprint 1 resuelve identidad y autorización. La decisión clave es no guardar permisos en el JWT: "
                 "se resuelven por petición para que un deny o una desactivación tengan efecto inmediato.")


# ------------------------------------------------------------------ 12 login flow
def s_login():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 1", "Flujo de inicio de sesión", "BCrypt siempre; permisos por petición.")
    fit_image(slide, IMG / "proceso-login.png", M, 1.68, 7.55, 4.9)
    steps = [
        ("1", "Rate limit", "Doble cubo: IP y IP + usuario."),
        ("2", "BCrypt", "Hash ficticio si el usuario no existe."),
        ("3", "Estado", "Cuenta activa antes de emitir."),
        ("4", "Permisos", "Se cargan de la vista final."),
        ("5", "JWT", "Identidad + expiración; respuesta 200."),
    ]
    y = 1.8
    for n, title, desc in steps:
        card(slide, 8.45, y, 0.42, 0.42, fill=TEAL, line=None, radius=0.5)
        text(slide, n, 8.45, y + 0.1, 0.42, 0.2, 9, WHITE, True, PP_ALIGN.CENTER)
        text(slide, title, 9.02, y - 0.02, 3.6, 0.25, 12, NAVY, True)
        text(slide, desc, 9.02, y + 0.27, 3.6, 0.3, 9.5, MUTED)
        y += 0.95
    card(slide, 8.45, 6.45, 4.25, 0.42, fill=SOFT_GOLD, line=None)
    text(slide, "401 genérico para no revelar si el usuario existe.", 8.6, 6.53, 4.0, 0.25, 8.5, AMBER, True)
    notes(slide, "El orden importa: rate limit antes de tocar la base; BCrypt siempre; estado de cuenta; permisos; JWT. "
                 "Los errores usan el mismo mensaje para no filtrar la existencia del usuario.")


# ------------------------------------------------------------------ 13 sprint 2
def s_sprint2():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 2", "Cuentas y movimientos",
                "Cuatro semanas para convertir el acceso en operación bancaria.")
    modules = [
        ("Cuentas", "22", "7 ahorro · 8 corriente · 7 empresarial", SOFT_BLUE, BLUE),
        ("Movimientos", "8", "3 aprobados · 5 pendientes", SOFT_GREEN, TEAL_DARK),
        ("Casos", "6", "5 abiertos · 1 resuelto", SOFT_GOLD, AMBER),
        ("Reglas", "16", "evaluaciones R1–R4 persistidas", SOFT_RED, RED),
    ]
    for i, (title, value, sub, fill, color) in enumerate(modules):
        x = M + (i % 2) * 4.1
        y = 1.7 + (i // 2) * 1.55
        card(slide, x, y, 3.85, 1.35, fill=fill, line=None)
        text(slide, title.upper(), x + 0.2, y + 0.14, 2.0, 0.22, 8.5, color, True)
        text(slide, value, x + 0.2, y + 0.4, 0.8, 0.45, 24, NAVY, True)
        text(slide, sub, x + 1.05, y + 0.55, 2.55, 0.4, 9, MUTED)
    text(slide, "QUÉ SE CONSTRUYÓ", 9.0, 1.72, 3.7, 0.25, 9.5, TEAL_DARK, True)
    bullets(slide, [
        "CRUD de cuentas con número automático o personalizado.",
        "Depósitos y retiros con confirmación de contraseña.",
        "Transferencias y pagos con R1–R4 y saldo.",
        "Aplicación y reversión de saldos con bloqueo.",
        "Casos y bandeja del analista.",
        "Dashboards por rol y filtros de movimientos.",
    ], 9.0, 2.08, 3.9, 3.9, 10.5, gap=6)
    card(slide, M, 5.3, 8.1, 0.9, fill=NAVY, line=None)
    text(slide, "Saldos consistentes: SELECT … FOR UPDATE + transacción SQL.", M + 0.22, 5.5, 7.6, 0.4, 13, WHITE, True)
    chip(slide, 9.0, 5.55, 1.85, 0.34, "ACID", fill=SOFT_GREEN, color=GREEN, size=9)
    chip(slide, 11.0, 5.55, 1.85, 0.34, "Reversión", fill=SOFT_GOLD, color=AMBER, size=9)
    notes(slide, "El Sprint 2 añade la operación bancaria. Los números son del entorno de demostración: 22 cuentas, "
                 "8 movimientos, 6 casos y 16 evaluaciones de reglas.")


# ------------------------------------------------------------------ 14 movimientos
def s_movements():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 2", "Cuatro tipos de movimiento",
                "Dos se aprueban al instante; dos pasan por el motor de reglas.")
    types = [
        ("DEPÓSITO", "Inmediato", "Acredita saldo en la cuenta destino. Confirma contraseña.", SOFT_BLUE, BLUE),
        ("RETIRO", "Inmediato", "Debita saldo de la cuenta origen. Confirma contraseña.", SOFT_BLUE, BLUE),
        ("TRANSFERENCIA", "Evaluado", "Origen → destino distinto. R1–R4 + saldo.", SOFT_GREEN, TEAL_DARK),
        ("PAGO", "Evaluado", "Mismo flujo que transferencia, con concepto.", SOFT_GREEN, TEAL_DARK),
    ]
    for i, (title, tag, desc, fill, color) in enumerate(types):
        x = M + i * 3.08
        card(slide, x, 1.7, 2.85, 2.55, fill=WHITE)
        card(slide, x, 1.7, 2.85, 0.1, fill=color, line=None, radius=0.2)
        text(slide, title, x + 0.18, 1.95, 2.5, 0.3, 12, NAVY, True)
        chip(slide, x + 0.18, 2.35, 1.1, 0.28, tag, fill=fill, color=color, size=7.5)
        text(slide, desc, x + 0.18, 2.78, 2.5, 1.2, 9.8, MUTED, line_spacing=1.05)
    # estados
    text(slide, "CICLO DE ESTADOS", M, 4.55, 3.0, 0.25, 9.5, TEAL_DARK, True)
    states = [("PENDIENTE", "Se abre un caso", SOFT_GOLD, AMBER), ("APROBADA", "Saldos aplicados", SOFT_GREEN, GREEN), ("RECHAZADA", "Saldos revertidos", SOFT_RED, RED)]
    for i, (state, desc, fill, color) in enumerate(states):
        x = M + i * 3.2
        card(slide, x, 4.9, 2.95, 0.85, fill=fill, line=None)
        text(slide, state, x + 0.18, 5.02, 2.6, 0.25, 11, color, True)
        text(slide, desc, x + 0.18, 5.32, 2.6, 0.22, 9, MUTED)
        if i < 2:
            text(slide, "→", x + 2.98, 5.12, 0.2, 0.25, 16, MUTED, True, PP_ALIGN.CENTER)
    card(slide, M, 6.1, 12.15, 0.55, fill=NAVY, line=None)
    text(slide, "Transferencia/pago: R1–R4 + saldo → APROBADA automática; cualquier falla → PENDIENTE + caso.",
         M + 0.22, 6.24, 11.6, 0.3, 10.5, WHITE, True)
    notes(slide, "Depósitos y retiros se eximen del motor de reglas porque se confirman con contraseña. "
                 "Transferencias y pagos se evalúan; si falla una regla, quedan pendientes y abren un caso.")


# ------------------------------------------------------------------ 15 reglas
def s_rules():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 2", "Motor de reglas R1–R4",
                "Una aprobación automática debe ser explicable, no una caja negra.")
    rules = [
        ("R1", "Recurrencia hacia el destino", "≥ 20 % de los movimientos históricos del origen van a la misma cuenta.", "12 de 48 = 25 %"),
        ("R2", "Recurrencia del tipo", "≥ 20 % de los movimientos históricos son del mismo tipo.", "9 de 48 = 19 %"),
        ("R3", "Monto vs promedio", "El monto no supera 2,5 veces el promedio histórico del origen.", "S/ 1,250 < S/ 2,400"),
        ("R4", "Intento de vaciado", "La diferencia con el saldo supera el 1 % (mínimo S/ 0,01).", "diferencia > umbral"),
    ]
    for i, (code, title, desc, example) in enumerate(rules):
        x = M + (i % 2) * 6.18
        y = 1.65 + (i // 2) * 2.15
        card(slide, x, y, 5.95, 1.9, fill=WHITE)
        card(slide, x + 0.18, y + 0.2, 0.62, 0.62, fill=SOFT_GOLD if i == 1 else SOFT_GREEN, line=None, radius=0.18)
        text(slide, code, x + 0.18, y + 0.34, 0.62, 0.26, 13, AMBER if i == 1 else GREEN, True, PP_ALIGN.CENTER)
        text(slide, title, x + 0.98, y + 0.18, 4.6, 0.3, 13.5, NAVY, True)
        text(slide, desc, x + 0.98, y + 0.55, 4.7, 0.65, 9.5, MUTED, line_spacing=1.03)
        text(slide, example, x + 0.98, y + 1.3, 4.7, 0.25, 9, AMBER if i == 1 else GREEN, True)
    card(slide, M, 6.05, 12.15, 0.75, fill=NAVY, line=None)
    text(slide, "APROBADA = R1 ∧ R2 ∧ R3 ∧ R4 ∧ saldo suficiente", M + 0.3, 6.22, 7.4, 0.35, 14, WHITE, True)
    text(slide, "Cualquier falla → PENDIENTE + caso", 8.45, 6.22, 3.9, 0.35, 12, RGBColor(0xFD, 0xE6, 0x8A), True)
    notes(slide, "Las reglas se evalúan antes de guardar la transacción y se persiste el detalle de cada una. "
                 "El analista ve exactamente qué regla falló y con qué números.")


# ------------------------------------------------------------------ 16 flujo
def s_flow():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 2", "Flujo de una transferencia",
                "Del registro a la resolución del caso, sin perder el rastro.")
    fit_image(slide, IMG / "proceso-movimiento.png", M, 1.5, 8.2, 5.1)
    steps = [
        ("1", "Registrar", "Origen, destino y monto."),
        ("2", "Bloquear", "Cuentas con FOR UPDATE."),
        ("3", "Evaluar", "R1–R4 + saldo."),
        ("4", "Resolver", "Aplicar, revertir o derivar."),
    ]
    y = 1.72
    for n, title, desc in steps:
        card(slide, 9.05, y, 0.4, 0.4, fill=TEAL, line=None, radius=0.5)
        text(slide, n, 9.05, y + 0.09, 0.4, 0.2, 8.5, WHITE, True, PP_ALIGN.CENTER)
        text(slide, title, 9.58, y - 0.02, 2.8, 0.25, 11.5, NAVY, True)
        text(slide, desc, 9.58, y + 0.26, 3.0, 0.25, 9, MUTED)
        y += 1.0
    card(slide, 9.05, 5.85, 3.6, 0.9, fill=SOFT_GOLD, line=None)
    text(slide, "16 evaluaciones", 9.22, 5.98, 3.2, 0.25, 11, AMBER, True)
    text(slide, "R1–R4 y saldo persistidos por transacción.", 9.22, 6.28, 3.2, 0.3, 8.5, MUTED)
    card(slide, 9.05, 6.9, 3.6, 0.0, fill=WHITE, line=None)
    notes(slide, "La secuencia completa está en el Word. El punto crítico es que la carga y el bloqueo de cuentas, "
                 "la evaluación, el guardado y la apertura del caso ocurren en la misma transacción.")


# ------------------------------------------------------------------ 17 casos
def s_cases():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Sprint 2", "La bandeja del analista",
                "Los casos convierten una regla fallida en una decisión revisable.")
    fit_image(slide, IMG / "wire-casos.png", M, 1.55, 7.65, 4.8)
    text(slide, "QUÉ VE EL ANALISTA", 8.5, 1.7, 3.8, 0.25, 9.5, TEAL_DARK, True)
    bullets(slide, [
        "Número de caso y transacción asociada.",
        "Cuentas origen/destino y monto.",
        "Estado de cada regla y su detalle.",
        "Acciones: aprobar, rechazar, editar, eliminar.",
        "Sincronización del caso al resolver.",
    ], 8.5, 2.05, 3.95, 2.4, 10.5, gap=6)
    card(slide, 8.5, 4.55, 4.0, 0.85, fill=SOFT_GREEN, line=None)
    text(slide, "APROBAR", 8.68, 4.68, 1.2, 0.22, 8.5, GREEN, True)
    text(slide, "Aplica saldos y deja el caso RESUELTO.", 8.68, 4.95, 3.6, 0.3, 9, MUTED)
    card(slide, 8.5, 5.5, 4.0, 0.85, fill=SOFT_RED, line=None)
    text(slide, "RECHAZAR", 8.68, 5.63, 1.2, 0.22, 8.5, RED, True)
    text(slide, "Revierte saldos y deja el caso RECHAZADO.", 8.68, 5.9, 3.6, 0.3, 9, MUTED)
    chip(slide, 8.5, 6.55, 4.0, 0.32, "RESOLVER_CASO requerido", fill=NAVY, color=WHITE, size=8.5)
    notes(slide, "La bandeja no es solo una lista: muestra la evaluación. Eso permite explicar por qué se derivó "
                 "y tomar una decisión con evidencia. Aprobar/rechazar exige RESOLVER_CASO.")


# ------------------------------------------------------------------ 18 prototipos 1
def s_proto1():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Prototipos", "Acceso y navegación",
                "Wireframes de estructura generados a partir de la interfaz implementada.")
    fit_image(slide, IMG / "wire-login.png", M, 1.65, 5.95, 3.75)
    fit_image(slide, IMG / "wire-launcher.png", 6.8, 1.65, 5.95, 3.75)
    text(slide, "Login: marca, credenciales y registro.", M, 5.55, 5.8, 0.25, 9.5, MUTED)
    text(slide, "Selector: paneles disponibles y bloqueados.", 6.8, 5.55, 5.8, 0.25, 9.5, MUTED)
    for i, (title, desc) in enumerate([
        ("Un solo shell", "sidebar, topbar, tema y logout compartidos."),
        ("Permisos visibles", "los módulos sin permiso no se muestran."),
        ("Responsive", "drawer en móvil y contenido fluido."),
    ]):
        x = M + i * 4.08
        card(slide, x, 6.0, 3.85, 0.72, fill=WHITE)
        text(slide, title, x + 0.15, 6.08, 3.5, 0.22, 9.5, NAVY, True)
        text(slide, desc, x + 0.15, 6.33, 3.5, 0.25, 8, MUTED)
    notes(slide, "Los wireframes muestran la estructura real: login a dos columnas, selector de paneles con tarjetas. "
                 "El shell es único: sidebar, topbar, tema y logout no se duplican por panel.")


# ------------------------------------------------------------------ 19 prototipos 2
def s_proto2():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Prototipos", "Administración y cuentas",
                "Dashboards con KPIs y tablas operativas.")
    fit_image(slide, IMG / "wire-admin.png", M, 1.65, 5.95, 3.75)
    fit_image(slide, IMG / "wire-cuentas.png", 6.8, 1.65, 5.95, 3.75)
    text(slide, "Administración: usuarios, roles y permisos.", M, 5.55, 5.8, 0.25, 9.5, MUTED)
    text(slide, "Cuentas: saldo, titular, tipo y estado.", 6.8, 5.55, 5.8, 0.25, 9.5, MUTED)
    card(slide, M, 6.0, 5.95, 0.72, fill=SOFT_BLUE, line=None)
    text(slide, "4 KPIs + actividad reciente", M + 0.15, 6.08, 5.6, 0.22, 9.5, BLUE, True)
    card(slide, 6.8, 6.0, 5.95, 0.72, fill=SOFT_GREEN, line=None)
    text(slide, "Tabla con acciones por permiso", 6.95, 6.08, 5.6, 0.22, 9.5, GREEN, True)
    notes(slide, "El dashboard administrativo muestra usuarios, roles, permisos y cuentas. La tabla de cuentas "
                 "incluye estado y acciones; una cuenta con movimientos no se elimina.")


# ------------------------------------------------------------------ 20 prototipos 3
def s_proto3():
    slide = new_slide()
    slide_title(slide, "Capítulo 3 · Prototipos", "Movimientos y casos",
                "La evaluación de reglas se muestra junto a la operación.")
    fit_image(slide, IMG / "wire-movimientos.png", M, 1.65, 5.95, 3.75)
    fit_image(slide, IMG / "wire-casos.png", 6.8, 1.65, 5.95, 3.75)
    text(slide, "Movimientos: filtros, estados y evaluación.", M, 5.55, 5.8, 0.25, 9.5, MUTED)
    text(slide, "Casos: bandeja y detalle de reglas.", 6.8, 5.55, 5.8, 0.25, 9.5, MUTED)
    for i, c in enumerate(["R1 ✓  R2 ✗  R3 ✓  R4 ✓", "ABIERTO → RESUELTO", "RESOLVER_CASO"]):
        chip(slide, M + i * 4.08, 6.0, 3.85, 0.4, c, fill=NAVY if i == 2 else WHITE,
             color=WHITE if i == 2 else NAVY, size=8.5)
    notes(slide, "Movimientos y casos comparten la misma información de reglas. El analista puede ver el detalle "
                 "y decidir; el usuario ve el estado de su operación.")


# ------------------------------------------------------------------ 21 pruebas
def s_tests():
    slide = new_slide()
    slide_title(slide, "Capítulo 4", "Verificación del proyecto",
                "Build, pruebas, API, seguridad y consistencia del esquema.")
    rows = [
        ("Build frontend", "Exit 0", "323,48 kB inicial"),
        ("Pruebas backend", "Exit 0", "Spring + MySQL"),
        ("Health / API", "204 / 200", "11 endpoints"),
        ("Seguridad", "401 / 403", "sin token / CORS"),
        ("Validación", "400", "POST vacío"),
        ("Base de datos", "10 tablas", "2 vistas · 6 triggers"),
        ("E2E y carga", "Pendiente", "plan de regresión"),
    ]
    table(slide, ["Comprobación", "Resultado", "Evidencia"], rows, M, 1.7, 8.0, 4.2,
          col_widths=[3.0, 2.0, 3.0], font_size=9.5, header_size=9.5)
    # donut
    data = ChartData()
    data.categories = ["Aprobadas", "Parciales", "Diseñadas"]
    data.add_series("Pruebas", (19, 2, 1))
    chart = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(9.0), Inches(1.65), Inches(3.65), Inches(3.35), data).chart
    chart.has_title = True
    chart.chart_title.text_frame.text = "22 pruebas"
    chart.chart_title.text_frame.paragraphs[0].font.size = Pt(11)
    chart.chart_title.text_frame.paragraphs[0].font.bold = True
    chart.chart_title.text_frame.paragraphs[0].font.color.rgb = NAVY
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(8)
    chart.font.name = FONT
    chart.font.size = Pt(9)
    try:
        chart.plots[0].has_data_labels = True
        chart.plots[0].data_labels.font.size = Pt(9)
        chart.plots[0].data_labels.font.bold = True
    except Exception:
        pass
    card(slide, 9.0, 5.25, 3.65, 1.25, fill=SOFT_GOLD, line=None)
    text(slide, "19 aprobadas · 2 parciales · 1 diseñada", 9.18, 5.38, 3.3, 0.3, 9.5, AMBER, True)
    text(slide, "Las parciales/diseñadas no se reportan como aprobadas.", 9.18, 5.72, 3.3, 0.5, 8.5, MUTED)
    text(slide, "La verificación se ejecutó el 25/10/2026 en el entorno local.", M, 6.35, 8.0, 0.3, 9.5, MUTED, italic=True)
    notes(slide, "Resultados reales: build y tests en verde; health 204; login y endpoints 200; sin token 401; "
                 "CORS externo 403; POST vacío 400. La suite E2E queda pendiente y se declara como tal.")


# ------------------------------------------------------------------ 22 despliegue
def s_deploy():
    slide = new_slide()
    slide_title(slide, "Capítulo 4", "Despliegue en un contenedor",
                "nginx + Spring Boot + Angular; MySQL queda fuera del contenedor.")
    # browser
    card(slide, M, 2.0, 1.55, 2.1, fill=SOFT_BLUE, line=None)
    text(slide, "NAVEGADOR", M + 0.18, 2.15, 1.25, 0.22, 7.5, BLUE, True)
    text(slide, "SPA\nAngular", M + 0.18, 2.52, 1.2, 0.8, 12, NAVY, True)
    # container (solo nginx + backend)
    card(slide, 2.35, 1.7, 6.0, 3.0, fill=WHITE, line=NAVY, line_width=1.5)
    text(slide, "CONTENEDOR DOCKER", 2.55, 1.85, 4.0, 0.25, 8.5, NAVY, True)
    boxes = [
        ("nginx", "SPA + proxy /api\nPORT 10000", 2.65, TEAL_DARK, SOFT_GREEN),
        ("Spring Boot", "API /api\nBACKEND_PORT 2003", 4.85, AMBER, SOFT_GOLD),
    ]
    for title, desc, x, color, fill in boxes:
        card(slide, x, 2.23, 1.85, 1.55, fill=fill, line=None)
        text(slide, title, x + 0.15, 2.4, 1.55, 0.28, 12, color, True)
        text(slide, desc, x + 0.15, 2.8, 1.55, 0.75, 8.5, NAVY)
    text(slide, "→", 4.53, 2.83, 0.28, 0.3, 18, MUTED, True, PP_ALIGN.CENTER)
    text(slide, "supervisord arranca nginx y el backend", 2.7, 4.1, 5.3, 0.25, 9, MUTED)
    text(slide, "Render inyecta PORT y las variables de entorno.", 2.7, 4.39, 5.3, 0.25, 9, MUTED)
    # MySQL fuera del contenedor
    card(slide, 8.75, 2.1, 2.05, 1.55, fill=SOFT_BLUE, line=None)
    text(slide, "MySQL 8", 8.92, 2.27, 1.7, 0.28, 12, BLUE, True)
    text(slide, "Base de datos\nservicio externo", 8.92, 2.67, 1.7, 0.75, 8.5, NAVY)
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.78), Inches(2.78), Inches(1.9), Inches(0.12))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = MUTED
    arrow.line.fill.background()
    text(slide, "JDBC", 8.42, 2.35, 0.35, 0.25, 7.5, MUTED, True)
    flow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(2.14), Inches(2.95), Inches(0.18), Inches(0.1))
    flow.fill.solid()
    flow.fill.fore_color.rgb = MUTED
    flow.line.fill.background()
    # chips
    chip(slide, 2.65, 4.8, 1.8, 0.35, "1 solo servicio", fill=NAVY, color=WHITE, size=8.5)
    chip(slide, 4.6, 4.8, 1.8, 0.35, "1 solo puerto", fill=NAVY, color=WHITE, size=8.5)
    chip(slide, 6.55, 4.8, 1.8, 0.35, "sin CORS", fill=NAVY, color=WHITE, size=8.5)
    # pasos
    steps = [
        ("1", "Esquema", "mysql < backend/schema.sql"),
        ("2", "Entorno", "backend/.env + JWT_SECRET"),
        ("3", "Build", "docker build -t sistema-bancario ."),
        ("4", "Publicar", "Render Blueprint / health /api/health"),
    ]
    x = M
    for n, title, desc in steps:
        card(slide, x, 5.45, 2.9, 1.15, fill=WHITE)
        card(slide, x + 0.16, 5.6, 0.36, 0.36, fill=TEAL, line=None, radius=0.5)
        text(slide, n, x + 0.16, 5.68, 0.36, 0.18, 8, WHITE, True, PP_ALIGN.CENTER)
        text(slide, title, x + 0.62, 5.58, 2.1, 0.25, 11, NAVY, True)
        text(slide, desc, x + 0.16, 5.95, 2.55, 0.45, 8.5, MUTED)
        x += 3.05
    text(slide, "El plan gratuito de Render suspende el servicio tras 15 min de inactividad.",
         M, 6.8, 12.0, 0.3, 8.5, MUTED, italic=True)
    notes(slide, "El Dockerfile compila Angular y Spring, y en runtime ejecuta nginx + supervisord + backend. "
                 "MySQL es un servicio externo; Render publica un solo puerto y usa /api/health como health check.")


# ------------------------------------------------------------------ 23 seguridad
def s_security():
    slide = new_slide()
    slide_title(slide, "Capítulo 4", "Seguridad y mantenimiento",
                "Lo que ya está implementado y lo que debe crecer antes de producción.")
    text(slide, "IMPLEMENTADO", M, 1.72, 5.5, 0.25, 9.5, TEAL_DARK, True)
    items = [
        ("JWT HS256", "Token firmado, expiración y validación de issuer."),
        ("BCrypt + rate limit", "Hash lento y doble cubo por IP/usuario."),
        ("RBAC + overrides", "Permisos por endpoint; deny-wins."),
        ("Auditoría", "creado_por, actualizado_por y fechas."),
        ("Integridad", "Transacciones SQL y bloqueo pesimista."),
    ]
    y = 2.08
    for title, desc in items:
        card(slide, M, y, 0.1, 0.62, fill=TEAL, line=None, radius=0.2)
        text(slide, title, M + 0.25, y, 2.4, 0.25, 10.5, NAVY, True)
        text(slide, desc, 3.25, y + 0.02, 2.9, 0.5, 9.5, MUTED)
        y += 0.78
    text(slide, "SIGUIENTE NIVEL", 6.75, 1.72, 5.0, 0.25, 9.5, AMBER, True)
    bullets(slide, [
        "MFA (TOTP) y recuperación por correo.",
        "Refresh tokens con rotación y revocación.",
        "Backups automáticos y prueba de restauración.",
        "Observabilidad: métricas, trazas y alertas.",
        "CI/CD con análisis de dependencias y secretos.",
        "Cifrado en reposo y gestión de secretos.",
    ], 6.75, 2.08, 5.8, 3.0, 11, gap=6, bullet_color=AMBER)
    card(slide, 6.75, 5.25, 5.8, 0.9, fill=SOFT_RED, line=None)
    text(slide, "No implementado: MFA, revocación de JWT, backups automáticos ni cumplimiento regulatorio.",
         6.92, 5.38, 5.45, 0.55, 9, RED, line_spacing=1.02)
    text(slide, "El prototipo demuestra el control de acceso; un banco real exige más capas.",
         M, 6.4, 12.0, 0.3, 9.5, MUTED, italic=True)
    notes(slide, "La seguridad implementada es sólida para el alcance: JWT, BCrypt, rate limit, RBAC y auditoría. "
                 "Las recomendaciones incluyen MFA, refresh tokens, backups y observabilidad.")


# ------------------------------------------------------------------ 24 conclusiones
def s_conclusions():
    slide = new_slide()
    slide_title(slide, "Cierre", "Conclusiones", "Un sistema demostrativo con decisiones de ingeniería verificables.")
    cards = [
        ("01", "Un solo shell", "Administración, Cuentas, Transacciones y Analista comparten sidebar, topbar, tema y logout."),
        ("02", "RBAC expresivo", "Roles, permisos y overrides con deny-wins; el backend valida cada endpoint."),
        ("03", "Reglas explicables", "R1–R4 con detalle persistido; el analista decide con evidencia, no a ciegas."),
        ("04", "Verificación real", "Build, tests, API, seguridad y base de datos comprobados el 25/10/2026."),
    ]
    for i, (n, title, desc) in enumerate(cards):
        x = M + (i % 2) * 6.18
        y = 1.7 + (i // 2) * 2.05
        card(slide, x, y, 5.95, 1.8, fill=WHITE)
        text(slide, n, x + 0.22, y + 0.2, 0.7, 0.35, 18, TEAL_DARK, True)
        text(slide, title, x + 1.0, y + 0.2, 4.7, 0.3, 14, NAVY, True)
        text(slide, desc, x + 1.0, y + 0.6, 4.7, 0.95, 9.8, MUTED, line_spacing=1.05)
    card(slide, M, 5.9, 12.15, 0.8, fill=NAVY, line=None)
    text(slide, "Límites: operación simulada · sin MFA · sin revocación de tokens · sin suite E2E automatizada.",
         M + 0.25, 6.1, 11.6, 0.35, 10.5, WHITE, True)
    notes(slide, "Cierre: el valor está en la arquitectura, el control de acceso, las reglas explicables y la "
                 "verificación reproducible. Los límites se declaran sin maquillarlos.")


# ------------------------------------------------------------------ 25 recomendaciones
def s_recommendations():
    slide = new_slide()
    slide_title(slide, "Cierre", "Recomendaciones", "Siguientes pasos para acercar el prototipo a producción.")
    left = [
        "MFA y recuperación de contraseña.",
        "Refresh tokens con rotación y revocación.",
        "Pruebas E2E con Playwright.",
        "Pruebas de integración con Testcontainers.",
        "Idempotency keys en movimientos.",
    ]
    right = [
        "Reglas configurables y versionadas.",
        "Notificaciones de casos y movimientos.",
        "Observabilidad y alertas operativas.",
        "Backups automáticos y restauración.",
        "CI/CD con escaneo de secretos.",
    ]
    bullets(slide, left, M, 2.0, 5.7, 3.2, 12.5, gap=10, bullet_color=TEAL)
    bullets(slide, right, 6.7, 2.0, 5.7, 3.2, 12.5, gap=10, bullet_color=GOLD)
    card(slide, M, 5.45, 12.15, 1.0, fill=SOFT_GREEN, line=None)
    text(slide, "Siguiente iteración sugerida", M + 0.25, 5.58, 4.0, 0.25, 9, GREEN, True)
    text(slide, "MFA + refresh tokens + E2E + observabilidad", M + 0.25, 5.9, 11.5, 0.35, 15, NAVY, True)
    text(slide, "Priorizar seguridad y pruebas antes de ampliar funcionalidad.", M, 6.6, 12.0, 0.3, 9.5, MUTED, italic=True)
    notes(slide, "Las recomendaciones se ordenan por impacto: seguridad, pruebas, resiliencia y luego evolución funcional. "
                 "No se implementan en este alcance.")


# ------------------------------------------------------------------ 26 cierre
def s_closing():
    global SLIDE_NO
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    SLIDE_NO += 1
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = NAVY
    d = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.2), Inches(-1.8), Inches(5.2), Inches(5.2))
    d.fill.solid()
    d.fill.fore_color.rgb = RGBColor(0x11, 0x4C, 0x72)
    d.line.fill.background()
    d2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11.6), Inches(4.4), Inches(3.4), Inches(3.4))
    d2.fill.solid()
    d2.fill.fore_color.rgb = RGBColor(0x0D, 0x3C, 0x5E)
    d2.line.fill.background()
    text(slide, "GRACIAS", M, 1.4, 6.0, 0.35, 12, RGBColor(0x94, 0xE8, 0xDF), True)
    text(slide, "Sistema Bancario", M, 1.9, 9.0, 0.8, 44, WHITE, True)
    text(slide, "Cuentas, movimientos y casos con seguridad y trazabilidad.",
         M, 2.95, 8.5, 0.4, 16, RGBColor(0xC4, 0xD6, 0xEB))
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(3.75), Inches(1.4), Pt(3))
    line.fill.solid()
    line.fill.fore_color.rgb = TEAL
    line.line.fill.background()
    text(slide, "Demo local: http://localhost:4200", M, 4.25, 6.0, 0.3, 13, WHITE, True)
    text(slide, "API: http://localhost:2003/api  ·  Health: /api/health", M, 4.65, 8.0, 0.3, 11, RGBColor(0x94, 0xE8, 0xDF))
    text(slide, "Documento Word y presentación disponibles en la carpeta docs/ del repositorio.",
         M, 5.35, 9.0, 0.3, 10, RGBColor(0xC4, 0xD6, 0xEB))
    text(slide, "Octubre 2026  ·  Angular 22  ·  Spring Boot 4.1.2  ·  Java 21  ·  MySQL 8",
         M, 6.55, 11.0, 0.3, 9, RGBColor(0x94, 0xA3, 0xB8))
    notes(slide, "Cierre y demo. El sistema corre localmente; la documentación y los wireframes están en docs/. "
                 "Agradecer y abrir preguntas.")


def main():
    s_cover()
    s_agenda()
    s_problem()
    s_objectives()
    s_canvas()
    s_scope()
    s_requirements()
    s_architecture()
    s_data()
    s_roles()
    s_sprint1()
    s_login()
    s_sprint2()
    s_movements()
    s_rules()
    s_flow()
    s_cases()
    s_proto1()
    s_proto2()
    s_proto3()
    s_tests()
    s_deploy()
    s_security()
    s_conclusions()
    s_recommendations()
    s_closing()
    prs.core_properties.title = "Sistema Bancario — Presentación del proyecto"
    prs.core_properties.author = "Equipo de desarrollo del Sistema Bancario"
    prs.core_properties.subject = "Planificación, diseño, desarrollo, pruebas y despliegue"
    prs.save(OUT)
    print("wrote", OUT)
    print("slides", len(prs.slides))


if __name__ == "__main__":
    main()
