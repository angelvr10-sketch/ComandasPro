"""
comanda_app/components.py
Componentes reutilizables de UI.
Equivalente a las funciones helper de Flet (crear_card, etc.)
"""

import reflex as rx
from .state import ComandaState


# ── Colores de la paleta ──────────────────────────────────────────────────────

COLORS = {
    "primary":    "#1565C0",   # azul oscuro (header)
    "card_blue":  "#1976D2",
    "card_green": "#2E7D32",
    "card_purple": "#6A1B9A",
    "card_orange": "#E65100",
    "bg":         "#F5F5F5",
    "white":      "#FFFFFF",
    "text":       "#212121",
    "subtext":    "#757575",
    "border":     "#E0E0E0",
    "success":    "#2E7D32",
    "error":      "#C62828",
    "info":       "#1565C0",
}

PIE_COLORS = [
    "#64B5F6", "#81C784", "#FFB74D", "#CE93D8",
    "#EF9A9A", "#80DEEA", "#FFF176", "#BCAAA4",
]


# ── Stat card ─────────────────────────────────────────────────────────────────

def stat_card(label: str, value: rx.Var, color: str, icon: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon(icon, color="white", size=22),
            rx.text(value, color="white", font_size="2em", font_weight="bold"),
            rx.text(label, color="rgba(255,255,255,0.85)", font_size="0.78em"),
            align="center",
            spacing="1",
        ),
        bg=color,
        border_radius="12px",
        padding="16px 12px",
        flex="1",
        min_width="130px",
        box_shadow="0 2px 8px rgba(0,0,0,0.15)",
    )


# ── Tabla de comandas ─────────────────────────────────────────────────────────

def tabla_row(fila: Dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.badge(fila["comanda"], color_scheme="blue", variant="soft"),
        ),
        rx.table.cell(fila["horario"]),
        rx.table.cell(fila["compania"]),
        rx.table.cell(fila["destino"]),
        rx.table.cell(
            rx.badge(fila["pax"], color_scheme="green"),
            text_align="center",
        ),
        rx.table.cell(
            rx.badge(
                fila["transporte"],
                color_scheme=rx.cond(
                    fila["transporte"] == "AEREO", "purple",
                    rx.cond(fila["transporte"] == "GANGWAY", "orange", "blue")
                ),
                variant="soft",
            ),
        ),
        rx.table.cell(
            rx.icon_button(
                rx.icon("file-text", size=16),
                on_click=ComandaState.generar_pdf_individual(fila["comanda"]),
                size="1",
                variant="ghost",
                color_scheme="red",
                title="Generar PDF de esta comanda",
            ),
        ),
        _hover={"bg": "#F3F4F6"},
    )


def tabla_comandas() -> rx.Component:
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[
                        rx.table.column_header_cell(h, font_weight="700", color=COLORS["primary"])
                        for h in ["Folio", "Horario", "Compañía", "Destino", "PAX", "Transporte", "PDF"]
                    ]
                ),
                bg="#EFF6FF",
            ),
            rx.table.body(
                rx.foreach(ComandaState.filas_tabla, tabla_row),
            ),
            width="100%",
            variant="surface",
        ),
        overflow_x="auto",
        border_radius="8px",
        border=f"1px solid {COLORS['border']}",
    )


# ── Lista de estadísticas ─────────────────────────────────────────────────────

def lista_stat_item(label: str, value: rx.Var, total: rx.Var) -> rx.Component:
    pct = rx.cond(total > 0, (value / total * 100).to(int), 0)
    return rx.box(
        rx.hstack(
            rx.text(label, font_size="0.85em", flex="1", color=COLORS["text"]),
            rx.text(value, font_weight="700", font_size="0.85em"),
            width="100%",
            justify="between",
        ),
        rx.box(
            rx.box(
                width=rx.cond(total > 0, f"{pct}%", "0%"),
                height="4px",
                bg=COLORS["card_blue"],
                border_radius="2px",
                transition="width 0.4s ease",
            ),
            width="100%",
            height="4px",
            bg=COLORS["border"],
            border_radius="2px",
            margin_top="4px",
        ),
        padding="6px 0",
        border_bottom=f"1px solid {COLORS['border']}",
    )


# ── Toast/notificación ────────────────────────────────────────────────────────

def toast_notificacion() -> rx.Component:
    color_map = {
        "success": COLORS["success"],
        "error":   COLORS["error"],
        "info":    COLORS["info"],
    }
    return rx.cond(
        ComandaState.mostrar_mensaje,
        rx.box(
            rx.hstack(
                rx.text(ComandaState.mensaje, color="white", font_size="0.9em", flex="1"),
                rx.icon_button(
                    rx.icon("x", size=14),
                    on_click=ComandaState.cerrar_mensaje,
                    variant="ghost",
                    color="white",
                    size="1",
                ),
                width="100%",
                align="center",
            ),
            position="fixed",
            bottom="24px",
            right="24px",
            bg=COLORS["info"],
            border_radius="10px",
            padding="14px 18px",
            z_index="1000",
            max_width="420px",
            box_shadow="0 4px 20px rgba(0,0,0,0.25)",
        ),
        rx.fragment(),
    )


# ── Zona de carga de PDF ──────────────────────────────────────────────────────

def zona_upload() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.icon("upload-cloud", size=48, color=COLORS["primary"]),
                rx.text(
                    "Arrastra tu PDF aquí o haz clic para seleccionar",
                    color=COLORS["primary"],
                    font_weight="600",
                    font_size="1em",
                    text_align="center",
                ),
                rx.text(
                    "Solo archivos .pdf",
                    color=COLORS["subtext"],
                    font_size="0.8em",
                ),
                align="center",
                spacing="2",
                padding="40px 60px",
            ),
            id="pdf_upload",
            accept={".pdf": ["application/pdf"]},
            max_files=1,
            border=f"2px dashed {COLORS['primary']}",
            border_radius="16px",
            bg="rgba(21,101,192,0.04)",
            cursor="pointer",
            _hover={"bg": "rgba(21,101,192,0.09)"},
            transition="background 0.2s",
        ),
        rx.button(
            rx.icon("file-up", size=16),
            "Procesar PDF",
            on_click=ComandaState.handle_upload(rx.upload_files(upload_id="pdf_upload")),
            color_scheme="blue",
            size="3",
            border_radius="8px",
            loading=ComandaState.loading,
        ),
        align="center",
        spacing="4",
        width="100%",
    )


# Importaciones que se necesitan en los componentes
from typing import Dict
