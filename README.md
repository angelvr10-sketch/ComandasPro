# 🛢️ Comanda App — Migración Flet → Reflex

Sistema de Gestión de Comandas PEMEX migrado de Flet (desktop) a **Reflex** (web + desktop).

---

## 📁 Estructura del proyecto

```
comanda_app/
├── rxconfig.py                  # Configuración de Reflex
├── requirements.txt
├── README.md
└── comanda_app/
    ├── __init__.py
    ├── parser.py                # Lógica de negocio (sin UI)
    ├── state.py                 # Estado reactivo (equivale a variables de Flet)
    ├── components.py            # Componentes reutilizables
    └── comanda_app.py           # Página principal y definición del app
```

---

## 🚀 Instalación y arranque

### 1. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Inicializar Reflex (solo la primera vez)
```bash
reflex init
```

### 4. Ejecutar en modo desarrollo
```bash
reflex run
```

Abre tu navegador en **http://localhost:3000**

### 5. Ejecutar como app de escritorio (desktop)
```bash
reflex run --backend-only &       # backend en segundo plano
reflex run --frontend-only        # o usa la ventana del navegador
```

> Para modo desktop nativo, usa **`reflex run`** — Reflex abrirá el navegador automáticamente.  
> Si quieres una ventana standalone, envuelve con **pywebview** o **Tauri** (ver sección avanzada abajo).

---

## 🔄 Tabla de equivalencias Flet → Reflex

| Concepto en Flet | Equivalente en Reflex |
|---|---|
| `page.update()` | Automático al mutar `State` |
| Variables de instancia (`self.comandas`) | `rx.State` vars (`ComandaState.comandas`) |
| `ft.Column`, `ft.Row` | `rx.vstack`, `rx.hstack` |
| `ft.Container` | `rx.box` |
| `ft.Text` | `rx.text`, `rx.heading` |
| `ft.ElevatedButton` | `rx.button` |
| `ft.FilePicker` | `rx.upload` |
| `ft.DataTable` | `rx.table.root` + `rx.foreach` |
| `ft.ListView` | `rx.scroll_area` + `rx.foreach` |
| `ft.PieChart` | `rx.recharts.pie_chart` |
| `ft.ProgressBar` | `loading=True` en `rx.button` |
| `on_click=lambda e: ...` | `on_click=State.handler` |
| `ft.colors.BLUE_800` | String CSS `"#1565C0"` |

---

## 📐 Cambios de paradigma importantes

### 1. Estado reactivo vs imperativo

**Flet (imperativo):**
```python
# Flet — mutas directamente y llamas page.update()
loading.visible = True
page.update()
data = parse_pdf(path)
loading.visible = False
page.update()
```

**Reflex (reactivo):**
```python
# Reflex — yield hace que el frontend reciba el nuevo estado
async def handle_upload(self, files):
    self.loading = True
    yield                          # el frontend se actualiza aquí
    data = parse_pdf(path)
    self.loading = False
```

### 2. Loops de UI con `rx.foreach`

**Flet:**
```python
list_destinos.controls = [
    ft.Container(ft.Row([ft.Text(d), ft.Text(str(v))])) 
    for d, v in stats.items()
]
```

**Reflex:**
```python
rx.foreach(
    ComandaState.por_destino,
    lambda item: rx.hstack(rx.text(item["destino"]), rx.text(item["pax"]))
)
```

### 3. Condicionales con `rx.cond`

**Flet:**
```python
dashboard_content.visible = True
```

**Reflex:**
```python
rx.cond(
    ComandaState.dashboard_visible,
    dashboard(),      # componente si True
    zona_inicial(),   # componente si False
)
```

---

## 🖥️ Modo desktop standalone (opcional)

Para empaquetar como app de escritorio sin navegador visible, instala **pywebview**:

```bash
pip install pywebview
```

Crea `desktop.py` en la raíz:

```python
import subprocess, threading, webview

def start_backend():
    subprocess.run(["reflex", "run", "--backend-only"])

threading.Thread(target=start_backend, daemon=True).start()
webview.create_window("Dashboard Comandas v3.0", "http://localhost:8000", width=1280, height=900)
webview.start()
```

Ejecuta con:
```bash
python desktop.py
```

---

## 📦 Empaquetar para distribución

```bash
# Instalar PyInstaller
pip install pyinstaller

# Empaquetar
pyinstaller --onefile --windowed desktop.py \
  --add-data "comanda_app:comanda_app"
```

---

## 🔑 Variables de entorno (opcional)

Crea `.env` en la raíz si necesitas configurar puertos:

```
REFLEX_BACKEND_PORT=8000
REFLEX_FRONTEND_PORT=3000
```

---

**Angel Valenzuela Romero © 2026**
