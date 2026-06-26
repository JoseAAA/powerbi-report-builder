# AGENTS.md — Power BI Report Builder

Guía para agentes de IA (Codex, Gemini CLI, OpenCode, Cursor, Claude Code…).
Este repo es un **framework para crear y auditar dashboards de Power BI como
proyecto PBIP** (TMDL + PBIR). En Claude Code además funciona como plugin con
skills (`skills/`); en cualquier otro agente, esta guía basta para operar.

## Qué hace el proyecto

Lleva a cualquier usuario —experto o no técnico— desde una idea de negocio hasta
un dashboard de Power BI **entregado como proyecto PBIP** versionable, aplicando
frameworks de la industria (Kimball, SQLBI, Chris Webb, IBCS, WCAG, OKR) con
scripts deterministas en Python (solo librería estándar).

## Cómo atender al usuario (3 casos)

1. **"Audita/valida mi reporte"** (experto): corre los dos validadores (tabla de
   abajo), contrasta con `references/fase4-modelado.md`, `nomenclatura.md`,
   `rendimiento-y-mantenimiento.md` y `fase5-visualizacion.md`, y entrega
   hallazgos por severidad con el fix por archivo.
2. **"Quiero crear un dashboard"** (de cero): sigue las fases en orden — marca →
   descubrimiento → KPIs → datos+M → modelo+DAX → visualización → MVP → entrega.
   Cada fase tiene su reference (tabla abajo). Puedes arrancar la base con
   `init_proyecto.py`.
3. **Usuario no técnico**: cero jerga, una pregunta a la vez, no muestres
   JSON/TMDL salvo que lo pida; entrega archivos terminados y pasos de clic.

Gradúa la profundidad por nivel: **básico** (1 fuente, 1-2 páginas) /
**intermedio** (varias fuentes, tema de marca, validación) / **complejo**
(SQL/Databricks/Fabric, RLS, refresco incremental, Git/CI).

## Scripts (Python 3.8+, sin dependencias)

| Comando | Qué hace |
|---|---|
| `python scripts/generar_theme.py --marca <marca.json> --salida theme.json` | marca → tema oficial con contraste WCAG |
| `python scripts/editar_theme.py --archivo theme.json [--modo oscuro …]` | edita un tema sin perder el resto |
| `python scripts/generar_conexion_m.py --fuente sql\|sharepoint-archivo\|databricks\|… ` | código Power Query M parametrizado por fuente |
| `python scripts/generar_datos_ejemplo.py --dominio ventas\|rrhh\|finanzas\|salud\|generico` | CSVs de ejemplo + `modelo-ejemplo.m` |
| `python scripts/scaffold_pbip.py --nombre "X" --dominio <d> --tema theme.json` | proyecto `.pbip` mínimo válido (estrella + PBIR) |
| `python scripts/init_proyecto.py --nombre "X" --dominio <d> --marca <m>\|--tema <t>\|--sin-marca` | bootstrap completo `proyecto-x/` |
| `python scripts/validar_modelo.py <ruta .SemanticModel>` | BPA-lite del modelo, reglas **R1–R11** (exit 1 si hay ALTA) |
| `python scripts/validar_pbip.py <ruta .Report>` | valida el reporte, reglas **P1–P7** (exit 1 si hay ALTA) |

**Prefiere el script al trabajo manual**: generan salidas correctas y
deterministas (temas, M, TMDL, PBIR) sin gastar tokens ni inventar formatos.

## Reglas duras (NO negociables)

1. **Antes de editar cualquier archivo de un proyecto PBIP**, lee
   `references/formatos-pbip.md` (qué es FIJO vs qué VARÍA, y propiedades
   requeridas). Errores aquí **corrompen el reporte** al abrirlo.
2. **Nunca cambies la propiedad interna `name`** (~20 caracteres) de páginas,
   visuales o bookmarks. `displayName` sí es editable.
3. **El tema del usuario nunca se ignora en silencio**: `init_proyecto.py` exige
   `--marca`/`--tema`/`--sin-marca`; al scaffoldear pasa SIEMPRE `--tema`.
   `validar_pbip.py` (P7) detecta temas sin cablear.
4. **Valida antes de entregar**: `validar_modelo.py` y `validar_pbip.py` en verde.
5. **No inventes datos del negocio** (tablas, colores, metas, grain): pregunta.
6. **No inventes "mejores prácticas"**: cada recomendación traza a Microsoft o a
   un experto reconocido (Kimball, SQLBI/BPA, Chris Webb, IBCS, WCAG). El
   conocimiento citado vive en `references/` — cárgalo por fase, no todo junto.
7. **Nada privado al repo**: ni marcas/datos reales de empresas, ni rutas locales
   absolutas, ni `.pbi/` (caché). La marca del usuario vive en SU proyecto.
8. TMDL es sensible a indentación (tabs); JSON siempre válido
   (`python -m json.tool`); no edites `.pbi/` ni `localSettings.json`.

## Mapa del conocimiento (cargar por fase)

| Fase / tema | Reference |
|---|---|
| Formato PBIP/TMDL/PBIR y reglas anti-corrupción | `references/formatos-pbip.md` |
| Marca y tema visual (WCAG) | `references/fase1-branding.md` |
| Descubrimiento (workshop) | `references/fase2-descubrimiento.md` |
| KPIs / OKRs | `references/fase3-kpis.md` |
| Conexión a fuentes y M (folding) | `references/datos-fuentes-y-m.md` |
| Modelo estrella y DAX | `references/fase4-modelado.md` + `references/nomenclatura.md` |
| Visualización y storytelling (IBCS) | `references/fase5-visualizacion.md` |
| MVP (datos de ejemplo + .pbip) | `references/datos-ejemplo-y-m.md` |
| Rendimiento y mantenimiento (VertiPaq) | `references/rendimiento-y-mantenimiento.md` |
| Publicar / Git / Service / MCP | `references/entrega-git-y-mcp.md` |
| Cómo mantener las plantillas vigentes | `references/mantenimiento-de-plantillas.md` |

## Convenciones del proyecto

- Contenido para el usuario en **español**; términos técnicos estándar en su
  forma habitual (measure, star schema, query folding).
- Modelo: **estrella siempre**; nombres de negocio con espacios (sin `DIM_`/
  `FACT_` ni snake_case); calendario dedicado; **Auto date/time apagado**.
- DAX: medidas (no columnas calculadas), `VAR`/`RETURN`, `DIVIDE()` (nunca `/`),
  `formatString` y `displayFolder` en cada medida; tabla `_ Medidas` oculta.
- Entregables como texto editable (JSON/TMDL/CSV/M), nunca capturas.
- Cambios de criterio → `CHANGELOG.md` con fecha y fuente.

## Verificación rápida del entorno

```bash
python -m py_compile scripts/*.py          # todo compila
python scripts/validar_modelo.py "example/proyecto-demo-ventas/06-mvp/Demo-Ventas/Demo-Ventas.SemanticModel"
python scripts/validar_pbip.py   "example/proyecto-demo-ventas/06-mvp/Demo-Ventas/Demo-Ventas.Report"
```
Los tres deben terminar sin hallazgos. Guía completa de pruebas: `docs/pruebas.md`.
