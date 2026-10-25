"""Genera la documentación Word del Sistema Bancario."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
IMG = BASE / "img"
OUT = BASE / "Sistema_Bancario_Documentacion.docx"

NAVY = "0B2545"
NAVY_LIGHT = "173A66"
TEAL = "10A89E"
TEAL_DARK = "0B8079"
GOLD = "D4A017"
INK = "1F2937"
MUTED = "64748B"
LIGHT = "F4F7FB"
ZEBRA = "F8FAFC"
BORDER = "CBD5E1"

FONT = "Calibri"
MONO = "Consolas"

HOY = "25 de octubre de 2026"


# ------------------------------------------------------------------ utilidades XML
def shade(cell, color: str) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def cell_margins(table, top=60, bottom=60, left=90, right=90) -> None:
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for tag, value in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{tag}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tbl_pr.append(mar)


def table_borders(table, color=BORDER, size=4) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tbl_pr.append(borders)


def keep_row_together(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant = OxmlElement("w:cantSplit")
    tr_pr.append(cant)


def _field_char(paragraph, kind: str):
    run = paragraph.add_run()
    fld = OxmlElement("w:fldChar")
    fld.set(qn("w:fldCharType"), kind)
    run._r.append(fld)
    return run


def add_field(paragraph, instruction: str, placeholder: str = "") -> None:
    _field_char(paragraph, "begin")
    run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    run._r.append(instr)
    _field_char(paragraph, "separate")
    if placeholder:
        paragraph.add_run(placeholder)
    _field_char(paragraph, "end")


def page_number(paragraph) -> None:
    _field_char(paragraph, "begin")
    run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    run._r.append(instr)
    _field_char(paragraph, "separate")
    paragraph.add_run("1")
    _field_char(paragraph, "end")


# ------------------------------------------------------------------ estilos
def setup(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.3)
    section.right_margin = Cm(2.1)
    section.header_distance = Cm(1.0)
    section.footer_distance = Cm(1.0)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size, color, before, after in (
        ("Heading 1", 20, NAVY, 0, 14),
        ("Heading 2", 14, TEAL_DARK, 14, 8),
        ("Heading 3", 12, NAVY, 10, 6),
    ):
        style = doc.styles[name]
        style.font.name = FONT
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.line_spacing = 1.0

    doc.styles["Heading 1"].paragraph_format.page_break_before = True

    for name in ("List Bullet", "List Number"):
        style = doc.styles[name]
        style.font.name = FONT
        style.font.size = Pt(10.5)
        style.paragraph_format.space_after = Pt(3)
        style.paragraph_format.line_spacing = 1.1

    # Encabezado
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("Sistema Bancario  ·  Documentación del proyecto")
    run.font.name = FONT
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(MUTED)
    p_pr = header._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:color"), BORDER)
    borders.append(bottom)
    p_pr.append(borders)

    # Pie con número de página
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Página ")
    run.font.name = FONT
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(MUTED)
    page_number(footer)
    for r in footer.runs:
        r.font.name = FONT
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor.from_string(MUTED)


def h1(doc, text: str) -> None:
    doc.add_heading(text, level=1)


def h2(doc, text: str) -> None:
    doc.add_heading(text, level=2)


def h3(doc, text: str) -> None:
    doc.add_heading(text, level=3)


def p(doc, text: str, bold_lead: str | None = None, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    par = doc.add_paragraph()
    par.alignment = align
    if bold_lead:
        run = par.add_run(bold_lead)
        run.bold = True
    par.add_run(text)
    return par


def bullets(doc, items: list[str]) -> None:
    for item in items:
        par = doc.add_paragraph(item, style="List Bullet")
        par.paragraph_format.left_indent = Cm(0.7)
        par.paragraph_format.first_line_indent = Cm(-0.3)


def numbered(doc, items: list[str]) -> None:
    for i, item in enumerate(items, start=1):
        par = doc.add_paragraph()
        par.paragraph_format.left_indent = Cm(0.8)
        par.paragraph_format.first_line_indent = Cm(-0.4)
        par.paragraph_format.space_after = Pt(3)
        run = par.add_run(f"{i}.  ")
        run.bold = True
        par.add_run(item)


def caption(doc, text: str) -> None:
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(3)
    par.paragraph_format.space_after = Pt(10)
    run = par.add_run(text)
    run.italic = True
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(MUTED)


def image(doc, name: str, width=16.4, cap: str = "") -> None:
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(2)
    par.add_run().add_picture(str(IMG / name), width=Cm(width))
    if cap:
        caption(doc, cap)


def add_table(doc, headers: list[str], rows: list[list[str]], widths: list[float] | None = None,
              font_size=8.5, header_size=8.5, zebra=True, align_center=False) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table_borders(table)
    cell_margins(table)
    hdr = table.rows[0]
    keep_row_together(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        par = cell.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(0)
        run = par.add_run(text)
        run.bold = True
        run.font.size = Pt(header_size)
        run.font.color.rgb = RGBColor.from_string("FFFFFF")
        shade(cell, NAVY)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    for r_idx, row in enumerate(rows):
        cells = table.add_row().cells
        keep_row_together(table.rows[-1])
        for i, value in enumerate(row):
            cell = cells[i]
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
            if align_center:
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = par.add_run(str(value))
            run.font.size = Pt(font_size)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if zebra and r_idx % 2 == 1:
                shade(cell, ZEBRA)
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Cm(width)
    # repetir encabezado en páginas siguientes
    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def note(doc, title: str, text: str, color=GOLD, fill="FFF7E0") -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Cm(16.4)
    cell = table.rows[0].cells[0]
    cell.width = Cm(16.4)
    shade(cell, fill)
    table_borders(table, color=color, size=6)
    cell_margins(table, top=120, bottom=120, left=180, right=180)
    par = cell.paragraphs[0]
    par.paragraph_format.space_after = Pt(2)
    run = par.add_run(title)
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(NAVY)
    par2 = cell.add_paragraph()
    par2.paragraph_format.space_after = Pt(0)
    run2 = par2.add_run(text)
    run2.font.size = Pt(9)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def code(doc, text: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Cm(16.4)
    cell = table.rows[0].cells[0]
    shade(cell, "F1F5F9")
    table_borders(table, color=BORDER, size=4)
    cell_margins(table, top=120, bottom=120, left=160, right=160)
    par = cell.paragraphs[0]
    par.paragraph_format.space_after = Pt(0)
    for i, line in enumerate(text.strip("\n").split("\n")):
        run = par.add_run(line)
        run.font.name = MONO
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string(INK)
        if i < len(text.strip("\n").split("\n")) - 1:
            run.add_break()
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def kv(doc, rows: list[tuple[str, str]]) -> None:
    add_table(doc, ["Elemento", "Detalle"], [[a, b] for a, b in rows], widths=[4.4, 12.0], font_size=9)


# ------------------------------------------------------------------ datos del esquema
def split_top_level(text: str) -> list[str]:
    parts, current, depth, quote = [], "", 0, False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "'":
            if quote and i + 1 < len(text) and text[i + 1] == "'":
                current += "''"
                i += 2
                continue
            quote = not quote
        if not quote:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(current.strip())
                current = ""
                i += 1
                continue
        current += ch
        i += 1
    if current.strip():
        parts.append(current.strip())
    return parts


def schema_tables():
    schema = (ROOT / "backend" / "schema.sql").read_text(encoding="utf-8")
    matches = re.findall(r"CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\) ENGINE = InnoDB", schema, re.S)
    result = []
    for name, body in matches:
        fks = {}
        for col, ref in re.findall(r"FOREIGN KEY\s*\((\w+)\)\s*REFERENCES\s*(\w+)", body, re.S):
            fks[col] = ref
        uniques = set()
        for cols in re.findall(r"UNIQUE\s*\(([^)]+)\)", body):
            for c in cols.split(","):
                uniques.add(c.strip().strip("`"))
        columns = []
        for part in split_top_level(body):
            if re.match(r"^(CONSTRAINT|PRIMARY KEY|UNIQUE|INDEX|KEY)\b", part):
                continue
            m = re.match(r"^(\w+)\s+([A-Z]+(?:\([^)]*\))?)\s*(.*)$", part, re.S)
            if not m:
                continue
            col, typ, rest = m.group(1), m.group(2), m.group(3)
            comment = ""
            cm = re.search(r"COMMENT\s+'((?:[^']|'')*)'", rest, re.S)
            if cm:
                comment = cm.group(1).replace("''", "'")
            default = ""
            dm = re.search(r"DEFAULT\s+('(?:[^']|'')*'|[^\s,]+(?:\([^)]*\))?)", rest, re.S)
            if dm:
                default = dm.group(1).strip("'")
            key = ""
            if "PRIMARY KEY" in rest:
                key = "PK"
            elif col in fks:
                key = f"FK → {fks[col]}"
            elif col in uniques:
                key = "UNIQUE"
            columns.append({
                "name": col,
                "type": typ.lower().replace("bigint", "BIGINT").replace("varchar", "VARCHAR")
                        .replace("decimal", "DECIMAL").replace("timestamp", "TIMESTAMP")
                        .replace("boolean", "BOOLEAN").replace("tinyint", "TINYINT"),
                "nullable": "No" if ("NOT NULL" in rest or "PRIMARY KEY" in rest) else "Sí",
                "key": key,
                "default": default,
                "comment": comment,
            })
        result.append({"name": name, "columns": columns})
    return result


TABLES = schema_tables()
TABLES_BY_NAME = {t["name"]: t for t in TABLES}

TABLE_DESC = {
    "usuarios": "Usuarios, credenciales y estado de acceso.",
    "roles": "Roles del sistema; ADMINISTRADOR está protegido.",
    "permisos": "Catálogo de permisos atómicos.",
    "roles_permisos": "Plantilla RBAC: permisos concedidos a cada rol.",
    "usuarios_roles": "Asignación de roles a usuarios.",
    "usuarios_permisos": "Overrides individuales grant/deny por usuario.",
    "cuentas_bancarias": "Cuentas, titular, tipo y saldo.",
    "transacciones": "Movimientos financieros y saldos posteriores.",
    "casos": "Casos abiertos para revisión del analista.",
    "transaccion_reglas": "Evaluación R1–R4 y saldo por transacción.",
}
ROW_COUNTS = {
    "usuarios": 4, "roles": 3, "permisos": 29, "usuarios_roles": 4,
    "cuentas_bancarias": 22, "transacciones": 8, "casos": 6, "transaccion_reglas": 16,
}


def dictionary(doc, names: list[str], title: str) -> None:
    h3(doc, title)
    p(doc, "Diccionario generado a partir de backend/schema.sql. Las claves foráneas y los "
           "índices se describen en la sección 2.2; aquí se documenta cada campo con su tipo, "
           "nulabilidad, clave y valor por defecto.")
    for name in names:
        table = TABLES_BY_NAME[name]
        h3(doc, f"Tabla {name}")
        p(doc, TABLE_DESC.get(name, ""))
        rows = []
        for c in table["columns"]:
            rows.append([c["name"], c["type"], c["nullable"], c["key"] or "—",
                         c["default"] or "—", c["comment"] or "—"])
        add_table(doc, ["Campo", "Tipo", "Nulo", "Clave", "Default", "Descripción"],
                  rows, widths=[3.1, 2.4, 0.9, 2.6, 3.0, 4.4], font_size=7.5, header_size=7.5)


# ------------------------------------------------------------------ portada / índice
def cover(doc: Document) -> None:
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(16)
    par.add_run().add_picture(str(IMG / "portada.png"), width=Cm(16.4))

    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(10)
    par.paragraph_format.space_after = Pt(2)
    run = par.add_run("SISTEMA BANCARIO")
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor.from_string(NAVY)
    run.font.name = FONT

    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(18)
    run = par.add_run("Documentación del proyecto: planificación, diseño, desarrollo, pruebas y despliegue")
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor.from_string(MUTED)

    kv(doc, [
        ("Tipo de documento", "Documentación técnica y académica del proyecto"),
        ("Producto", "Aplicación web de gestión de cuentas y movimientos bancarios"),
        ("Versión", "1.0"),
        ("Fecha", HOY),
        ("Stack", "Angular 22 · Spring Boot 4.1.2 · Java 21 · MySQL 8"),
        ("Autor", "Equipo de desarrollo del Sistema Bancario"),
        ("Estado", "Documento de entrega; proyecto verificado en entorno local"),
    ])
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run("Documento demostrativo. El sistema no procesa dinero real.")
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(MUTED)


def table_of_contents(doc: Document) -> None:
    h1(doc, "Contenido")
    p(doc, "El índice se actualiza automáticamente en Word. Si aparece desactualizado, pulsa "
           "Ctrl+E (Windows) o Cmd+E (macOS) y elige «Actualizar campo» → «Actualizar toda la tabla».")
    par = doc.add_paragraph()
    add_field(par, 'TOC \\o "1-3" \\h \\z \\u',
              "Abre el documento en Word y actualiza el campo para generar el índice.")
    par.paragraph_format.space_before = Pt(8)

    h2(doc, "Resumen ejecutivo")
    p(doc, "El Sistema Bancario es una aplicación web desarrollada como proyecto académico para "
           "centralizar la gestión de usuarios, roles y permisos, cuentas bancarias y movimientos "
           "financieros. La solución separa responsabilidades en cuatro paneles —Administración, "
           "Cuentas, Transacciones y Analista— y aplica un modelo RBAC con overrides por usuario, "
           "autenticación JWT, auditoría y un motor de reglas que decide si una transferencia o pago "
           "se aprueba automáticamente o queda pendiente para revisión.")
    p(doc, "El frontend está construido con Angular 22 standalone y signals; el backend con Spring "
           "Boot 4.1.2, Java 21 y Spring Data JPA; la persistencia usa MySQL 8 con transacciones SQL "
           "y bloqueo pesimista. La verificación del 25 de octubre de 2026 confirmó que el frontend "
           "compila, las pruebas del backend pasan, los endpoints principales responden y la base "
           "de datos contiene 4 usuarios, 3 roles, 29 permisos, 22 cuentas y 8 movimientos de prueba.")
    note(doc, "Alcance del documento",
         "Este documento describe el sistema implementado, no un diseño hipotético. Los diagramas, "
         "wireframes, diccionarios y resultados de pruebas se elaboraron a partir del código y de la "
         "base de datos del repositorio. Las cifras de datos corresponden al entorno local de desarrollo.")

    h2(doc, "Mapa del documento")
    add_table(doc, ["Sección", "Contenido"], [
        ["1. Planificación y análisis", "Problema, objetivos, Canvas, charter, WBS, cronograma, alcance, estado del arte, requerimientos y wireframes."],
        ["2. Diseño", "Arquitectura de software, modelo entidad-relación lógico y físico, y diagrama de clases."],
        ["3. Desarrollo", "Sprint 1 de autenticación; Sprint 2 de cuentas y movimientos; procesos, casos de uso, secuencias, diccionarios, prototipos y pruebas."],
        ["4. Pruebas, despliegue y mantenimiento", "Manual de usuarios, manual de instalación, verificación, solución de problemas y mantenimiento."],
        ["5. Conclusiones y 6. Recomendaciones", "Resultados del proyecto, límites y siguientes pasos."],
        ["Referencias y anexos", "Fuentes consultadas, matriz de permisos, endpoints y evidencia de verificación."],
    ], widths=[4.5, 11.9], font_size=8.5)


# ------------------------------------------------------------------ capítulo 1
def chapter1(doc: Document) -> None:
    h1(doc, "1. PLANIFICACIÓN Y ANÁLISIS")

    h2(doc, "1.1 Descripción del problema")
    p(doc, "En muchas instituciones y proyectos académicos la gestión de cuentas y movimientos se "
           "realiza con hojas de cálculo, registros manuales o aplicaciones aisladas. Esa forma de "
           "trabajar produce tres problemas recurrentes: la información no está centralizada, las "
           "operaciones no dejan una traza confiable de quién hizo qué y no existe un criterio "
           "uniforme para decidir cuándo una transferencia debe revisarse antes de aplicarse.")
    p(doc, "El problema se acentúa cuando conviven varios perfiles. Un usuario necesita consultar sus "
           "cuentas y registrar movimientos sin depender de un operador; un analista necesita una "
           "bandeja única de casos pendientes; un administrador necesita gobernar identidades, roles y "
           "permisos sin romper la seguridad. Si cada perfil usa una herramienta distinta, se duplican "
           "datos y se pierde la posibilidad de auditar el proceso completo.")
    p(doc, "El Sistema Bancario aborda ese problema con una aplicación web de un solo origen que "
           "integra acceso, cuentas, movimientos, reglas de aprobación y resolución de casos. El "
           "sistema es demostrativo: simula saldos y operaciones, no se conecta a una red bancaria real "
           "ni procesa dinero. Aun así, reproduce las decisiones de diseño relevantes: autenticación "
           "stateless, autorización por permiso, integridad contable y trazabilidad.")

    h2(doc, "1.2 Definición de objetivos")
    h3(doc, "1.2.1 Objetivo general")
    p(doc, "Diseñar e implementar una aplicación web que permita gestionar cuentas bancarias y "
           "movimientos financieros con autenticación, autorización por roles y permisos, reglas de "
           "aprobación automática y una bandeja de resolución de casos, manteniendo trazabilidad y "
           "consistencia de saldos.")
    h3(doc, "1.2.2 Objetivos específicos")
    bullets(doc, [
        "Implementar un acceso seguro con JWT, BCrypt, límite de intentos y cierre de sesión por expiración.",
        "Construir un modelo RBAC con roles, permisos y overrides por usuario, aplicado tanto en el menú como en cada endpoint.",
        "Gestionar cuentas de tipo ahorro, corriente y empresarial, con saldo, estado y titular.",
        "Registrar depósitos, retiros, transferencias y pagos, aplicando saldos dentro de una transacción SQL.",
        "Automatizar la aprobación de transferencias y pagos mediante las reglas R1–R4 y la validación de saldo.",
        "Abrir casos para las operaciones que no cumplen las reglas y permitir que el analista las apruebe, rechace o edite.",
        "Ofrecer dashboards y listados filtrables por estado, tipo y cuenta para los cuatro paneles.",
        "Empaquetar frontend, backend y nginx en una imagen Docker desplegable en Render.",
    ])

    h2(doc, "1.3 Modelo Canvas")
    p(doc, "El lienzo se adapta a un proyecto académico con operación simulada. El bloque de ingresos "
           "se deja explícito como «no aplica» para no presentar el prototipo como un producto comercial.")
    canvas_rows = [
        ("Socios clave", "Equipo de desarrollo, docente/asesor del proyecto, proveedor de hosting y MySQL local."),
        ("Actividades clave", "Análisis de requisitos, diseño de arquitectura y datos, desarrollo por sprints, pruebas y despliegue."),
        ("Propuesta de valor", "Centralizar cuentas, movimientos y casos en una sola aplicación, con reglas automáticas y trazabilidad por usuario."),
        ("Relación con clientes", "Autoservicio para el usuario; bandeja de revisión para el analista; gobierno de accesos para el administrador."),
        ("Segmentos de clientes", "Usuarios bancarios (demostración), analistas de operaciones y administradores del sistema."),
        ("Recursos clave", "Equipo, repositorio, stack Angular/Spring/MySQL, base de datos, contenedor Docker y documentación."),
        ("Canales", "Aplicación web responsive servida por nginx; API REST para el frontend."),
        ("Estructura de costes", "Tiempo de desarrollo, equipo de cómputo, hosting gratuito y base de datos local."),
        ("Fuentes de ingreso", "No aplica: proyecto académico sin cobro. Un despliegue comercial requeriría licenciamiento o suscripción."),
    ]
    add_table(doc, ["Bloque", "Contenido"], [[a, b] for a, b in canvas_rows], widths=[4.0, 12.4], font_size=9)

    h2(doc, "1.4 Project Charter")
    charter = [
        ("Nombre del proyecto", "Sistema Bancario — gestión de cuentas, movimientos y casos."),
        ("Propósito", "Demostrar una solución web completa para operar cuentas y movimientos con seguridad, reglas y trazabilidad."),
        ("Alcance", "Acceso, administración RBAC, cuentas, movimientos, motor de reglas, casos, dashboards, Docker y documentación."),
        ("Objetivo medible", "Cubrir los flujos de los tres roles, con build y pruebas en verde y endpoints principales operativos."),
        ("Entregables", "Código fuente, esquema SQL, aplicación Angular, API Spring, imagen Docker, manuales y esta documentación."),
        ("Interesados", "Equipo de desarrollo, docente, usuarios de prueba (USUARIO, ANALISTA, ADMINISTRADOR)."),
        ("Hitos", "Planificación; diseño; Sprint 1 de autenticación; Sprint 2 de cuentas y movimientos; pruebas y despliegue."),
        ("Riesgos", "Cambios de alcance, configuración incorrecta de MySQL/.env, fuga de secretos, falta de pruebas E2E automatizadas."),
        ("Presupuesto", "Ocho semanas de trabajo académico; sin licencias pagadas. Hosting en plan gratuito."),
        ("Criterios de éxito", "Compilación sin errores, pruebas del backend en verde, API protegida, datos consistentes y documentación reproducible."),
    ]
    kv(doc, charter)

    h2(doc, "1.5 Work Breakdown Structure")
    p(doc, "La WBS organiza el trabajo en cuatro paquetes y ocho entregables. La numeración se usa "
           "también en el cronograma y en las tablas de sprint.")
    image(doc, "wbs.png", 16.4, "Figura 1. Estructura de desglose del trabajo del Sistema Bancario.")
    wbs_rows = [
        ("1.1", "Gestión del proyecto", "Charter, acta de constitución, riesgos y criterios de aceptación.", "Equipo"),
        ("1.2", "Análisis", "Problema, objetivos, Canvas, requerimientos funcionales y no funcionales.", "Analista"),
        ("2.1", "Arquitectura", "Vista de capas, decisión SPA + REST, seguridad y despliegue.", "Arquitecto"),
        ("2.2", "Datos", "Modelo ER lógico, modelo físico, diccionario y reglas de integridad.", "Diseñador de datos"),
        ("2.3", "Interfaz", "Wireframes, shell compartido, componentes y comportamiento responsive.", "Diseñador UI"),
        ("3.1", "Sprint 1", "Autenticación, RBAC, usuarios, roles, permisos y sesión.", "Backend + Frontend"),
        ("3.2", "Sprint 2", "Cuentas, movimientos, reglas, casos y dashboards.", "Backend + Frontend"),
        ("4.1", "Pruebas", "Build, pruebas de contexto, API, seguridad y base de datos.", "QA"),
        ("4.2", "Despliegue y manuales", "Docker, Render, manual de usuario y de instalación.", "DevOps + Documentación"),
    ]
    add_table(doc, ["Código", "Paquete", "Entregable", "Responsable"],
              [[a, b, c, d] for a, b, c, d in wbs_rows], widths=[1.6, 3.3, 8.4, 3.1], font_size=8.5)

    doc.add_page_break()
    h2(doc, "1.6 Cronograma")
    p(doc, "El proyecto se planificó en ocho semanas. La columna «●» indica las semanas con trabajo "
           "activo; las actividades de documentación y pruebas se solapan con los sprints.")
    gantt_headers = ["Actividad", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
    gantt = [
        ("Planificación y charter", ["●", "●", "", "", "", "", "", ""]),
        ("Requerimientos y Canvas", ["", "●", "●", "", "", "", "", ""]),
        ("Arquitectura y modelo de datos", ["", "", "●", "●", "", "", "", ""]),
        ("Sprint 1: autenticación y RBAC", ["", "", "●", "●", "", "", "", ""]),
        ("Sprint 2: cuentas y movimientos", ["", "", "", "", "●", "●", "●", ""]),
        ("Pruebas funcionales y de seguridad", ["", "", "", "", "", "●", "●", "●"]),
        ("Documentación y manuales", ["", "●", "●", "●", "●", "●", "●", "●"]),
        ("Docker y despliegue", ["", "", "", "", "", "", "", "●"]),
    ]
    table = doc.add_table(rows=1, cols=9)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table_borders(table)
    cell_margins(table, top=50, bottom=50, left=60, right=60)
    for i, text in enumerate(gantt_headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        par = cell.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(0)
        run = par.add_run(text)
        run.bold = True
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string("FFFFFF")
        shade(cell, NAVY)
    for r_idx, (activity, marks) in enumerate(gantt):
        cells = table.add_row().cells
        keep_row_together(table.rows[-1])
        cells[0].text = ""
        run = cells[0].paragraphs[0].add_run(activity)
        run.font.size = Pt(8)
        for i, mark in enumerate(marks, start=1):
            cell = cells[i]
            cell.text = ""
            par = cell.paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(0)
            run = par.add_run(mark)
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor.from_string("FFFFFF")
            if mark:
                shade(cell, TEAL if r_idx % 2 == 0 else NAVY_LIGHT)
    for row in table.rows:
        row.cells[0].width = Cm(7.2)
        for i in range(1, 9):
            row.cells[i].width = Cm(1.15)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    h2(doc, "1.7 Alcances y limitaciones")
    h3(doc, "1.7.1 Alcances")
    bullets(doc, [
        "Acceso con login, autorregistro, sesión JWT, cierre por expiración y cambio de contraseña.",
        "Administración de usuarios, roles, permisos, asignaciones y overrides.",
        "Cuentas de ahorro, corriente y empresarial, con número generado o personalizado.",
        "Depósitos, retiros, transferencias y pagos; aplicación y reversión de saldos.",
        "Motor de reglas R1–R4 con evaluación persistida y bandeja de casos para el analista.",
        "Dashboards, filtros, tablas, paginación y tema claro/oscuro.",
        "Empaquetado en Docker con nginx y despliegue documentado en Render.",
    ])
    h3(doc, "1.7.2 Limitaciones")
    bullets(doc, [
        "Los saldos y movimientos son simulados; no hay integración con una red bancaria ni con dinero real.",
        "El sistema es monolítico en cuanto a despliegue: un contenedor con nginx, backend y frontend.",
        "No incluye autenticación multifactor, recuperación de contraseña por correo ni revocación de tokens.",
        "La base de datos de demostración no tiene réplica, alta disponibilidad ni respaldo automatizado.",
        "Las pruebas de interfaz son manuales; no hay una suite E2E automatizada en el repositorio.",
        "No se implementan cumplimiento normativo, firma digital, conciliación bancaria ni multi-moneda.",
    ])
    h3(doc, "1.7.3 Fuera del alcance")
    bullets(doc, [
        "Cobros, pasarela de pagos, tarjetas, préstamos, intereses y productos de inversión.",
        "Integración con SWIFT, ISO 8583, cámaras de compensación o billeteras externas.",
        "Aplicación móvil nativa y notificaciones push.",
        "Facturación electrónica y reportería regulatoria.",
    ])

    h2(doc, "1.8 Estado del arte")
    p(doc, "La banca digital evolucionó desde aplicaciones monolíticas con sesiones en servidor hacia "
           "arquitecturas web desacopladas, APIs REST y autenticación stateless. En el frente de "
           "seguridad, el estándar de facto para delegar identidad en APIs es JWT (RFC 7519), "
           "combinado con TLS, almacenamiento de contraseñas con funciones de derivación lentas como "
           "BCrypt y autorización granular. En el frente de producto, los sistemas modernos separan "
           "canales (web/móvil), servicios de negocio y motores de decisión; esa separación permite "
           "cambiar reglas sin reescribir la interfaz.")
    p(doc, "Para este proyecto se eligió una arquitectura de tres capas lógicas —presentación, "
           "negocio y persistencia— con un frontend SPA y un backend REST. Es una solución adecuada "
           "para el alcance académico y, a la vez, reproducible en un contenedor. El motor de reglas "
           "se implementó como un servicio de dominio, no como un producto externo, para que las "
           "decisiones R1–R4 sean auditables y explicables.")
    add_table(doc, ["Enfoque", "Ventajas", "Limitaciones", "Relación con el proyecto"],
              [["Core bancario monolítico", "Consistencia fuerte y control centralizado.", "Evolución lenta y acoplamiento alto.", "Se toma la consistencia transaccional, no el tamaño."],
               ["Banca digital con SPA + API", "Desacopla interfaz y negocio; facilita el despliegue web.", "Requiere gestionar CORS, tokens y versionado.", "Es el enfoque implementado."],
               ["Motor de reglas externo", "Reglas configurables por negocio sin recompilar.", "Costo, integración y gobernanza adicionales.", "Se implementa un motor propio, suficiente para R1–R4."],
               ["Autenticación con sesión en servidor", "Revocación inmediata y simplicidad de cookies.", "Escalado horizontal y CSRF.", "Se elige JWT stateless por el carácter de API."]],
              widths=[3.6, 4.2, 4.2, 4.4], font_size=8)

    h2(doc, "1.9 Requerimientos")
    h3(doc, "1.9.1 Requerimientos funcionales")
    rf = [
        ("RF-01", "Iniciar sesión", "Usuario", "Validar credenciales y emitir JWT con permisos.", "Alta"),
        ("RF-02", "Autorregistro", "Visitante", "Crear usuario con rol USUARIO.", "Alta"),
        ("RF-03", "Sesión vigente", "Autenticado", "Consultar usuario y permisos actuales.", "Alta"),
        ("RF-04", "Cambiar contraseña", "Autenticado", "Exigir contraseña actual y validar la nueva.", "Media"),
        ("RF-05", "Gestionar usuarios", "Administrador", "Listar, buscar, crear, editar, activar y eliminar.", "Alta"),
        ("RF-06", "Gestionar roles", "Administrador", "CRUD de roles no protegidos y sus permisos.", "Alta"),
        ("RF-07", "Gestionar permisos", "Administrador", "CRUD de permisos no base.", "Alta"),
        ("RF-08", "Asignar roles y overrides", "Administrador", "Asignar roles y conceder/denegar permisos por usuario.", "Alta"),
        ("RF-09", "Gestionar cuentas", "Usuario/Administrador", "Crear, consultar, editar y eliminar cuentas.", "Alta"),
        ("RF-10", "Cambiar estado de cuenta", "Administrador/Analista", "Activar o desactivar una cuenta.", "Media"),
        ("RF-11", "Registrar depósito", "Usuario", "Acreditar saldo con confirmación de contraseña.", "Alta"),
        ("RF-12", "Registrar retiro", "Usuario", "Debitar saldo con confirmación de contraseña.", "Alta"),
        ("RF-13", "Registrar transferencia", "Usuario", "Debitar origen y acreditar destino.", "Alta"),
        ("RF-14", "Registrar pago", "Usuario", "Mismo flujo que transferencia, con concepto.", "Alta"),
        ("RF-15", "Evaluar reglas", "Sistema", "Evaluar R1–R4 y saldo para transferencias/pagos.", "Alta"),
        ("RF-16", "Abrir caso", "Sistema", "Crear caso ABIERTO si la operación no se aprueba.", "Alta"),
        ("RF-17", "Resolver caso", "Analista", "Aprobar, rechazar, editar o eliminar la transacción.", "Alta"),
        ("RF-18", "Consultar movimientos", "Usuario/Analista", "Listar y filtrar por estado, tipo y cuenta.", "Alta"),
        ("RF-19", "Dashboards", "Todos", "Mostrar KPIs, series y actividad reciente.", "Media"),
        ("RF-20", "Auditoría", "Sistema", "Registrar creado_por, actualizado_por y fechas.", "Alta"),
        ("RF-21", "Selector de paneles", "Autenticado", "Mostrar paneles accesibles según permisos.", "Media"),
        ("RF-22", "Menú por permisos", "Autenticado", "Ocultar módulos y rutas no autorizadas.", "Alta"),
        ("RF-23", "Tema claro/oscuro", "Autenticado", "Persistir la preferencia visual.", "Baja"),
        ("RF-24", "Diseño responsive", "Todos", "Adaptar sidebar, tablas y formularios a móvil.", "Media"),
    ]
    add_table(doc, ["ID", "Requerimiento", "Actor", "Descripción", "Prioridad"],
              [list(row) for row in rf], widths=[1.2, 3.4, 3.0, 7.1, 1.7], font_size=8, header_size=8)

    h3(doc, "1.9.2 Requerimientos no funcionales")
    rnf = [
        ("RNF-01", "Seguridad", "Contraseñas con BCrypt; JWT HS256; permisos validados en cada endpoint."),
        ("RNF-02", "Confidencialidad", "No se devuelven contraseñas ni se registran tokens en logs."),
        ("RNF-03", "Integridad", "Saldos y transacciones se modifican en una transacción SQL con bloqueo pesimista."),
        ("RNF-04", "Rendimiento", "Los dashboards responden en menos de 2 s con los datos de demostración."),
        ("RNF-05", "Disponibilidad", "Health check /api/health para el despliegue en Render."),
        ("RNF-06", "Usabilidad", "Interfaz responsive, mensajes de error claros y navegación por teclado."),
        ("RNF-07", "Compatibilidad", "Navegadores modernos con soporte para ES2022 y CSS Grid/Flexbox."),
        ("RNF-08", "Mantenibilidad", "Separación por capas, DTOs, servicios y un shell único de paneles."),
        ("RNF-09", "Portabilidad", "Un solo Dockerfile con nginx, Spring Boot y Angular."),
        ("RNF-10", "Auditoría", "Campos creado_por/actualizado_por y fechas en entidades relevantes."),
        ("RNF-11", "Escalabilidad", "API stateless; la sesión no depende de memoria del servidor."),
        ("RNF-12", "Accesibilidad", "Contraste, etiquetas, foco visible y soporte de prefers-reduced-motion."),
    ]
    add_table(doc, ["ID", "Atributo", "Criterio"], [[a, b, c] for a, b, c in rnf],
              widths=[1.5, 3.2, 11.7], font_size=8.5)

    h2(doc, "1.10 Wireframes")
    p(doc, "Los wireframes reflejan la estructura real de la aplicación: un shell compartido con "
           "sidebar, topbar, contenido y acciones por permiso. Se generaron para esta documentación "
           "a partir de los componentes y de los textos usados en la interfaz; no son capturas de "
           "pantalla, sino prototipos de estructura.")
    image(doc, "wire-login.png", 16.2, "Figura 2. Wireframe de la pantalla de inicio de sesión.")
    image(doc, "wire-launcher.png", 16.2, "Figura 3. Wireframe del selector de paneles.")
    note(doc, "Criterio de diseño",
         "El sidebar se colapsa en móvil y se abre como drawer; el contenido usa una sola columna "
         "fluida. Los módulos se filtran por permisos antes de renderizar, pero el backend vuelve a "
         "validar cada petición. El tema y la sesión se gestionan desde el shell compartido.")


# ------------------------------------------------------------------ capítulo 2
def chapter2(doc: Document) -> None:
    h1(doc, "2. DISEÑO")

    h2(doc, "2.1 Diseño de arquitectura de software")
    p(doc, "La aplicación usa una arquitectura de tres capas lógicas y un despliegue de un solo "
           "contenedor. El navegador carga una SPA Angular; nginx sirve los archivos estáticos y "
           "reenvía /api al backend Spring Boot; el backend accede a MySQL mediante Spring Data JPA. "
           "La autenticación es stateless: el JWT viaja en la cabecera Authorization y el backend "
           "resuelve los permisos efectivos en cada petición.")
    image(doc, "arquitectura.png", 16.6, "Figura 4. Arquitectura lógica y de despliegue del Sistema Bancario.")
    add_table(doc, ["Capa / componente", "Responsabilidad", "Tecnología"],
              [["Presentación", "SPA, guards, interceptor JWT, formularios, tablas y dashboards.", "Angular 22, TypeScript, SCSS"],
               ["Borde / entrega", "Sirve el SPA, comprime, aplica caché y proxifica /api al backend.", "nginx + supervisord"],
               ["API", "Controladores REST, validación, autorización por permiso y respuestas uniformes.", "Spring Boot 4.1.2, Java 21"],
               ["Seguridad", "Emisión/validación de JWT, BCrypt, rate limiting y conversión de permisos.", "Spring Security, Nimbus JOSE"],
               ["Negocio", "Reglas de cuentas, movimientos, evaluación R1–R4, casos y auditoría.", "Services + @Transactional"],
               ["Persistencia", "Repositorios JPA, consultas, bloqueo pesimista y vistas de permisos.", "MySQL 8, Spring Data JPA"],
               ["Operación", "Health check, logs, imagen única y blueprint de despliegue.", "Docker, Render"]],
              widths=[3.6, 8.4, 4.4], font_size=8.5)
    p(doc, "Decisiones relevantes:")
    bullets(doc, [
        "SPA + API REST: permite separar la interfaz del dominio y reutilizar la API en otros canales.",
        "JWT sin estado: el servidor no guarda sesiones; el token contiene la identidad y el backend resuelve permisos.",
        "Permisos en el backend: la interfaz solo oculta lo que el usuario no puede usar; cada endpoint exige su autoridad.",
        "Transacciones SQL y bloqueo pesimista: evitan condiciones de carrera al aplicar o revertir saldos.",
        "Un solo contenedor: simplifica el despliegue académico y elimina CORS en producción al compartir origen.",
        "Shell único de paneles: sidebar, topbar, tema y logout viven en un solo componente.",
    ])
    note(doc, "Trazabilidad de la verificación",
         "El 25/10/2026 se comprobó el build de Angular (exit 0), las pruebas de Spring Boot (exit 0), "
         "el health check (204), el login (200), la sesión (200), los endpoints de los cuatro paneles "
         "(200) y el rechazo sin token (401). La base de datos respondió con las 10 tablas del esquema.")

    h2(doc, "2.2 Diseño de diagrama Entidad Relación (lógico y físico)")
    p(doc, "El modelo lógico se organiza en tres bloques: identidad y accesos (usuarios, roles, "
           "permisos y tablas asociativas), operación bancaria (cuentas y transacciones) y "
           "aseguramiento (casos y evaluación de reglas). El modelo físico conserva la integridad "
           "referencial con FK RESTRICT en cuentas y movimientos para no perder historial contable.")
    image(doc, "modelo-er.png", 16.6, "Figura 5. Modelo entidad-relación lógico del Sistema Bancario.")
    add_table(doc, ["Relación", "Cardinalidad", "Implementación", "Regla"],
              [["usuarios → cuentas_bancarias", "1:N", "cuentas_bancarias.usuario_id", "Un usuario puede tener varias cuentas; una cuenta tiene un titular."],
               ["usuarios ↔ roles", "N:M", "usuarios_roles", "Un usuario puede tener varios roles y un rol varios usuarios."],
               ["roles ↔ permisos", "N:M", "roles_permisos", "Plantilla RBAC; ADMINISTRADOR recibe todos los permisos."],
               ["usuarios ↔ permisos", "N:M", "usuarios_permisos", "Override grant/deny por usuario; deny-wins."],
               ["cuentas → transacciones", "1:N", "cuenta_origen_id / cuenta_destino_id", "Una cuenta participa como origen o destino en muchos movimientos."],
               ["transacciones → casos", "1:N", "casos.transaccion_id", "Una transacción puede abrir casos de revisión."],
               ["transacciones → transaccion_reglas", "1:N", "transaccion_reglas.transaccion_id", "Se guarda una fila por regla evaluada."]],
              widths=[4.2, 1.8, 4.8, 5.6], font_size=8)
    h3(doc, "2.2.1 Modelo físico")
    p(doc, "El esquema backend/schema.sql crea la base sistema_bancario con 10 tablas, 2 vistas, "
           "6 triggers y datos iniciales. La tabla siguiente resume el estado actual de la base de "
           "desarrollo; los conteos son evidencia de la verificación, no valores fijos del diseño.")
    rows = []
    for t in TABLES:
        name = t["name"]
        rows.append([name, str(len(t["columns"])), str(ROW_COUNTS.get(name, "—")), TABLE_DESC.get(name, "")])
    add_table(doc, ["Tabla", "Columnas", "Filas actuales", "Propósito"], rows,
              widths=[4.2, 1.6, 2.4, 8.2], font_size=8.5)
    p(doc, "Índices y protecciones destacadas:")
    bullets(doc, [
        "Índices compuestos por usuario, cuenta, estado y fecha para los listados y dashboards.",
        "FK RESTRICT en cuentas y transacciones para preservar el historial contable.",
        "Triggers que impiden eliminar o modificar el rol ADMINISTRADOR y los permisos base.",
        "Vistas v_permisos_efectivos y v_permisos_finales que aplican la precedencia deny-wins.",
        "Auditoría con creado_por, actualizado_por, creado_en y actualizado_en en las entidades que la requieren.",
    ])
    note(doc, "Integridad contable",
         "Una cuenta con movimientos no se elimina: se desactiva. Al eliminar o rechazar una "
         "transacción aprobada, el servicio revierte los saldos dentro de la misma transacción SQL. "
         "Las FK RESTRICT impiden borrar cuentas o transacciones que dejarían huérfano el historial.")

    h2(doc, "2.3 Diseño de diagrama de clases")
    p(doc, "El backend se organiza en controladores, servicios, repositorios y entidades JPA. Los "
           "controladores solo traducen HTTP a llamadas de servicio y aplican @PreAuthorize; los "
           "servicios concentran las reglas de negocio y la delimitación transaccional; los "
           "repositorios encapsulan las consultas.")
    image(doc, "clases.png", 16.6, "Figura 6. Diagrama de clases por capas: controladores, servicios, dominio y repositorios.")
    add_table(doc, ["Paquete", "Clase / componente", "Responsabilidad"],
              [["oracle.auth", "AuthController, AuthService, JWT", "Login, registro, sesión, cambio de contraseña y emisión de tokens."],
               ["oracle.admin", "UsuarioService, RolService, PermisoService", "CRUD de identidades, roles, permisos y asignaciones."],
               ["oracle.bancario", "CuentaService", "Apertura, edición, estado y eliminación controlada de cuentas."],
               ["oracle.bancario", "TransaccionService", "Registro, aplicación/reversión de saldos, casos y filtros."],
               ["oracle.bancario", "ReglasService", "Evaluación R1–R4 y saldo; devuelve el detalle por regla."],
               ["oracle.bancario", "AnalistaService", "Bandeja de movimientos, casos y dashboard del analista."],
               ["oracle.common", "SecurityConfig, PermisosJwtConverter", "Cadena stateless, CORS, JWT y conversión de autoridades."],
               ["oracle.common", "GlobalExceptionHandler, ApiResponse", "Errores uniformes y sobre de respuesta."],
               ["frontend/core", "Auth, SesionStore, guards, interceptores", "Sesión, permisos, rutas protegidas y cabecera Bearer."],
               ["frontend/panels", "PanelShell", "Sidebar, topbar, tema, menú y logout compartidos."]],
              widths=[3.2, 6.0, 7.2], font_size=8.5)


# ------------------------------------------------------------------ capítulo 3
def chapter3(doc: Document) -> None:
    h1(doc, "3. DESARROLLO")

    h2(doc, "3.1 Sprint 1: Autenticación de Usuarios")
    p(doc, "El primer sprint tuvo como objetivo habilitar el acceso seguro y la base del gobierno de "
           "identidades. Se implementaron login, autorregistro, sesión JWT, RBAC con overrides y los "
           "módulos de usuarios, roles y permisos. La duración planificada fue de tres semanas.")
    add_table(doc, ["Elemento", "Detalle"],
              [["Objetivo", "Permitir que un usuario se autentique y que cada operación quede autorizada por permiso."],
               ["Duración", "Semanas 1–3 (planificación y ejecución)."],
               ["Historias", "HU-01 Login; HU-02 Registro; HU-03 Sesión; HU-04 RBAC; HU-05 Administración; HU-06 Rate limiting."],
               ["Entregables", "API /auth, /usuarios, /roles, /permisos; login Angular; shell y guards."],
               ["Criterio de aceptación", "Login válido devuelve token; sin token 401; con permiso insuficiente 403; menú filtrado."],
               ["Estado", "Completado y verificado."]],
              widths=[4.0, 12.4], font_size=9)
    h3(doc, "3.1.1 Diagrama de procesos")
    p(doc, "El login aplica rate limiting por IP y por combinación IP + usuario, ejecuta BCrypt incluso "
           "cuando el usuario no existe para no filtrar su existencia por tiempo, valida el estado de "
           "la cuenta y emite un JWT con la identidad. Los permisos no se guardan en el token: se "
           "resuelven por petición para que un deny o una desactivación tengan efecto inmediato.")
    image(doc, "proceso-login.png", 15.8, "Figura 7. Proceso de inicio de sesión y respuestas de error.")
    h3(doc, "3.1.2 Diagrama de casos de uso")
    image(doc, "casos-uso.png", 16.2, "Figura 8. Casos de uso por actor del sistema.")
    add_table(doc, ["Actor", "Casos de uso principales", "Permisos clave"],
              [["USUARIO", "Iniciar sesión, registrarse, gestionar sus cuentas, depositar, retirar, transferir, pagar, consultar movimientos.", "PANEL_CUENTAS, CREAR_TRANSACCIONES, VER_TRANSACCIONES"],
               ["ANALISTA", "Revisar todas las transacciones, resolver casos, editar cuentas y consultar el dashboard.", "RESOLVER_CASO, VER_CUENTAS, MODIFICAR_CUENTAS"],
               ["ADMINISTRADOR", "Gestionar usuarios, roles, permisos, asignaciones y overrides.", "PANEL_ADMIN y permisos de administración"]],
              widths=[3.2, 8.8, 4.4], font_size=8.5)
    h3(doc, "3.1.3 Diagrama de secuencia")
    p(doc, "La secuencia de login muestra la colaboración entre la SPA, el controlador, el servicio, "
           "los repositorios y el emisor de JWT. La transacción de lectura de permisos usa la vista "
           "final, de modo que el menú y las autoridades reflejan el estado actual de la base.")
    image(doc, "secuencia-login.png", 16.2, "Figura 9. Secuencia de inicio de sesión.")
    h3(doc, "3.1.4 Diccionario de datos")
    dictionary(doc, ["usuarios", "roles", "permisos", "roles_permisos", "usuarios_roles", "usuarios_permisos"],
               "Tablas de identidad y control de accesos")
    h3(doc, "3.1.5 Prototipo")
    p(doc, "El prototipo del sprint incluye la pantalla de acceso, el selector de paneles y el "
           "dashboard administrativo. La interfaz usa una paleta azul marino/verde azulado, tarjetas "
           "de KPI, tablas y un sidebar colapsable; el tema claro/oscuro se conserva en el shell.")
    image(doc, "wire-login.png", 15.8, "Figura 10. Prototipo de la pantalla de login.")
    image(doc, "wire-launcher.png", 15.8, "Figura 11. Prototipo del selector de paneles.")
    image(doc, "wire-admin.png", 15.8, "Figura 12. Prototipo del dashboard administrativo.")
    doc.add_page_break()
    h3(doc, "3.1.6 Pruebas funcionales")
    p(doc, "Las pruebas del sprint se ejecutaron contra el entorno local con MySQL activo. La tabla "
           "distingue las pruebas ejecutadas en esta verificación de las que quedan como plan de regresión.")
    tests1 = [
        ("TF-01", "Build del frontend", "npm run build", "Compila sin errores.", "Aprobada", "Exit 0; bundle inicial 323,48 kB."),
        ("TF-02", "Pruebas del backend", "./mvnw test", "Contexto Spring y MySQL cargan.", "Aprobada", "Exit 0; 1 clase de prueba."),
        ("TF-03", "Health check", "GET /api/health", "204 sin cuerpo.", "Aprobada", "204."),
        ("TF-04", "Login válido", "POST /api/auth/login", "200 + token + 29 permisos.", "Aprobada", "200; token Bearer."),
        ("TF-05", "Credenciales inválidas", "POST /api/auth/login", "401 sin revelar el motivo.", "Aprobada", "401."),
        ("TF-06", "Acceso sin token", "GET /api/cuentas", "401.", "Aprobada", "401."),
        ("TF-07", "Token inválido", "GET /api/auth/sesion", "401.", "Aprobada", "401."),
        ("TF-08", "Sesión vigente", "GET /api/auth/sesion", "200 + usuario y permisos.", "Aprobada", "200."),
        ("TF-09", "Módulos de administración", "GET /usuarios, /roles, /permisos", "200 con datos.", "Aprobada", "200 en los tres."),
        ("TF-10", "CORS no permitido", "OPTIONS /cuentas desde origen externo", "Rechazo de CORS.", "Aprobada", "403."),
        ("TF-11", "Navegación por paneles", "Browser /admin, /cuentas, /analista", "Shell y menús correctos por rol.", "Parcial", "Verificado en navegador; falta E2E automatizado."),
    ]
    add_table(doc, ["ID", "Prueba", "Entrada", "Resultado esperado", "Estado", "Evidencia"],
              [list(t) for t in tests1], widths=[1.2, 3.2, 4.2, 3.4, 1.8, 2.6], font_size=7.5)

    h2(doc, "3.2 Sprint 2: Gestión de Cuentas y Movimientos")
    p(doc, "El segundo sprint traslada el foco al negocio bancario. Se implementaron cuentas, "
           "depósitos, retiros, transferencias, pagos, el motor de reglas y la bandeja de casos. Se "
           "mantuvo el nombre de «Sprint 2» de la plantilla académica y se adaptó «Gestión de Ventas» "
           "al dominio del proyecto: «Gestión de Cuentas y Movimientos».")
    add_table(doc, ["Elemento", "Detalle"],
              [["Objetivo", "Operar cuentas y movimientos con saldos consistentes, reglas explícitas y resolución de casos."],
               ["Duración", "Semanas 4–7."],
               ["Historias", "HU-07 Cuentas; HU-08 Depósito/retiro; HU-09 Transferencia/pago; HU-10 Reglas; HU-11 Casos; HU-12 Dashboards; HU-13 Auditoría."],
               ["Entregables", "API /cuentas, /transacciones y /analista; pantallas de cuentas, movimientos y casos; motor R1–R4."],
               ["Criterio de aceptación", "Los saldos cuadran, las operaciones que no cumplen reglas quedan pendientes y el analista puede resolverlas."],
               ["Estado", "Completado; operación simulada verificada."]],
              widths=[4.0, 12.4], font_size=9)
    h3(doc, "3.2.1 Diagrama de procesos")
    p(doc, "Depósitos y retiros se aprueban al instante tras confirmar la contraseña. Transferencias y "
           "pagos se evalúan contra R1–R4 y saldo; si pasan, se aplican los saldos, y si no, quedan "
           "PENDIENTES y abren un caso. La aprobación o el rechazo posterior del analista actualiza "
           "el caso y revierte o aplica saldos según corresponda.")
    image(doc, "proceso-movimiento.png", 16.4, "Figura 13. Proceso de registro y resolución de un movimiento.")
    add_table(doc, ["Regla", "Criterio", "Efecto si falla"],
              [["R1", "Al menos 20 % de los movimientos históricos del origen van al mismo destino.", "La operación queda PENDIENTE y se abre un caso."],
               ["R2", "Al menos 20 % de los movimientos históricos son del mismo tipo.", "La operación queda PENDIENTE."],
               ["R3", "El monto no supera 2,5 veces el promedio histórico del origen.", "La operación queda PENDIENTE."],
               ["R4", "El movimiento no deja la cuenta prácticamente vacía (diferencia > 1 % del saldo, mínimo S/ 0,01).", "La operación queda PENDIENTE."],
               ["SALDO", "El saldo del origen cubre el monto.", "Se rechaza la aprobación; no se aplica."]],
              widths=[1.6, 9.8, 5.0], font_size=8.5)
    doc.add_page_break()
    h3(doc, "3.2.2 Diagrama de casos de uso")
    p(doc, "El diagrama de la Figura 8 cubre ambos sprints. Para el Sprint 2, los casos de uso "
           "específicos y su trazabilidad con la API son los siguientes.")
    add_table(doc, ["Caso de uso", "Actor", "Endpoint", "Regla de negocio"],
              [["Abrir cuenta", "USUARIO / ADMIN", "POST /api/cuentas", "Número único; titular autorizado; tipo válido."],
               ["Editar cuenta", "USUARIO / ANALISTA", "PUT /api/cuentas/{id}", "Solo cuentas propias o privilegiadas."],
               ["Desactivar cuenta", "ANALISTA / ADMIN", "PATCH /api/cuentas/{id}/activo", "Permiso CAMBIAR_ESTADO_CUENTAS."],
               ["Depositar / retirar", "USUARIO", "POST /api/transacciones", "Contraseña obligatoria; sin motor de reglas."],
               ["Transferir / pagar", "USUARIO", "POST /api/transacciones", "R1–R4 + saldo; caso si no cumple."],
               ["Resolver caso", "ANALISTA", "PUT /api/transacciones/{id}", "Aprobar/rechazar; reversión de saldos."],
               ["Consultar bandeja", "ANALISTA", "GET /api/analista/casos", "Solo transacciones de usuarios USUARIO."]],
              widths=[4.0, 3.2, 5.2, 4.0], font_size=8.5)
    h3(doc, "3.2.3 Diagrama de secuencia")
    p(doc, "La secuencia de una transferencia muestra la carga y el bloqueo de las cuentas, la "
           "evaluación de reglas, la persistencia de la transacción y la apertura del caso. La "
           "resolución posterior reutiliza el mismo servicio y sincroniza el estado del caso.")
    image(doc, "secuencia-transferencia.png", 16.6, "Figura 14. Secuencia de transferencia y resolución de un caso.")
    h3(doc, "3.2.4 Diccionario de datos")
    dictionary(doc, ["cuentas_bancarias", "transacciones", "casos", "transaccion_reglas"],
               "Tablas de operación bancaria y aseguramiento")
    h3(doc, "3.2.5 Prototipo")
    p(doc, "Las pantallas de cuentas y movimientos priorizan la lectura rápida: filtros, KPIs, tabla "
           "con estados y acciones contextuales. La bandeja de casos muestra el detalle de la "
           "evaluación de reglas para que el analista pueda decidir con evidencia.")
    image(doc, "wire-cuentas.png", 15.8, "Figura 15. Prototipo de la gestión de cuentas.")
    image(doc, "wire-movimientos.png", 15.8, "Figura 16. Prototipo de movimientos y evaluación de reglas.")
    image(doc, "wire-casos.png", 15.8, "Figura 17. Prototipo de la bandeja de casos del analista.")
    doc.add_page_break()
    h3(doc, "3.2.6 Pruebas funcionales")
    tests2 = [
        ("TF-12", "Listado de cuentas", "GET /api/cuentas", "200 con 22 cuentas.", "Aprobada", "200; 22 registros en BD."),
        ("TF-13", "Dashboard de cuentas", "GET /api/cuentas/dashboard", "200 con KPIs.", "Aprobada", "200."),
        ("TF-14", "Listado de movimientos", "GET /api/transacciones", "200 con 8 movimientos.", "Aprobada", "200; 3 aprobadas y 5 pendientes."),
        ("TF-15", "Dashboard de transacciones", "GET /api/transacciones/dashboard", "200 con KPIs y series.", "Aprobada", "200."),
        ("TF-16", "Bandeja de casos", "GET /api/analista/casos", "200 con 6 casos.", "Aprobada", "200; 5 abiertos y 1 resuelto."),
        ("TF-17", "Dashboard del analista", "GET /api/analista/dashboard", "200 con KPIs.", "Aprobada", "200."),
        ("TF-18", "Validación de movimiento", "POST /api/transacciones vacío", "400 con errores de campo.", "Aprobada", "400."),
        ("TF-19", "Integridad del esquema", "Consulta a information_schema", "10 tablas, 2 vistas, 6 triggers.", "Aprobada", "Conteos coinciden."),
        ("TF-20", "Evaluación de reglas", "16 filas en transaccion_reglas", "R1–R4 y saldo persistidos.", "Aprobada", "16 evaluaciones."),
        ("TF-21", "Responsive y accesibilidad", "Revisión manual de breakpoints", "Sidebar drawer y foco visible.", "Parcial", "Diseñado; falta prueba automatizada."),
        ("TF-22", "Flujo completo de caso", "Crear, aprobar y revertir", "Saldos cuadran y caso se cierra.", "Diseñada", "Plan de regresión; no ejecutada en esta verificación."),
    ]
    add_table(doc, ["ID", "Prueba", "Entrada", "Resultado esperado", "Estado", "Evidencia"],
              [list(t) for t in tests2], widths=[1.2, 3.2, 4.2, 3.4, 1.8, 2.6], font_size=7.5)
    note(doc, "Lectura de los resultados",
         "Las pruebas «Aprobada» se ejecutaron en el entorno local. Las marcadas «Parcial» o "
         "«Diseñada» no se presentan como aprobadas: quedan como plan de regresión para una suite "
         "E2E. La verificación funcional de esta entrega se concentra en build, contexto Spring, API, "
         "seguridad y consistencia del esquema.")


# ------------------------------------------------------------------ capítulo 4
def chapter4(doc: Document) -> None:
    h1(doc, "4. PRUEBAS, DESPLIEGUE Y MANTENIMIENTO")

    h2(doc, "4.1 Manual de usuarios")
    p(doc, "El sistema tiene tres roles operativos. El menú y las rutas se filtran por permisos; si un "
           "usuario intenta abrir una ruta para la que no tiene permiso, el guard lo redirige a "
           "«Sin acceso». El backend vuelve a validar cada operación.")
    add_table(doc, ["Rol", "Puede hacer", "No puede hacer"],
              [["USUARIO", "Ver y operar sus propias cuentas; depositar, retirar, transferir, pagar y consultar sus movimientos.", "Ver cuentas ajenas, resolver casos, administrar usuarios o cambiar estados."],
               ["ANALISTA", "Ver todas las transacciones de usuarios USUARIO; editar cuentas; aprobar, rechazar o eliminar movimientos; resolver casos.", "Administrar usuarios, roles o permisos."],
               ["ADMINISTRADOR", "Acceder a todos los paneles; gestionar usuarios, roles, permisos, asignaciones y overrides.", "Eliminar o modificar el rol ADMINISTRADOR o los permisos base (protegidos por triggers)."]],
              widths=[3.0, 8.2, 5.2], font_size=8.5)
    h3(doc, "4.1.1 Inicio de sesión y selección de panel")
    numbered(doc, [
        "Abre la aplicación en la URL del servicio. Si no tienes sesión, verás la pantalla de login.",
        "Ingresa tu usuario o email y tu contraseña. Si son correctos, se guarda el JWT y se cargan tus permisos.",
        "En el selector de paneles verás solo los paneles disponibles. Los paneles sin permiso aparecen bloqueados.",
        "Elige un panel. El sidebar muestra los módulos permitidos y la topbar muestra tu nombre y correo.",
        "Usa el botón «Cambiar de panel» para volver al selector, el icono de tema para alternar claro/oscuro y el icono de salida para cerrar sesión.",
    ])
    h3(doc, "4.1.2 Gestión de cuentas")
    numbered(doc, [
        "Entra al panel Cuentas y abre el módulo Cuentas.",
        "Pulsa «Nueva cuenta», elige el titular (si eres privilegiado) y el tipo AHORRO, CORRIENTE o EMPRESARIAL.",
        "Deja el número vacío para generarlo automáticamente o ingresa uno único.",
        "Guarda. La cuenta aparece en la tabla con su saldo y estado.",
        "Para editar, usa la acción de la fila. Para desactivar, usa el interruptor de estado si tienes CAMBIAR_ESTADO_CUENTAS.",
        "No se puede eliminar una cuenta con movimientos: el sistema la conserva para no romper el historial.",
    ])
    h3(doc, "4.1.3 Registro de movimientos")
    numbered(doc, [
        "Entra al panel Transacciones y abre Movimientos.",
        "Pulsa «Nuevo movimiento» y elige el tipo: depósito, retiro, transferencia o pago.",
        "Para depósito o retiro, confirma tu contraseña; la operación se aprueba al instante.",
        "Para transferencia o pago, selecciona cuenta origen y destino (o escribe el número de destino) e ingresa el monto.",
        "Si cumple R1–R4 y hay saldo, se aprueba y los saldos se actualizan. Si no, queda PENDIENTE y se abre un caso.",
        "El listado permite filtrar por estado y tipo; el detalle muestra la evaluación de cada regla.",
    ])
    h3(doc, "4.1.4 Resolución de casos")
    numbered(doc, [
        "Entra al panel Analista y abre Casos.",
        "Revisa el número de caso, las cuentas, el monto y el estado de las reglas.",
        "Abre el movimiento y elige aprobar, rechazar, editar o eliminar según el permiso RESOLVER_CASO.",
        "Al aprobar se aplican los saldos; al rechazar o eliminar una operación aprobada se revierten.",
        "El caso se sincroniza a RESUELTO o RECHAZADO y desaparece de la bandeja de abiertos.",
    ])
    h3(doc, "4.1.5 Administración")
    numbered(doc, [
        "En el panel Administración, usa Usuarios para crear, editar, activar o eliminar cuentas de usuario.",
        "En Roles, crea roles y asígnales permisos. El rol ADMINISTRADOR no se puede renombrar, desactivar ni eliminar.",
        "En Permisos, consulta el catálogo. Los permisos base están protegidos por triggers.",
        "En la ficha del usuario, asigna roles y, si hace falta, concede o deniega permisos individuales.",
        "Cierra sesión al terminar. La sesión también se cierra automáticamente al expirar el token.",
    ])
    note(doc, "Buenas prácticas para el usuario",
         "No compartas tu contraseña ni el token. Usa el botón de salida en equipos compartidos. Si una "
         "operación queda pendiente, revisa el detalle de reglas antes de volver a intentarla.")

    h2(doc, "4.2 Manual de instalación")
    h3(doc, "4.2.1 Requisitos de hardware")
    add_table(doc, ["Entorno", "Mínimo", "Recomendado"],
              [["Desarrollo", "4 núcleos, 8 GB RAM, 10 GB libres.", "8 núcleos, 16 GB RAM, SSD."],
               ["Producción (Render Free)", "Instancia gratuita de 512 MB RAM.", "Plan pago con más memoria y CPU."],
               ["Base de datos", "MySQL 8 local o remoto.", "MySQL 8 con backups y réplica."]],
              widths=[4.4, 6.4, 5.6], font_size=9)
    h3(doc, "4.2.2 Requisitos de software")
    add_table(doc, ["Software", "Versión / nota"],
              [["Java JDK", "21 (el proyecto usa Java 21)."],
               ["Node.js", "22 o superior; npm 11."],
               ["MySQL", "8.x con usuario y base creados."],
               ["Docker", "24 o superior (opcional para despliegue)."],
               ["Git", "Para clonar el repositorio."],
               ["Navegador", "Chrome, Edge, Firefox o Safari actualizado."]],
              widths=[4.4, 12.0], font_size=9)
    h3(doc, "4.2.3 Requisitos de contenido")
    bullets(doc, [
        "Repositorio completo con backend, frontend, Dockerfile y render.yaml.",
        "Archivo backend/schema.sql para crear la base y los datos iniciales.",
        "Archivo backend/.env a partir de backend/.env.example (no se versiona).",
        "Logo y assets en frontend/public; el build los copia a dist/frontend/browser.",
        "Credenciales del administrador semilla: USER_ADMIN, USER_PASSWORD, USER_EMAIL y USER_ROL.",
        "Si se despliega en Render: variables DB_*, JWT_SECRET, JWT_ISSUER, CORS_ALLOWED_ORIGINS y USER_*.",
    ])
    h3(doc, "4.2.4 Manual de instalación paso a paso")
    p(doc, "1) Clonar el repositorio y entrar a la carpeta raíz.")
    code(doc, "git clone <url-del-repositorio>\ncd \"Sistema Bancario\"")
    p(doc, "2) Crear la base de datos y cargar el esquema.")
    code(doc, "mysql -u root -p < backend/schema.sql")
    p(doc, "El esquema crea la base sistema_bancario, las 10 tablas, las vistas, los triggers y los "
           "datos iniciales. Si usas otro nombre de base, actualiza DB_NAME en backend/.env.")
    p(doc, "3) Configurar las variables del backend.")
    code(doc, "cp backend/.env.example backend/.env\n# Edita backend/.env con DB_HOST, DB_PORT, DB_NAME,\n# DB_USER, DB_PASSWORD, JWT_SECRET (>= 32 caracteres),\n# JWT_ISSUER, CORS_ALLOWED_ORIGINS y USER_*.")
    p(doc, "4) Arrancar el backend.")
    code(doc, "cd backend\n./mvnw spring-boot:run\n# API: http://localhost:2003/api\n# Health: http://localhost:2003/api/health")
    p(doc, "5) Arrancar el frontend en otra terminal.")
    code(doc, "cd frontend\nnpm install\nnpm start\n# SPA: http://localhost:4200")
    p(doc, "6) Verificar el acceso.")
    code(doc, "curl -i http://localhost:2003/api/health\n# Debe responder 204\n\ncurl -s -X POST http://localhost:2003/api/auth/login \\\n  -H 'Content-Type: application/json' \\\n  -d '{\"usuario\":\"<usuario>\",\"contrasena\":\"<clave>\"}'\n# Debe responder 200 con token y permisos")
    p(doc, "7) Despliegue con Docker (opcional).")
    code(doc, "docker build -t sistema-bancario .\ndocker run --rm -p 10000:10000 --env-file backend/.env sistema-bancario\n# SPA en http://localhost:10000; /api se proxifica al backend interno.")
    p(doc, "8) Despliegue en Render.")
    numbered(doc, [
        "Sube el repositorio a GitHub o GitLab.",
        "En Render, crea un Blueprint y selecciona el repositorio; Render leerá render.yaml.",
        "Completa las variables marcadas con sync: false.",
        "Espera el health check /api/health y abre la URL del servicio.",
    ])
    note(doc, "Seguridad en la instalación",
         "No subas backend/.env al repositorio. JWT_SECRET debe tener al menos 32 caracteres. En "
         "producción, configura CORS_ALLOWED_ORIGINS con el dominio real y usa HTTPS. El plan gratuito "
         "de Render suspende el servicio tras 15 minutos de inactividad.")

    h3(doc, "4.2.5 Verificación de la instalación")
    add_table(doc, ["Comprobación", "Comando / ruta", "Resultado observado"],
              [["Build frontend", "npm run build", "Exit 0; bundle inicial 323,48 kB."],
               ["Pruebas backend", "./mvnw test", "Exit 0; contexto Spring y MySQL OK."],
               ["Health", "GET /api/health", "204."],
               ["Login", "POST /api/auth/login", "200; token y 29 permisos."],
               ["Sesión", "GET /api/auth/sesion", "200."],
               ["Sin token", "GET /api/cuentas", "401."],
               ["CORS externo", "OPTIONS /api/cuentas", "403."],
               ["Módulos", "GET /cuentas, /transacciones, /analista/casos", "200."],
               ["Base de datos", "10 tablas, 2 vistas, 6 triggers", "Conteos coinciden."]],
              widths=[4.4, 7.2, 4.8], font_size=8.5)
    h3(doc, "4.2.6 Solución de problemas")
    add_table(doc, ["Síntoma", "Causa probable", "Solución"],
              [["401 en todas las rutas", "Token vencido o JWT_SECRET distinto.", "Vuelve a iniciar sesión y revisa JWT_SECRET."],
               ["CORS bloqueado", "Origen no listado en CORS_ALLOWED_ORIGINS.", "Agrega el origen exacto (esquema, host y puerto)."],
               ["No conecta a MySQL", "DB_HOST/DB_USER/DB_PASSWORD incorrectos.", "Revisa backend/.env y que MySQL escuche en el puerto."],
               ["El backend no arranca", "JWT_SECRET corto o puerto 2003 ocupado.", "Usa >= 32 caracteres y libera el puerto."],
               ["El SPA no encuentra /api", "nginx no está proxificando o el backend no está arriba.", "Verifica BACKEND_PORT y los logs de supervisord."],
               ["Usuario semilla ausente", "USER_* incompletos.", "Configura USER_ADMIN, USER_PASSWORD y USER_EMAIL; reinicia."]],
              widths=[4.6, 5.8, 6.0], font_size=8.5)

    h2(doc, "4.3 Mantenimiento")
    p(doc, "El mantenimiento se organiza en cuatro frentes: seguridad, datos, operación y evolución "
           "funcional. Las tareas siguientes son recomendaciones para un entorno real; el prototipo "
           "académico no las ejecuta automáticamente.")
    add_table(doc, ["Frente", "Tarea", "Frecuencia"],
              [["Seguridad", "Rotar JWT_SECRET y credenciales; revisar dependencias y permisos.", "Trimestral / ante incidente."],
               ["Datos", "Respaldo lógico de MySQL y prueba de restauración.", "Diario / mensual."],
               ["Operación", "Revisar logs, health check y uso de recursos.", "Semanal."],
               ["Rendimiento", "Analizar consultas lentas e índices de transacciones.", "Mensual."],
               ["Funcional", "Revisar reglas, catálogo de permisos y flujos de casos.", "Por release."],
               ["Documentación", "Actualizar manuales, diagramas y diccionario.", "Por release."]],
              widths=[3.2, 9.6, 3.6], font_size=8.5)
    p(doc, "Respaldo sugerido:")
    code(doc, "mysqldump -u <usuario> -p sistema_bancario > respaldo_$(date +%F).sql\n# Restauración:\nmysql -u <usuario> -p sistema_bancario < respaldo_2026-10-25.sql")
    note(doc, "Continuidad",
         "En producción se recomienda una base gestionada con backups automáticos, un gestor de "
         "secretos y un pipeline CI/CD que ejecute build, pruebas y análisis de dependencias antes "
         "de desplegar.")


# ------------------------------------------------------------------ cierre
def closing(doc: Document) -> None:
    h1(doc, "5. CONCLUSIONES")
    p(doc, "El proyecto cumplió el objetivo general: entregar una aplicación web funcional para "
           "gestionar cuentas y movimientos bancarios con autenticación, autorización por permisos, "
           "reglas de aprobación y resolución de casos. La separación en capas permitió mantener el "
           "dominio independiente de la interfaz y concentrar las decisiones críticas en servicios "
           "transaccionales.")
    bullets(doc, [
        "La unificación del shell de paneles eliminó la duplicación de sidebar, topbar, tema y logout; "
        "los cuatro paneles comparten una sola implementación.",
        "El modelo RBAC con overrides y la resolución deny-wins ofrecen un control de acceso expresivo, "
        "probado en la API y reflejado en el menú.",
        "El motor R1–R4 hace explícita la decisión de aprobar o derivar una operación; el analista recibe "
        "el detalle de cada regla, no solo un estado.",
        "La aplicación de saldos con bloqueo pesimista y la reversión al rechazar/eliminar protegen la "
        "consistencia contable dentro del alcance del prototipo.",
        "La verificación del 25/10/2026 dejó evidencia reproducible: build, pruebas, endpoints, seguridad "
        "y estado de la base de datos.",
        "El despliegue en un solo contenedor con nginx + Spring Boot + Angular simplifica la puesta en "
        "marcha y elimina CORS en producción.",
    ])
    p(doc, "Como toda solución académica, el sistema tiene límites claros: no procesa dinero real, no "
           "incluye MFA ni revocación de tokens, no tiene una suite E2E automatizada y no implementa "
           "requisitos regulatorios. Esos límites no invalidan el valor del ejercicio: el proyecto "
           "demuestra criterio de arquitectura, seguridad, modelado de datos y verificación.")

    h1(doc, "6. RECOMENDACIONES")
    numbered(doc, [
        "Agregar autenticación multifactor (TOTP) y recuperación de contraseña por correo con tokens de un solo uso.",
        "Implementar refresh tokens con rotación, revocación y lista de sesiones activas.",
        "Automatizar pruebas E2E con Playwright para los flujos de login, cuentas, transferencias y resolución de casos.",
        "Agregar pruebas de integración con Testcontainers/MySQL y pruebas de contrato para la API.",
        "Incorporar idempotency keys en la creación de movimientos para evitar duplicados por reintentos.",
        "Externalizar las reglas R1–R4 a una tabla configurable o a un motor de reglas, con versionado y auditoría.",
        "Agregar notificaciones (correo o en la app) cuando una operación queda pendiente o un caso se resuelve.",
        "Fortalecer la observabilidad: métricas de negocio, trazas distribuidas, alertas y dashboards operativos.",
        "Configurar backups automáticos, réplica de lectura y pruebas periódicas de restauración.",
        "Revisar accesibilidad (WCAG 2.2 AA), internacionalización y multi-moneda antes de un uso real.",
        "Documentar y automatizar el pipeline CI/CD con análisis de dependencias y escaneo de secretos.",
        "Definir políticas de retención y protección de datos personales antes de operar con usuarios reales.",
    ])

    h1(doc, "REFERENCIAS")
    refs = [
        "Angular. (2026). Angular documentation. https://angular.dev/",
        "Spring. (2026). Spring Boot reference documentation. https://docs.spring.io/spring-boot/",
        "Oracle. (2026). MySQL 8.0 reference manual. https://dev.mysql.com/doc/refman/8.0/en/",
        "IETF. (2015). RFC 7519: JSON Web Token (JWT). https://www.rfc-editor.org/rfc/rfc7519",
        "OWASP. (2025). OWASP Application Security Verification Standard. https://owasp.org/www-project-application-security-verification-standard/",
        "NIST. (2017). NIST SP 800-63B: Digital Identity Guidelines. https://pages.nist.gov/800-63-3/sp800-63b.html",
        "Docker. (2026). Docker documentation. https://docs.docker.com/",
        "Render. (2026). Render documentation. https://render.com/docs",
    ]
    for ref in refs:
        par = doc.add_paragraph(ref)
        par.paragraph_format.left_indent = Cm(0.8)
        par.paragraph_format.first_line_indent = Cm(-0.8)
        par.paragraph_format.space_after = Pt(4)
        par.paragraph_format.line_spacing = 1.05

    h1(doc, "ANEXOS")
    h2(doc, "Anexo A. Matriz de permisos por rol")
    p(doc, "La matriz refleja los permisos base asignados por backend/schema.sql. El rol "
           "ADMINISTRADOR recibe todos los permisos y está protegido por triggers; USUARIO y ANALISTA "
           "tienen los permisos operativos indicados.")
    admin = {"ASIGNAR_ROLES", "VER_ROLES", "CREAR_ROLES", "MODIFICAR_ROLES", "ELIMINAR_ROLES",
             "ASIGNAR_PERMISOS", "VER_PERMISOS", "CREAR_PERMISOS", "MODIFICAR_PERMISOS",
             "ELIMINAR_PERMISOS", "VER_USUARIOS", "CREAR_USUARIOS", "MODIFICAR_USUARIOS",
             "ELIMINAR_USUARIOS", "PANEL_ADMIN", "DASHBOARD_ADMIN", "PANEL_CUENTAS",
             "DASHBOARD_CUENTAS", "VER_CUENTAS", "CREAR_CUENTAS", "MODIFICAR_CUENTAS",
             "ELIMINAR_CUENTAS", "CAMBIAR_ESTADO_CUENTAS", "PANEL_TRANSACCIONES",
             "DASHBOARD_TRANSACCIONES", "VER_TRANSACCIONES", "CREAR_TRANSACCIONES",
             "PANEL_ANALISTA", "RESOLVER_CASO"}
    usuario = {"PANEL_CUENTAS", "DASHBOARD_CUENTAS", "VER_CUENTAS", "CREAR_CUENTAS",
               "MODIFICAR_CUENTAS", "ELIMINAR_CUENTAS", "PANEL_TRANSACCIONES",
               "DASHBOARD_TRANSACCIONES", "VER_TRANSACCIONES", "CREAR_TRANSACCIONES"}
    analista = {"PANEL_ANALISTA", "PANEL_TRANSACCIONES", "DASHBOARD_TRANSACCIONES",
                "VER_TRANSACCIONES", "RESOLVER_CASO", "VER_CUENTAS", "MODIFICAR_CUENTAS",
                "ELIMINAR_CUENTAS", "CAMBIAR_ESTADO_CUENTAS"}
    perm_names = sorted(admin | usuario | analista)
    rows = []
    for name in perm_names:
        rows.append([name,
                     "Sí" if name in admin else "—",
                     "Sí" if name in usuario else "—",
                     "Sí" if name in analista else "—"])
    add_table(doc, ["Permiso", "ADMINISTRADOR", "USUARIO", "ANALISTA"], rows,
              widths=[7.4, 3.0, 3.0, 3.0], font_size=8, header_size=8, align_center=True)

    h2(doc, "Anexo B. Endpoints principales")
    p(doc, "La API expone 60 mappings REST. La tabla resume los grupos y el permiso que exige cada "
           "operación; todas las rutas, salvo login, registro y health, requieren Bearer token.")
    add_table(doc, ["Método", "Ruta", "Permiso / acceso", "Uso"],
              [["GET", "/api/health", "Público", "Health check."],
               ["POST", "/api/auth/login", "Público", "Iniciar sesión."],
               ["POST", "/api/auth/registro", "Público", "Autorregistro con rol USUARIO."],
               ["GET", "/api/auth/sesion", "Autenticado", "Usuario y permisos actuales."],
               ["PUT", "/api/auth/contrasena", "Autenticado", "Cambiar la propia contraseña."],
               ["GET/POST", "/api/usuarios", "VER/CREAR_USUARIOS", "Listar y crear usuarios."],
               ["GET", "/api/usuarios/resumen", "VER_USUARIOS + VER_ROLES + VER_PERMISOS", "Roles y permisos por usuario."],
               ["PUT/DELETE", "/api/usuarios/{id}", "MODIFICAR/ELIMINAR_USUARIOS", "Editar o eliminar."],
               ["PATCH", "/api/usuarios/{id}/activo", "MODIFICAR_USUARIOS", "Activar o desactivar."],
               ["GET/POST", "/api/roles", "VER/CREAR_ROLES", "Listar y crear roles."],
               ["PUT/DELETE", "/api/roles/{id}", "MODIFICAR/ELIMINAR_ROLES", "Editar o eliminar roles."],
               ["GET/POST", "/api/permisos", "VER/CREAR_PERMISOS", "Catálogo de permisos."],
               ["GET", "/api/cuentas", "VER_CUENTAS", "Listar cuentas visibles."],
               ["POST", "/api/cuentas", "CREAR_CUENTAS", "Abrir cuenta."],
               ["PUT/DELETE", "/api/cuentas/{id}", "MODIFICAR/ELIMINAR_CUENTAS", "Editar o eliminar."],
               ["PATCH", "/api/cuentas/{id}/activo", "CAMBIAR_ESTADO_CUENTAS", "Activar o desactivar."],
               ["GET", "/api/cuentas/dashboard", "DASHBOARD_CUENTAS", "KPIs de cuentas."],
               ["GET", "/api/transacciones", "VER_TRANSACCIONES", "Listar movimientos."],
               ["POST", "/api/transacciones", "CREAR_TRANSACCIONES", "Registrar movimiento."],
               ["PUT/DELETE", "/api/transacciones/{id}", "RESOLVER_CASO", "Resolver o eliminar."],
               ["GET", "/api/transacciones/dashboard", "DASHBOARD_TRANSACCIONES", "KPIs de movimientos."],
               ["GET", "/api/analista/transacciones", "RESOLVER_CASO", "Bandeja global del analista."],
               ["GET", "/api/analista/casos", "RESOLVER_CASO", "Casos pendientes."],
               ["GET", "/api/analista/dashboard", "RESOLVER_CASO", "KPIs del analista."]],
              widths=[2.3, 5.6, 5.2, 3.5], font_size=7.5, header_size=7.5)

    h2(doc, "Anexo C. Evidencia de verificación")
    add_table(doc, ["Comprobación", "Resultado"],
              [["Fecha de verificación", "25 de octubre de 2026."],
               ["Frontend", "Build exit 0; bundle inicial 323,48 kB (89,23 kB transferidos)."],
               ["Backend", "mvnw test exit 0; contexto Spring y MySQL cargados."],
               ["API pública", "Health 204; login 200; registro disponible."],
               ["API protegida", "Sesión, cuentas, transacciones y analista 200 con token."],
               ["Seguridad", "Sin token 401; token inválido 401; CORS externo 403."],
               ["Validación", "POST /transacciones vacío 400."],
               ["Base de datos", "10 tablas, 2 vistas, 6 triggers; 4 usuarios, 3 roles, 29 permisos, 22 cuentas, 8 movimientos, 6 casos."],
               ["Código", "123 archivos Java (6.732 líneas); 76 TS (7.080 líneas); 2.956 líneas HTML; 2.886 SCSS; 60 mappings."],
               ["Pendiente", "Suite E2E automatizada y prueba de carga; no se reportan como aprobadas."]],
              widths=[4.6, 11.8], font_size=8.5)


def main() -> None:
    doc = Document()
    setup(doc)
    doc.core_properties.title = "Sistema Bancario — Documentación del proyecto"
    doc.core_properties.subject = "Planificación, diseño, desarrollo, pruebas y despliegue"
    doc.core_properties.author = "Equipo de desarrollo del Sistema Bancario"
    doc.core_properties.keywords = "Angular, Spring Boot, MySQL, JWT, RBAC, sistema bancario"
    cover(doc)
    table_of_contents(doc)
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    closing(doc)
    doc.save(OUT)
    print("wrote", OUT)
    print("tables parsed", len(TABLES), [t["name"] for t in TABLES])


if __name__ == "__main__":
    main()
