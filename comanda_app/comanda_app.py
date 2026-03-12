"""
comanda_app/comanda_app.py
Página principal del dashboard de comandas.
"""

import reflex as rx
from .state import ComandaState
from .components import (
    stat_card,
    tabla_comandas,
    zona_upload,
    toast_notificacion,
    COLORS,
    PIE_COLORS,
)


# ── Sección: Header ────────────────────────────────────────────────────────────

def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading(
                    ComandaState.titulo_proyecto,
                    size="7",
                    color="white",
                    font_weight="800",
                ),
                rx.text(
                    "Sistema de Gestión de Comandas v3.0",
                    color="rgba(255,255,255,0.7)",
                    font_size="0.88em",
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.badge(
                "● EN LÍNEA",
                color_scheme="green",
                variant="soft",
                font_size="0.75em",
            ),
            width="100%",
            align="center",
        ),
        bg=COLORS["primary"],
        padding="24px 32px",
        width="100%",
    )


# ── Sección: Cards de stats ────────────────────────────────────────────────────

def cards_stats() -> rx.Component:
    return rx.hstack(
        stat_card("Comandas",    ComandaState.total_comandas,  COLORS["card_blue"],   "clipboard-list"),
        stat_card("Total PAX",   ComandaState.total_alimentos, COLORS["card_green"],  "users"),
        stat_card("Morteras",    ComandaState.total_mortera,   COLORS["card_purple"], "soup"),
        stat_card("Viandas",     ComandaState.total_viandas,   COLORS["card_orange"], "utensils"),
        spacing="3",
        width="100%",
        wrap="wrap",
    )


# ── Gráfico de pastel (SVG manual) ────────────────────────────────────────────

def pie_chart_svg() -> rx.Component:
    """
    Gráfico de torta simple generado con Recharts PieChart.
    """
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            rx.recharts.cell(
                *[
                    rx.recharts.cell(fill=PIE_COLORS[i % len(PIE_COLORS)])
                    for i in range(8)
                ]
            ),
            data=ComandaState.por_destino_grafico,
            data_key="pax",
            name_key="destino",
            cx="50%",
            cy="50%",
            outer_radius=100,
            label=True,
        ),
        rx.recharts.legend(),
        rx.recharts.tooltip(),
        width="100%",
        height=280,
    )


# ── Panel: Lista de items de stat ─────────────────────────────────────────────

def lista_item(etiqueta: str, valor: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.text(etiqueta, font_size="0.82em", flex="1", color=COLORS["text"]),
        rx.badge(valor, color_scheme="blue", variant="soft"),
        width="100%",
        justify="between",
        padding_y="4px",
        border_bottom=f"1px solid {COLORS['border']}",
    )


def panel_lista(titulo: str, items: rx.Var, key_label: str, key_value: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(titulo, font_weight="700", font_size="1em", color=COLORS["text"]),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        items,
                        lambda item: lista_item(item[key_label], item[key_value]),
                    ),
                    width="100%",
                    spacing="0",
                ),
                height="220px",
                width="100%",
            ),
            width="100%",
            spacing="2",
        ),
        bg=COLORS["white"],
        border_radius="12px",
        padding="16px",
        border=f"1px solid {COLORS['border']}",
        flex="1",
        min_width="200px",
        box_shadow="0 1px 4px rgba(0,0,0,0.07)",
    )


# ── Sección: Gráficas y listas ────────────────────────────────────────────────

def seccion_graficas() -> rx.Component:
    return rx.hstack(
        # Lista destinos
        panel_lista("📍 PAX por Destino", ComandaState.por_destino, "destino", "pax"),

        # Lista compañías
        panel_lista("🏢 PAX por Compañía", ComandaState.por_compania, "compania", "pax"),

        # Gráfico
        rx.box(
            rx.vstack(
                rx.text("📊 Distribución por Destino", font_weight="700", font_size="1em"),
                pie_chart_svg(),
                width="100%",
                spacing="2",
            ),
            bg=COLORS["white"],
            border_radius="12px",
            padding="16px",
            border=f"1px solid {COLORS['border']}",
            flex="1.5",
            min_width="280px",
            box_shadow="0 1px 4px rgba(0,0,0,0.07)",
        ),
        spacing="4",
        width="100%",
        align_items="start",
        wrap="wrap",
    )


# ── Sección: Transportes ──────────────────────────────────────────────────────

def seccion_transportes() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("🚁 PAX por Transporte", font_weight="700", font_size="1em"),
            rx.hstack(
                rx.foreach(
                    ComandaState.por_transporte,
                    lambda t: rx.box(
                        rx.vstack(
                            rx.text(t["transporte"], font_weight="600", font_size="0.9em"),
                            rx.text(t["pax"], font_size="1.6em", font_weight="800", color=COLORS["primary"]),
                            rx.text(t["porcentaje"].to(str) + "%", color=COLORS["subtext"], font_size="0.78em"),
                            align="center",
                            spacing="0",
                        ),
                        bg="#EFF6FF",
                        border_radius="10px",
                        padding="12px 24px",
                        border=f"1px solid {COLORS['border']}",
                    ),
                ),
                spacing="3",
                wrap="wrap",
            ),
            width="100%",
            spacing="3",
        ),
        bg=COLORS["white"],
        border_radius="12px",
        padding="16px",
        border=f"1px solid {COLORS['border']}",
        width="100%",
        box_shadow="0 1px 4px rgba(0,0,0,0.07)",
    )


