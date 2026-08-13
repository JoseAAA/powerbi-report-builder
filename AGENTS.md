# AGENTS.md — Power BI Report Builder

Guía para agentes de IA (Codex, Gemini CLI, Antigravity, OpenCode, Cursor, Claude
Code…). Este repo es un **framework para crear y auditar dashboards de Power BI como
proyecto PBIP** (TMDL + PBIR). En Claude Code además funciona como plugin con
skills (`skills/`); en cualquier otro agente, esta guía basta para operar.

Punteros por agente: `CLAUDE.md` (Claude Code) y `GEMINI.md` (Gemini CLI /
Antigravity) apuntan aquí; Codex, OpenCode y Cursor leen este `AGENTS.md` directo.
Una sola fuente de verdad, sin contenido duplicado.

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
   descubrimiento → KPIs → datos+M → modelo+DAX (RLS si aplica) → visualización →
   MVP → IA/Copilot → entrega. Cada fase tiene su reference (tabla abajo). Puedes
   arrancar la base con `init_proyecto.py`.
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
| `python scripts/generar_datos_ejemplo.py --dominio ventas\|rrhh\|finanzas\|salud\|generico` | CSVs de ejemplo (5 tablas) + `modelo-ejemplo.m` |
| `python scripts/scaffold_pbip.py --nombre "X" --dominio <d> --tema theme.json [--datos <carpeta>] [--en-raiz]` | proyecto `.pbip` válido (estrella + PBIR). **`--datos` cablea las particiones a los CSV**; `--en-raiz` deja el `.pbip` en la raíz |
| `python scripts/plan_reporte.py --nombre "X" --dominio <d> [--salida docs/plan.md] [--json]` | **el PLAN en lenguaje de negocio, ANTES de construir**: qué se mide, cómo se corta, la historia de cada página y las decisiones pendientes |
| `python scripts/init_proyecto.py --nombre "X" --dominio <d> --marca <m>\|--tema <t>\|--sin-marca [--aqui]` | bootstrap completo: `.pbip` en la raíz + `datos/` cableados + `docs/` |
| `python scripts/validar_modelo.py <ruta .SemanticModel>` | modelo: **R1–R12** propias **+ 26 reglas OFICIALES de Microsoft** (`BPARules.json`), cada hallazgo con su ID oficial y su fuente (exit 1 si hay ALTA) |
| `python scripts/catalogo_reglas.py` | guarda del catálogo: toda regla con fuente, ninguna ALTA apoyada solo en nivel 5, y el SHA-256 de `BPARules.json` sin tocar |
| `python scripts/validar_pbip.py <ruta .Report>` | valida el reporte, reglas **P1–P12** — incluye **P9: `altText` en todo visual**, la regla de accesibilidad de mayor severidad (exit 1 si hay ALTA) |
| `python scripts/verificar_cableado.py <carpeta del proyecto>` | **datos ↔ modelo**, reglas **E1–E6**: que el `.pbip` lea los CSV, que ninguna clave quede huérfana y que las medidas no mezclen indicadores |
| `python scripts/actualizar_catalogo.py [--forzar\|--json\|--marcar-revisado]` | vigila las **15 fuentes oficiales** (`scripts/fuentes.py`) y reporta páginas agregadas/eliminadas/**modificadas**. 1 llamada HTTP por fuente, sin token, con TTL por fuente (7/30/90 días) |
| `python scripts/prueba_rapida.py [--dominio d] [--salida ruta]` | **prueba de extremo a extremo autoverificada** (23 comprobaciones): genera plan + proyecto, corre los 4 validadores, y mete fallos a propósito para confirmar que se detectan. Sin internet |
| `python scripts/check_consistencia.py` | guarda de invariantes del repo, reglas **C1–C11** (frontmatter, forma de las `description`, `## Boundaries`, skills huérfanos, TMDL, rangos, references, portabilidad) |

`scripts/arquetipos.py` guarda el **conocimiento de diseño como datos**: el
cookbook *pregunta → visual* (con su regla y su fuente) y los arquetipos de
página con sus ranuras, posiciones y **texto alternativo**. El scaffold genera
las páginas desde ahí, no con visuales fijos: por eso produce **2 páginas y 14
visuales** con `altText` en todos, en vez de los 3 sin accesibilidad de antes.
Los arquetipos de negocio van marcados `heuristico=True` — Microsoft no define
arquetipos de página con nombre; los canónicos (tooltip 320×240, drillthrough,
móvil) sí tienen parámetros oficiales.

`scripts/tmdl.py` es un **parser de TMDL** (objetos y propiedades, no regex): las
reglas se escriben sobre datos. `scripts/catalogo_reglas.py` **consume el
`BPARules.json` OFICIAL de Microsoft** (copia fijada en `references/bpa/` con su
SHA-256) en vez de reinventar buenas prácticas: 71 reglas disponibles, 25
implementadas + 1 propia, 6 **excluidas a propósito y con motivo escrito** (p. ej.
`DATECOLUMN_FORMATSTRING` exige `mm/dd/yyyy`, que es incorrecto en es-ES).

`scripts/dominios.py` es el **catálogo único** de dominios de ejemplo (dimensiones,
indicadores, esquema de cada CSV). Lo importan `generar_datos_ejemplo.py` y
`scaffold_pbip.py`: si tocas nombres o filas de un dominio, se toca aquí y en un
solo sitio. Antes estaba duplicado en los dos scripts y divergió en todos los
dominios, así que los datos y el `.pbip` describían modelos distintos.

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
   `validar_pbip.py` detecta temas sin cablear (P7) y nombres de tema inconsistentes que rompen el tema **al publicar en el Service** (P8).
4. **Valida antes de entregar**: `validar_modelo.py`, `validar_pbip.py` y
   `verificar_cableado.py` en verde. Los dos primeros comprueban las reglas del
   framework; el tercero comprueba que el proyecto **describa algo coherente**
   (que el reporte lea los datos que hay al lado). Un modelo puede pasar R1–R12
   y P1–P12 y aun así mostrar cifras falsas: eso ya pasó.
5. **El plan se aprueba antes de construir.** Si el usuario va a obtener páginas y
   visuales NUEVOS, genera `plan_reporte.py`, resúmelo en lenguaje de negocio y
   **espera su OK**. No construyas con preguntas abiertas sin resolver. Revisar
   media página cuesta un minuto; rehacer 14 visuales, una tarde.
   _(Propuesta→aprobación de Fission-AI/OpenSpec; HARD-GATE de obra/superpowers.)_
6. **El MVP no puede mentir**: si generas datos de ejemplo, el `.pbip` los tiene
   que **leer** (`--datos`). Nunca entregues CSVs junto a un reporte que muestra
   otros números; el usuario corrige un CSV, refresca y espera ver el cambio.
7. **No inventes datos del negocio** (tablas, colores, metas, grain): pregunta.
8. **No inventes "mejores prácticas"**: cada recomendación traza a Microsoft o a
   un experto reconocido (Kimball, SQLBI/BPA, Chris Webb, IBCS, WCAG). El
   conocimiento citado vive en `references/` — cárgalo por fase, no todo junto.
   Respeta la **jerarquía de autoridad** (`NIVELES_AUTORIDAD` en `scripts/fuentes.py`):
   1 Microsoft Learn · 2 repos oficiales de Microsoft · 3 estándar de un organismo
   (W3C/IBCS) · 4 experto reconocido · 5 otro. **Una regla de severidad ALTA no
   puede sustentarse solo en un nivel 5.** Si no hay fuente oficial, «no está
   documentado oficialmente» es una respuesta válida; inventar no lo es.
   `check_consistencia.py` (C11) exige que cada reference cite al menos una
   fuente con URL; la deuda pendiente está **declarada** en
   `SIN_CITAS_PENDIENTES` y solo puede encoger.
9. **Nada privado al repo**: ni marcas/datos reales de empresas, ni rutas locales
   absolutas, ni `.pbi/` (caché). La marca del usuario vive en SU proyecto.
   Ojo con `expressions.tmdl`: el parámetro `RutaBase` lleva una ruta absoluta
   en el proyecto del usuario (correcto ahí, abre y funciona), pero cualquier
   proyecto que se versione como ejemplo público se genera con
   `--ruta-base "C:\CAMBIA-ESTA-RUTA\datos"`. El CI lo comprueba.
10. TMDL es sensible a indentación (tabs); JSON siempre válido
   (`python -m json.tool`); no edites `.pbi/` ni `localSettings.json`. Las
   descripciones de objeto van con **`///` encima del objeto** (no `description:`).
11. **Disciplina Git al editar un PBIP existente**: trabaja en una rama (no en
   `main`), valida con ambos validadores antes y después, y **nunca hagas commit
   automático** — el usuario revisa y confirma. Recomienda commit ANTES de una
   edición masiva. _(Práctica del repo oficial microsoft/skills-for-fabric.)_

## Mapa del conocimiento (cargar por fase)

| Fase / tema | Reference |
|---|---|
| Formato PBIP/TMDL/PBIR y reglas anti-corrupción | `references/formatos-pbip.md` |
| Marca y tema visual (WCAG) | `references/fase1-branding.md` |
| Descubrimiento (workshop) | `references/fase2-descubrimiento.md` |
| KPIs / OKRs | `references/fase3-kpis.md` |
| Conexión a fuentes y M (folding) | `references/datos-fuentes-y-m.md` |
| Modelo estrella y DAX | `references/fase4-modelado.md` + `references/nomenclatura.md` |
| Seguridad: RLS / OLS | `references/seguridad-rls.md` |
| Visualización y storytelling (IBCS) | `references/fase5-visualizacion.md` |
| MVP (datos de ejemplo + .pbip) | `references/datos-ejemplo-y-m.md` |
| Rendimiento y mantenimiento (VertiPaq) | `references/rendimiento-y-mantenimiento.md` |
| Modelo listo para IA / Copilot | `references/preparar-datos-ia.md` |
| Publicar / Git / Service / MCP | `references/entrega-git-y-mcp.md` |
| Cómo mantener las plantillas vigentes | `references/mantenimiento-de-plantillas.md` |

## Cómo se escribe un skill de este repo

Tres reglas, todas verificadas por `check_consistencia.py` (C8–C10) para que no se
erosionen:

1. **La `description` dice solo CUÁNDO, nunca QUÉ.** Arranca con `USAR cuando` y
   sigue con síntomas y frases literales del usuario entre comillas. Si la
   description resume el tema o el flujo, el agente **actúa desde ella y se salta
   el cuerpo del skill** — es un hallazgo empírico documentado en
   `obra/superpowers` (`skills/writing-skills/SKILL.md`), no una preferencia de
   estilo. Once de nuestras doce descriptions arrancaban con "Fase N — …".
2. **Disparador negativo obligatorio.** `NO usar para X (eso es <skill-hermano>)`.
   Con doce fases que se solapan (modelado vs rendimiento vs auditoría), sin esto
   el enrutamiento es una moneda al aire. Patrón de `DietrichGebert/ponytail`.
3. **`## Boundaries` en el cuerpo**: alcance dentro, alcance fuera, y a qué skill
   hermano enrutar lo que queda fuera. En las fases opinadas añade *cuándo NO
   aplicar el criterio al pie de la letra* — una regla que no sabe cuándo callarse
   se aplica donde estorba.

El cuerpo del skill es un **router**, no un manual: carga las references por
demanda con una tabla `Tema | Reference | Cuándo cargar` y la instrucción
explícita de no cargarlas todas de una vez (patrón de
`microsoft/skills-for-fabric`).

## De dónde sale cada decisión (trazabilidad)

Ninguna pieza de este framework es invención propia sin declararlo. Quién respalda qué:

| Pieza | Origen | Qué se tomó |
|---|---|---|
| Catálogo de reglas del modelo | **`BPARules.json` oficial de Microsoft** | Las 71 reglas con ID, severidad y expresión; 26 implementadas, 6 excluidas con motivo |
| Formato PBIP/TMDL/PBIR | **Microsoft Learn** + `microsoft/json-schemas` | Estructura, límites duros, regla del `$schema` |
| Roles de cada visual y props de tema | **`@microsoft/powerbi-report-authoring-cli`** (`catalog`, `formatting`) | Nombres de rol exactos por `visualType`; nunca se infieren de memoria |
| Accesibilidad | **WCAG 2.2 (W3C)** + checklist de Microsoft | `altText`, contraste 4.5:1 / 3:1, `tabOrder`, forma por serie |
| Modelo dimensional | **Kimball** | Esquema estrella, calendario dedicado |
| DAX | **Microsoft Learn** + **SQLBI** | `DIVIDE`, VAR/RETURN, medidas sobre columnas calculadas |
| Plan antes de construir | **Fission-AI/OpenSpec** + **obra/superpowers** | Propuesta→aprobación con artefacto en disco; HARD-GATE de diseño |
| `description` = solo disparadores | **obra/superpowers** | Hallazgo empírico: si resume el flujo, el agente se salta el cuerpo (C8) |
| Disparador negativo + `## Boundaries` | **DietrichGebert/ponytail** | "NO usar para X"; alcance dentro/fuera y a dónde enrutar (C9, C10) |
| Tabla `Tema \| Reference \| Cuándo cargar` | **microsoft/skills-for-fabric** | Progressive disclosure: no cargar todo de una vez |
| Vigilante de fuentes con TTL | **JoseAAA/power-automate-architect** | Lockfile + gate humano + contrato `--json` |
| Honestidad sobre lo no medido | **JuliusBrussee/caveman** | Declarar límites y lo que no tiene evidencia |

Lo que **no** tiene respaldo va marcado `[HEURÍSTICO]` o `[NO VERIFICADO]` en la
reference correspondiente, y no es exigible.

## Convenciones del proyecto

- Contenido para el usuario en **español**; términos técnicos estándar en su
  forma habitual (measure, star schema, query folding).
- Modelo: **estrella siempre**; nombres de negocio con espacios (sin `DIM_`/
  `FACT_` ni snake_case); calendario dedicado; **Auto date/time apagado**.
- DAX: medidas (no columnas calculadas), `VAR`/`RETURN`, `DIVIDE()` (nunca `/`),
  `formatString`, `displayFolder` y **descripción `///`** en cada medida (comentario
  `///` encima del measure, sintaxis TMDL oficial — la leen Copilot y los agentes
  LLM/MCP — R12); tabla `_ Medidas` oculta.
- Entregables como texto editable (JSON/TMDL/CSV/M), nunca capturas.
- Cambios de criterio → `CHANGELOG.md` con fecha y fuente.

## Verificación rápida del entorno

```bash
python -m py_compile scripts/*.py          # todo compila
python scripts/check_consistencia.py
python scripts/validar_modelo.py    "example/proyecto-demo-ventas/Demo-Ventas.SemanticModel"
python scripts/validar_pbip.py      "example/proyecto-demo-ventas/Demo-Ventas.Report"
python scripts/verificar_cableado.py "example/proyecto-demo-ventas"
```
Los cinco deben terminar sin hallazgos. Guía completa: `docs/pruebas.md`.
