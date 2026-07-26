# Guía de uso

De lo más simple a lo avanzado. El objetivo siempre: **un dashboard de Power BI
entregado como proyecto PBIP** (versionable y editable por IA).

## 1. Instalar (una vez)

**Claude Code (plugin completo):**
```
/plugin marketplace add JoseAAA/powerbi-report-builder
/plugin install powerbi-report-builder@powerbi-report-builder-marketplace
```
*(Para desarrollo local usa la ruta clonada en vez del `owner/repo`:
`/plugin marketplace add /ruta/a/powerbi-report-builder`.)*

**Otros agentes (Codex, Gemini CLI, OpenCode, Cursor…):** clona el repo y abre tu
agente en esta carpeta — leerán `AGENTS.md` y sabrán usar los scripts y las
references. No hay dependencias que instalar (Python estándar).

**Sin agente:** usa los scripts directamente (sección 4).

## 2. Los 3 caminos según tu caso

### 🔍 Experto: "solo quiero validar mi reporte"
> "Audita este proyecto de Power BI" (apunta a tu carpeta `.pbip`)

O directo en terminal:
```bash
python scripts/validar_modelo.py "MiReporte.SemanticModel"   # modelo/DAX: R1–R12
python scripts/validar_pbip.py   "MiReporte.Report"          # reporte:    P1–P8
```
Salen hallazgos por severidad (ALTA/MEDIA/BAJA) con el fix concreto.

### 🛠️ Tengo una idea y quiero el reporte completo
> "Quiero crear un dashboard de ventas para mi empresa"

El orquestador te lleva por fases (marca → descubrimiento → KPIs → datos →
modelo → visualización → MVP → IA/Copilot → entrega). O arranca la base en un comando:
```bash
python scripts/init_proyecto.py --nombre "Mi Reporte" --dominio ventas --marca mi-marca.json
```
*(El tema es obligatorio: `--marca`, `--tema` o `--sin-marca` explícito — tus
colores nunca se ignoran en silencio.)*

### 👤 No técnico
> "Necesito un reporte bonito de ventas para mi jefe, no sé por dónde empezar"

Modo guiado: cero jerga, una pregunta a la vez, y recibes el `.pbip` listo con
pasos de clic.

## 3. Tu marca (los colores de tu empresa)

1. Copia `assets/marca/_plantilla-marca.json` → `mi-empresa.json` **en tu
   proyecto** (p. ej. `mi-reporte/docs/`), llénalo (o pide al agente que lo
   llene desde tu logo/manual/hex) y pon `"activa": true`.
2. Genera el tema: `python scripts/generar_theme.py --marca mi-empresa.json --salida theme.json`
3. Ese `theme.json` va en todo lo demás (`init_proyecto --tema`, `scaffold --tema`).

> La marca vive en **tu proyecto**, no dentro del plugin (los plugins se
> actualizan y borran lo que guardes dentro).

## 4. Scripts disponibles (sin agente)

| Script | Qué hace |
|---|---|
| `generar_theme.py` | marca → `theme.json` (schema oficial + contraste WCAG) |
| `editar_theme.py` | cambios puntuales a un theme (modo oscuro, primario…) |
| `generar_conexion_m.py` | código M por fuente (Excel/SharePoint/SQL/Databricks/Fabric) |
| `generar_datos_ejemplo.py` | CSVs de ejemplo multi-dominio + `modelo-ejemplo.m` |
| `scaffold_pbip.py` | proyecto `.pbip` mínimo y válido (estrella + PBIR + tema) |
| `init_proyecto.py` | bootstrap completo `proyecto-<nombre>/` (estructura + tema + datos + `.pbip`) |
| `validar_modelo.py` | BPA-lite del modelo (R1–R12, incl. description para IA) |
| `validar_pbip.py` | validación del reporte (P1–P8, incl. tema cableado) |

## 5. Publicar (producción)

Dos caminos (detalle en `references/entrega-git-y-mcp.md`):
- **Sin Git:** Power BI Desktop → Publicar → workspace → credenciales + refresco.
- **Con Git:** GitHub + Fabric Git integration (rama `main` ↔ workspace) + pipelines.

Antes de publicar: corre ambos validadores.