# ── Sección: Tabla de comandas ────────────────────────────────────────────────

def seccion_tabla() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("📋 Gestión de Comandas", size="4"),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        rx.icon("bar-chart-2", size=15),
                        "Reporte Estadístico",
                        on_click=ComandaState.generar_reporte,
                        variant="outline",
                        color_scheme="blue",
                        size="2",
                    ),
                    rx.button(
                        rx.icon("file-text", size=15),
                        "Todas las Comandas",
                        on_click=ComandaState.generar_todas,
                        color_scheme="blue",
                        size="2",
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            # Buscador
            rx.input(
                rx.input.slot(rx.icon("search", size=16)),
                placeholder="Buscar por folio, destino o compañía...",
                value=ComandaState.search_term,
                on_change=ComandaState.set_search,
                width="100%",
                border_radius="8px",
            ),
            tabla_comandas(),
            rx.text(
                rx.el.span(ComandaState.filas_tabla.length()),
                " resultados encontrados",
                color=COLORS["subtext"],
                font_size="0.8em",
            ),
            width="100%",
            spacing="4",
        ),
        bg=COLORS["white"],
        border_radius="12px",
        padding="20px",
        border=f"1px solid {COLORS['border']}",
        width="100%",
        box_shadow="0 1px 4px rgba(0,0,0,0.07)",
    )


# ── Dashboard (visible después de cargar datos) ────────────────────────────────

def dashboard() -> rx.Component:
    return rx.vstack(
        cards_stats(),
        seccion_graficas(),
        seccion_transportes(),
        seccion_tabla(),
        width="100%",
        spacing="5",
    )


# ── Zona inicial de carga ─────────────────────────────────────────────────────

def zona_inicial() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("file-search", size=64, color=COLORS["primary"]),
            rx.heading("Cargar Reporte PDF", size="5", color=COLORS["text"]),
            rx.text(
                "Selecciona o arrastra un PDF de comandas PEMEX para comenzar.",
                color=COLORS["subtext"],
                text_align="center",
                max_width="420px",
            ),
            zona_upload(),
            align="center",
            spacing="5",
        ),
        bg=COLORS["white"],
        border_radius="16px",
        border=f"1px solid {COLORS['border']}",
        padding="48px 32px",
        width="100%",
        box_shadow="0 2px 12px rgba(0,0,0,0.08)",
    )


# ── Página principal ──────────────────────────────────────────────────────────

def index() -> rx.Component:
    return rx.vstack(
        header(),

        # Contenido principal
        rx.box(
            rx.vstack(
                # Botón de carga siempre visible cuando hay datos
                rx.cond(
                    ComandaState.tiene_datos,
                    rx.hstack(
                        rx.text(
                            "Cargar otro PDF:",
                            color=COLORS["subtext"],
                            font_size="0.85em",
                        ),
                        rx.upload(
                            rx.button(
                                rx.icon("refresh-cw", size=14),
                                "Reemplazar PDF",
                                variant="outline",
                                size="2",
                                color_scheme="blue",
                            ),
                            id="pdf_reload",
                            accept={".pdf": ["application/pdf"]},
                            max_files=1,
                        ),
                        rx.button(
                            "Procesar",
                            on_click=ComandaState.handle_upload(
                                rx.upload_files(upload_id="pdf_reload")
                            ),
                            size="2",
                            color_scheme="blue",
                            loading=ComandaState.loading,
                        ),
                        align="center",
                        spacing="2",
                        justify="end",
                        width="100%",
                    ),
                    rx.fragment(),
                ),

                # Zona de carga inicial o dashboard
                rx.cond(
                    ComandaState.dashboard_visible,
                    dashboard(),
                    zona_inicial(),
                ),
                width="100%",
                spacing="4",
            ),
            padding="24px",
            max_width="1400px",
            width="100%",
            margin="0 auto",
        ),

        # Footer
        rx.box(
            rx.text(
                "Angel Valenzuela Romero © 2026",
                color=COLORS["subtext"],
                font_size="0.78em",
                text_align="center",
                font_style="italic",
            ),
            width="100%",
            padding="16px",
            border_top=f"1px solid {COLORS['border']}",
        ),

        # Toast de notificaciones
        toast_notificacion(),

        width="100%",
        min_height="100vh",
        bg=COLORS["bg"],
        spacing="0",
        align_items="stretch",
    )


# ── App ───────────────────────────────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        radius="medium",
    ),
    stylesheets=[],
)

app.add_page(
    index,
    route="/",
    title="Dashboard Comandas v3.0 — PEMEX",
    description="Sistema de Gestión de Comandas Pemex",
)
