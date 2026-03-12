"""
comanda_app/state.py
Estado global de la aplicación usando Reflex State.
Equivalente a las variables mutables de Flet, pero de forma reactiva.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional

import reflex as rx

from .parser import (
    parse_pdf,
    calcular_estadisticas,
    generar_pdf_comanda,
    generar_todas_pdf,
    generar_reporte_estadistico,
    abrir_archivo,
)


class ComandaState(rx.State):
    # ── Datos cargados ────────────────────────────────────────────────────────
    comandas: List[Dict[str, Any]] = []
    fecha_pdf: str = ""
    titulo_proyecto: str = "REFORMA PEMEX"

    # ── UI ────────────────────────────────────────────────────────────────────
    loading: bool = False
    search_term: str = ""
    dashboard_visible: bool = False

    # Estadísticas (aplanadas para ser serializables por Reflex)
    total_comandas: int = 0
    total_alimentos: int = 0
    total_mortera: int = 0
    total_viandas: int = 0

    por_destino: List[Dict[str, Any]] = []       # [{destino, pax}]
    por_destino_grafico: List[Dict[str, Any]] = []  # [{destino, pax, porcentaje}]
    por_compania: List[Dict[str, Any]] = []      # [{compania, pax, porcentaje}]
    por_transporte: List[Dict[str, Any]] = []    # [{transporte, pax, porcentaje}]

    # Tabla filtrada
    filas_tabla: List[Dict[str, Any]] = []

    # Notificación/toast
    mensaje: str = ""
    mensaje_tipo: str = "info"   # "info" | "success" | "error"
    mostrar_mensaje: bool = False

    # ── Computed vars ─────────────────────────────────────────────────────────
    @rx.var
    def tiene_datos(self) -> bool:
        return len(self.comandas) > 0

    # ── Handlers ──────────────────────────────────────────────────────────────

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la carga de archivos PDF desde el navegador."""
        if not files:
            return

        self.loading = True
        yield

        try:
            file = files[0]
            content = await file.read()

            # Guardar temporalmente en disco para que pypdf pueda leerlo
            suffix = ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            await self._procesar_archivo(tmp_path)

        except Exception as e:
            self._notificar(f"Error al cargar el archivo: {e}", "error")
        finally:
            self.loading = False
            # Limpiar temporal si existe
            try:
                if "tmp_path" in dir():
                    os.unlink(tmp_path)
            except Exception:
                pass

    async def handle_upload_local(self, path: str):
        """Maneja la apertura de archivo desde ruta local (desktop)."""
        if not path:
            return

        self.loading = True
        yield

        try:
            await self._procesar_archivo(path)
        except Exception as e:
            self._notificar(f"Error al procesar el archivo: {e}", "error")
        finally:
            self.loading = False

    async def _procesar_archivo(self, path: str):
        """Parsea el PDF y actualiza el estado."""
        comandas, fecha_pdf, titulo_proyecto = parse_pdf(path)

        if not comandas:
            self._notificar("No se encontraron comandas en el PDF.", "error")
            return

        self.comandas = comandas
        self.fecha_pdf = fecha_pdf
        self.titulo_proyecto = titulo_proyecto

        self._actualizar_estadisticas()
        self._actualizar_tabla(self.search_term)
        self.dashboard_visible = True
        self._notificar(
            f"✅ {len(comandas)} comandas cargadas — Total PAX: {self.total_alimentos}",
            "success",
        )

    def _actualizar_estadisticas(self):
        s = calcular_estadisticas(self.comandas)
        if not s:
            return

        self.total_comandas = s["total_comandas"]
        self.total_alimentos = s["total_alimentos"]
        self.total_mortera = s["total_mortera"]
        self.total_viandas = s["total_alimentos"] - s["total_mortera"]

        self.por_destino = [
            {"destino": d, "pax": v}
            for d, v in s["por_destino"].items()
        ]

        total_pax = s["total_alimentos"] or 1
        self.por_destino_grafico = [
            {
                "destino": d,
                "pax": v,
                "porcentaje": round(v / total_pax * 100, 1),
            }
            for d, v in sorted(s["por_destino_grafico"].items(), key=lambda x: x[1], reverse=True)
        ]

        self.por_compania = [
            {
                "compania": c,
                "pax": v,
                "porcentaje": round(v / total_pax * 100, 1),
            }
            for c, v in sorted(s["por_compania"].items(), key=lambda x: x[1], reverse=True)
        ]

        self.por_transporte = [
            {
                "transporte": t,
                "pax": v,
                "porcentaje": round(v / total_pax * 100, 1),
            }
            for t, v in sorted(s["por_transporte"].items(), key=lambda x: x[1], reverse=True)
        ]

    def _actualizar_tabla(self, term: str):
        term_lower = term.lower()
        self.filas_tabla = [
            {
                "comanda": c["comanda"],
                "compania": c["compania"][:30],
                "destino": c["destino"],
                "pax": str(c["pax"]),
                "transporte": c["transporte"],
                "horario": c["horario"],
            }
            for c in self.comandas
            if (
                term_lower in c["comanda"].lower()
                or term_lower in c["destino"].lower()
                or term_lower in c["compania"].lower()
            )
        ]

    def set_search(self, value: str):
        self.search_term = value
        self._actualizar_tabla(value)

    # ── Generación de PDFs ────────────────────────────────────────────────────

    def _output_dir(self) -> str:
        """Directorio de salida para PDFs generados."""
        d = os.path.join(os.getcwd(), "generated_pdfs")
        os.makedirs(d, exist_ok=True)
        return d

    def generar_pdf_individual(self, folio: str):
        """Genera PDF de una comanda específica por su folio."""
        cmd = next((c for c in self.comandas if c["comanda"] == folio), None)
        if not cmd:
            self._notificar(f"No se encontró la comanda {folio}", "error")
            return

        path = os.path.join(self._output_dir(), f"Comanda_{folio}.pdf")
        generar_pdf_comanda(cmd, path, self.fecha_pdf, self.titulo_proyecto)
        abrir_archivo(path)
        self._notificar(f"PDF generado: Comanda_{folio}.pdf", "success")

    def generar_todas(self):
        path = os.path.join(self._output_dir(), "Todas_las_Comandas.pdf")
        generar_todas_pdf(self.comandas, path, self.fecha_pdf, self.titulo_proyecto)
        abrir_archivo(path)
        self._notificar("PDF generado: Todas_las_Comandas.pdf", "success")

    def generar_reporte(self):
        path = os.path.join(self._output_dir(), "Reporte_Estadistico.pdf")
        generar_reporte_estadistico(self.comandas, path, self.fecha_pdf, self.titulo_proyecto)
        abrir_archivo(path)
        self._notificar("PDF generado: Reporte_Estadistico.pdf", "success")

    # ── Notificaciones ────────────────────────────────────────────────────────

    def _notificar(self, msg: str, tipo: str = "info"):
        self.mensaje = msg
        self.mensaje_tipo = tipo
        self.mostrar_mensaje = True

    def cerrar_mensaje(self):
        self.mostrar_mensaje = False
