"""
comanda_app/parser.py
Lógica de negocio: parseo de PDF y generación de comandas en PDF.
Sin dependencias de UI (Flet o Reflex).
"""

from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import re
import math
import os
import platform
from datetime import datetime
from typing import List, Dict, Any, Optional


# ── Patrón de destinos ──────────────────────────────────────────────────────

DESTINO_PATTERN = (
    r'(?:PLATAFORMA\s+CAMPECHE|ORGULLO\s+PETROLERO|'
    r'WEST\s+COURAGEOUS|WEST\s+DEFENDER|WEST\s+INTREPID|'
    r'GRAND\s+CANYON|ARBOL\s+GRANDE|GARZPROM\s+II|'
    r'CAYO\s+ARCAS|TARATUNICH|CB\s+LITORAL|PAPALOAPAN|'
    r'BLUE\s+GIANT|BLUE\s+PIONEER|BARCO\s+LA\s+BAMBA|'
    r'CREST-CENTURION|ENLACE\s+LITORAL|LITORAL\s+TABASCO|'
    r'LITORAL\s+A|CIA\s+C/G|OCH-TAN-A|'
    r'REFORMA\s+PEMEX|CERRO\s+DE\s+LA\s+PEZ|'
    r'ABKATUN|AKAL|ALUX|AYATSIL|BATAB|BOLONTIKU|'
    r'CAAN|CHEEK|CHE|CHIHUAHUA|CHUC|CHUHUK|COESL|COVADONGA|'
    r'EKTAL|EKU|ELT|ESAH|ETKAL|GABINETE|GERSEMI|'
    r'HAYABIL|HERCULES|HOK|HOMOL|IXTAL|'
    r'KAB|KAX|KIX|KU|KUIL|KUKULKAN|LATINA|LTH|'
    r'MALOOB|MANIK|MAY|MULACH|NEPTUNO|NOHOCH|OCH|ONEL|'
    r'PB-LIT|POL|PROTEUS|REBOMBEO|'
    r'SINAN|TEHUANA|TSIMIN|T-SIMIN|TUMUT|TUXPANAPA|'
    r'UECH|XANAB|XIKIN|XUB|XUX|YAXCHE|YUM|ZAAP|ZACATECAS)'
    r'[\w\s\-/\[\]]*?'
)

REGEX_COMANDA = (
    r'(?P<comanda>[A-Z]{3}\d+)\s+'
    r'(?P<horario>\d{2}:\d{2})\s+'
    r'(?P<compania>(?:[\w\.\-]+(?:\s+[\w\.\-]+){0,4}?))\s+'
    rf'(?P<destino>{DESTINO_PATTERN})\s+'
    r'(?P<pax>\d{1,3})\s+'
    r'(?P<transporte>AEREO|GANGWAY|MARÍTIMO|VIUDA)\s+'
    r'(?P<m1>\d{1,3})\s+'
    r'(?P<m2>\d{1,3})'
)


# ── Parser ───────────────────────────────────────────────────────────────────

def parse_pdf(file_path: str) -> tuple[List[Dict[str, Any]], str, str]:
    """
    Parsea un PDF de comandas PEMEX.

    Returns:
        (lista_comandas, fecha_pdf, titulo_proyecto)
    """
    if not file_path:
        return [], "", "REFORMA PEMEX"

    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # Fecha
        fecha_match = re.search(r'(\w+,\s\d{1,2}\sde\s\w+\sde\s\d{4})', text)
        fecha_pdf = (
            fecha_match.group(1).upper()
            if fecha_match
            else datetime.now().strftime("%d DE %B DE %Y").upper()
        )

        # Título del proyecto
        titulo_match = re.search(
            r'(REFORMA\s+PEMEX|CERRO\s+DE\s+LA\s+PEZ)', text, re.IGNORECASE
        )
        titulo_proyecto = titulo_match.group(1).upper() if titulo_match else "REFORMA PEMEX"

        # Comandas
        comandas: List[Dict[str, Any]] = []
        for m in re.finditer(REGEX_COMANDA, text):
            compania = " ".join(m.group("compania").split())
            destino = " ".join(m.group("destino").split())
            context_after = text[m.end(): m.end() + 100].upper()
            comandas.append(
                {
                    "comanda": m.group("comanda"),
                    "horario": m.group("horario"),
                    "compania": compania,
                    "destino": destino,
                    "pax": int(m.group("pax")),
                    "transporte": m.group("transporte"),
                    "menu_1": int(m.group("m1")),
                    "menu_2": int(m.group("m2")),
                    "tipo": "MORTERA" if "MORTERA" in context_after else "VIANDA",
                }
            )

        return comandas, fecha_pdf, titulo_proyecto

    except Exception as e:
        print(f"❌ Error al procesar PDF: {e}")
        import traceback; traceback.print_exc()
        return [], "", "REFORMA PEMEX"


