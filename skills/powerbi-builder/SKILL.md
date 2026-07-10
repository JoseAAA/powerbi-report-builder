---
name: powerbi-builder
description: >
  Orquestador y punto de entrada para crear, mejorar o auditar un reporte/dashboard
  de Power BI como proyecto PBIP. USAR cuando el usuario quiere "crear un dashboard",
  "armar/mejorar un reporte de Power BI", no sabe por donde empezar, sube archivos
  .pbip/.tmdl/.pbir/theme.json sin una fase clara, o su pedido abarca varias fases.
  Enruta a la fase: powerbi-marca, powerbi-descubrimiento, powerbi-kpis,
  powerbi-datos-m, powerbi-modelado-dax, powerbi-visualizacion, powerbi-mvp,
  powerbi-rendimiento, powerbi-ia-copilot, powerbi-auditoria, powerbi-entrega. NO usar
  para Excel/Power Query puro ni SQL de fuentes fuera de Power BI.
---

# Power BI Report Builder — Orquestador

El objetivo SIEMPRE es **un dashboard de Power BI entregado como proyecto PBIP**
(TMDL + PBIR), versionable en Git y editable por LLM/MCP. Este skill detecta con
quien hablas y en que fase estas, y deriva al skill especializado. El usuario
puede entrar por cualquier fase.

## Paso 0 — PERFIL del usuario (define *como* hablas)

Ante la duda, modo guiado.
- **Guiado (no tecnico):** "quiero un reporte bonito", "para mi jefe"; no menciona
  DAX/TMDL/JSON; sube Excel o imagen. → Cero jerga; no muestres codigo crudo salvo
  que lo pidan; entrega el archivo listo con pasos de clic; una pregunta a la vez.
- **Experto (tecnico):** menciona DAX, estrella, TMDL, PBIR, Git, Tabular Editor;
  sube .pbip; pide "audita/refactoriza/valida". → Directo y denso; edita archivos
  en su lugar; asume Git (sugiere commit antes de ediciones masivas).

## Paso 0-bis — NIVEL del proyecto (define *cuanto* haces)

El nivel gradua la profundidad, no elimina fases. Perfil y nivel son ejes
independientes (un usuario de negocio puede pedir un dashboard complejo).

| Nivel | Señales | Dashboard | Profundidad |
|---|---|---|---|
| **Basico** | 1 fuente (Excel/CSV), 1 area | 1-2 paginas, pocos KPIs | estrella simple; puede saltar descubrimiento/KPIs |
| **Intermedio** | varias fuentes, metas, varias areas | 3-5 paginas con drill | calculation groups, tema de marca, validar modelo |
| **Complejo** | SQL/Databricks/Fabric, RLS, gobierno | multipagina, bookmarks/drill-through | DirectQuery/Direct Lake, incremental, RLS, UDF, rendimiento, Git/CI |

## Paso 0.5 — Enruta a la fase (skill especializado)

| El usuario trae / pide | Skill |
|---|---|
| Colores, logo, marca, "crea/cambia el theme" | **powerbi-marca** |
| "Reunion con el area", "no se que pedir" | **powerbi-descubrimiento** |
| Lista de indicadores, "¿tenemos datos?", metas | **powerbi-kpis** |
| "¿De donde saco los datos?", Excel/SQL/Databricks/SharePoint, M | **powerbi-datos-m** |
| Tablas, relaciones, "crea las medidas", DAX, .tmdl | **powerbi-modelado-dax** |
| "Disena la pagina", "cuenta una historia", .pbir | **powerbi-visualizacion** |
| "Datos de ejemplo", "un .pbip base", "MVP rapido", arrancar un proyecto | **powerbi-mvp** |
| "Optimiza", "va lento", mantenimiento, VertiPaq | **powerbi-rendimiento** |
| "Prepara el modelo para Copilot/IA", sinonimos, descripciones, Q&A, "Approved for Copilot" | **powerbi-ia-copilot** |
| Una carpeta PBIP completa ("audita mi proyecto") | **powerbi-auditoria** |
| "Publicar", "subir a producción", versionar/GitHub, conectar al Service | **powerbi-entrega** |

Si llega sin contexto, pregunta en que punto esta y arranca ahi. No fuerces todas
las fases si solo necesita una.

## Principios transversales (aplican a TODOS los skills)

1. **Nunca inventes datos del negocio** (tabla, color, meta, grain): pregunta.
2. **No inventes recomendaciones**: cada "mejor practica" traza a documentacion de
   Microsoft o a un experto reconocido (Kimball, SQLBI/Tabular Editor BPA, Chris
   Webb, IBCS/*Storytelling with Data*, WCAG, Anthropic Agent Skills). Si no hay
   fuente, dilo. Las plantillas son **vivas**: llevan `actualizado:`/`fuentes:` y se
   mantienen vigentes (ver `${CLAUDE_PLUGIN_ROOT}/references/mantenimiento-de-plantillas.md`).
3. **Facil de usar y best-in-class**: en guiado, pasos de clic y cero jerga; el
   trabajo mecanico lo hacen los scripts; apunta al mejor resultado, no a "aceptable".
4. **Entregables editables y versionables** (theme JSON, TMDL, PBIR JSON, CSV), no capturas.
5. **Eficiencia de tokens**: carga solo el skill/reference de la fase activa; el
   trabajo determinista va a `${CLAUDE_PLUGIN_ROOT}/scripts/*.py`, no a tokens.
6. **Cada fase produce un entregable** que alimenta la siguiente.
7. **Antes de tocar un PBIP existente**, lee `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md`.

## Flujo completo

```
Marca → theme.json   ·   Descubrimiento → doc   ·   KPIs → fichas
Datos+M → query por tabla   ·   Modelado+DAX → TMDL   ·   Visualizacion → PBIR
MVP → datos ejemplo + .pbip base   ·   Rendimiento → modelo optimizado + validado
```

## Arrancar un proyecto nuevo (bootstrap)

Para una empresa/trabajo nuevo, genera la base en un comando:
`python "${CLAUDE_PLUGIN_ROOT}/scripts/init_proyecto.py" --nombre "<Empresa>" --dominio <d> --marca <marca.json>|--tema theme.json|--sin-marca`
→ crea `proyecto-<nombre>/` con paletas, estructura de fases y un `.pbip` base.
El tema es una eleccion EXPLICITA (regla: los colores del usuario nunca se
ignoran en silencio). La marca del usuario vive en SU proyecto, no en el plugin.