# ── Estadísticas ─────────────────────────────────────────────────────────────

def calcular_estadisticas(comandas: List[Dict]) -> Optional[Dict]:
    if not comandas:
        return None

    stats: Dict[str, Any] = {
        "total_comandas": len(comandas),
        "total_alimentos": sum(c["pax"] for c in comandas),
        "total_mortera": sum(c["pax"] for c in comandas if "MORTERA" in c["tipo"]),
        "por_destino": {},
        "por_destino_grafico": {},
        "por_compania": {},
        "por_transporte": {},
    }

    for c in comandas:
        if c["transporte"] == "AEREO":
            destino_key = "AÉREOS"
            destino_grafico = "AÉREOS"
        else:
            destino_key = f"{c['destino'].upper()} ({c['transporte']})"
            abrev = "G" if c["transporte"] == "GANGWAY" else "M"
            destino_grafico = f"{c['destino'].upper()} ({abrev})"

        stats["por_destino"][destino_key] = stats["por_destino"].get(destino_key, 0) + c["pax"]
        stats["por_destino_grafico"][destino_grafico] = (
            stats["por_destino_grafico"].get(destino_grafico, 0) + c["pax"]
        )
        stats["por_compania"][c["compania"]] = stats["por_compania"].get(c["compania"], 0) + c["pax"]
        stats["por_transporte"][c["transporte"]] = (
            stats["por_transporte"].get(c["transporte"], 0) + c["pax"]
        )

    return stats


# ── Generación de PDFs ────────────────────────────────────────────────────────

def _dibujar_comanda(c: canvas.Canvas, comanda: Dict, fecha_pdf: str, titulo_proyecto: str):
    width, height = letter
    fecha_texto = fecha_pdf or "FECHA NO DISPONIBLE"
    y = height - 40

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, titulo_proyecto)
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, "CONTRATO No. 428224804")
    y -= 18
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(
        width / 2, y,
        f"CONTROL DE ALIMENTOS AL AREA DEL DIA {fecha_texto.upper()}"
    )
    y -= 30
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, y, comanda["comanda"])
    y -= 40

    data = [
        ["DESTINO", "DEPARTAMENTO/COMPAÑÍA", "NO. PERSONAS", "MENU 1", "MENU 2"],
        [
            comanda["destino"], comanda["compania"],
            str(comanda["pax"]), str(comanda["menu_1"]), str(comanda["menu_2"]),
        ],
    ]
    t = Table(data, colWidths=[140, 180, 80, 60, 60])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 45, y - 50)
    y -= 80

    items = [
        ["DESCRIPCION", "CANT"],
        ["PORTA VIANDA", ""], ["MORTERA", ""], ["THERMO MCA. IGLOO 3 LT", ""],
        ["THERMO MCA. IGLOO 19 LT", ""], ["PARA SERVIR ACERO INOX.", ""],
        ["PINZAS PARA ENSALADAS", ""], ["INSERTOS DE AC. INOX.", ""],
        ["TOTAL ARTICULOS", ""],
    ]

    y_tablas = y - 20
    for x_offset, titulo in [(60, "SALIDA"), (330, "DEVOLUCIÓN")]:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_offset, y_tablas, titulo)
        tbl = Table(items, colWidths=[150, 40], rowHeights=22)
        tbl.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        tbl.wrapOn(c, width, height)
        tbl.drawOn(c, x_offset, y_tablas - 210)

    y_f = y_tablas - 270
    col1, col2, line_w, esp = width * 0.28, width * 0.72, 170, 110

    def dib(py, t1, s1, t2, s2):
        c.line(col1 - line_w / 2, py, col1 + line_w / 2, py)
        c.line(col2 - line_w / 2, py, col2 + line_w / 2, py)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(col1, py - 15, t1)
        c.drawCentredString(col2, py - 15, t2)
        c.setFont("Helvetica", 7)
        c.drawCentredString(col1, py - 25, s1)
        c.drawCentredString(col2, py - 25, s2)

    dib(y_f, "NOMBRE Y FIRMA", "ENTREGA ALIMENTOS", "NOMBRE Y FIRMA", "RECIBE ALIMENTOS")
    dib(y_f - esp, "NOMBRE Y FIRMA", "RECIBE UTENSILIOS", "NOMBRE Y FIRMA", "ENTREGA UTENSILIOS")

    c.setFont("Helvetica-Oblique", 6)
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.drawCentredString(width / 2, 20, "Angel Valenzuela Romero © 2026")


def generar_pdf_comanda(comanda: Dict, filename: str, fecha_pdf: str, titulo_proyecto: str) -> str:
    """Genera PDF de una sola comanda. Retorna la ruta del archivo."""
    cv = canvas.Canvas(filename, pagesize=letter)
    _dibujar_comanda(cv, comanda, fecha_pdf, titulo_proyecto)
    cv.save()
    return filename


def generar_todas_pdf(
    comandas: List[Dict], filename: str, fecha_pdf: str, titulo_proyecto: str
) -> str:
    """Genera PDF con todas las comandas. Retorna la ruta del archivo."""
    cv = canvas.Canvas(filename, pagesize=letter)
    for i, cmd in enumerate(sorted(comandas, key=lambda x: x["comanda"])):
        if i > 0:
            cv.showPage()
        _dibujar_comanda(cv, cmd, fecha_pdf, titulo_proyecto)
    cv.save()
    return filename


def generar_reporte_estadistico(
    comandas: List[Dict], filename: str, fecha_pdf: str, titulo_proyecto: str
) -> str:
    """Genera reporte estadístico en PDF. Retorna la ruta del archivo."""
    s = calcular_estadisticas(comandas)
    if not s:
        return ""

    cv = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    y = height - 40
    cv.setFont("Helvetica-Bold", 18)
    cv.drawCentredString(width / 2, y, f"{titulo_proyecto} - REPORTE OPERATIVO")
    y -= 20
    cv.setFont("Helvetica", 10)
    fecha_texto = fecha_pdf or "FECHA NO DISPONIBLE"
    cv.drawCentredString(width / 2, y, f"Fecha del Reporte: {fecha_texto}")
    y -= 30

    # Cards métricas
    card_w, card_h, gap = 120, 70, 15
    total_w = card_w * 4 + gap * 3
    sx = (width - total_w) / 2
    card_y = y - card_h

    card_colors = [
        colors.Color(0.68, 0.85, 0.90), colors.Color(0.68, 0.93, 0.78),
        colors.Color(0.85, 0.75, 0.95), colors.Color(1.00, 0.85, 0.70),
    ]
    card_text_colors = [
        colors.Color(0.20, 0.40, 0.55), colors.Color(0.25, 0.55, 0.35),
        colors.Color(0.45, 0.30, 0.60), colors.Color(0.70, 0.45, 0.20),
    ]
    card_data = [
        ("Comandas", str(s["total_comandas"])),
        ("Total PAX", str(s["total_alimentos"])),
        ("Morteras", str(s["total_mortera"])),
        ("Viandas", str(s["total_alimentos"] - s["total_mortera"])),
    ]

    for i, (title, value) in enumerate(card_data):
        x = sx + i * (card_w + gap)
        cv.setFillColor(card_colors[i])
        cv.roundRect(x, card_y, card_w, card_h, 8, fill=1, stroke=0)
        cv.setFillColor(card_text_colors[i])
        cv.setFont("Helvetica-Bold", 20)
        cv.drawCentredString(x + card_w / 2, card_y + card_h - 38, value)
        cv.setFont("Helvetica", 9)
        cv.drawCentredString(x + card_w / 2, card_y + 12, title)

    y = card_y - 40

    # Gráfico de pastel
    cv.setFillColor(colors.black)
    cv.setFont("Helvetica-Bold", 12)
    cv.drawCentredString(width / 2, y, "Distribución de PAX por Destino y Transporte")
    y -= 20

    pie_cx, pie_cy, pie_r = width / 2, y - 100, 90
    total_pax_dest = sum(s["por_destino_grafico"].values())
    destinos_sorted = sorted(s["por_destino_grafico"].items(), key=lambda x: x[1], reverse=True)

    pie_colors = [
        colors.Color(0.60, 0.80, 0.95), colors.Color(0.60, 0.90, 0.70),
        colors.Color(1.00, 0.80, 0.60), colors.Color(0.90, 0.70, 0.95),
        colors.Color(1.00, 0.70, 0.75), colors.Color(0.70, 0.90, 0.90),
        colors.Color(1.00, 0.95, 0.60), colors.Color(0.95, 0.85, 0.95),
    ]

    start_angle = 90
    for i, (dest, pax) in enumerate(destinos_sorted):
        sweep = (pax / total_pax_dest) * 360
        color = colors.Color(0.75, 0.80, 0.85) if dest == "AÉREOS" else pie_colors[i % len(pie_colors)]
        cv.setFillColor(color)
        path = cv.beginPath()
        path.moveTo(pie_cx, pie_cy)
        n = max(int(sweep), 2)
        for j in range(n + 1):
            angle = math.radians(start_angle - j * sweep / n)
            path.lineTo(pie_cx + pie_r * math.cos(angle), pie_cy + pie_r * math.sin(angle))
        path.close()
        cv.drawPath(path, fill=1, stroke=0)
        mid = math.radians(start_angle - sweep / 2)
        lx = pie_cx + pie_r * 0.65 * math.cos(mid)
        ly = pie_cy + pie_r * 0.65 * math.sin(mid)
        cv.setFillColor(colors.Color(0.2, 0.2, 0.2))
        cv.setFont("Helvetica-Bold", 9)
        cv.drawCentredString(lx, ly, str(pax))
        start_angle -= sweep

    # Leyenda
    lx, ly = pie_cx + pie_r + 30, pie_cy + 60
    cv.setFillColor(colors.black)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawString(lx, ly, "Leyenda:")
    ly -= 12
    for i, (dest, pax) in enumerate(destinos_sorted):
        color = colors.Color(0.75, 0.80, 0.85) if dest == "AÉREOS" else pie_colors[i % len(pie_colors)]
        cv.setFillColor(color)
        cv.rect(lx, ly - 2, 10, 8, fill=1, stroke=0)
        cv.setFillColor(colors.black)
        cv.setFont("Helvetica", 8)
        pct = (pax / total_pax_dest) * 100
        cv.drawString(lx + 14, ly, f"{dest[:25]}: {pax} ({pct:.1f}%)")
        ly -= 11

    y = pie_cy - pie_r - 30

    # Tabla de compañías
    cv.setFillColor(colors.black)
    cv.setFont("Helvetica-Bold", 11)
    cv.drawCentredString(width / 2, y, "Detalle por Compañía")
    y -= 18

    comp_data = [["Compañía", "PAX", "% del Total"]]
    for comp, pax in sorted(s["por_compania"].items(), key=lambda x: x[1], reverse=True):
        pct = (pax / s["total_alimentos"]) * 100
        comp_data.append([comp, str(pax), f"{pct:.1f}%"])

    t_comp = Table(comp_data, colWidths=[280, 70, 90])
    t_comp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.65, 0.78, 0.88)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.Color(0.2, 0.3, 0.4)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.97, 0.98)]),
    ]))
    avail_h = y - 60
    t_comp.wrapOn(cv, width, avail_h)
    tx = (width - 440) / 2
    t_comp.drawOn(cv, tx, y - t_comp._height - 5)

    cv.setFont("Helvetica-Oblique", 7)
    cv.setFillColor(colors.grey)
    cv.drawCentredString(width / 2, 25, "Angel Valenzuela Romero © 2026")
    cv.drawString(50, 25, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    cv.save()
    return filename


def abrir_archivo(path: str):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        pass
