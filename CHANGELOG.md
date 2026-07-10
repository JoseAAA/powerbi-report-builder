# CHANGELOG — powerbi-report-builder

Registro de cambios de criterio y de plantillas. Cada entrada: fecha · qué cambió
· fuente que lo respalda. Ver `references/mantenimiento-de-plantillas.md`.

## 2026-07-10 — portabilidad multi-agente (sin release)

- **README reposicionado**: ya no es "Skill para Claude"; es un **framework
  multi-proveedor** (Claude Code, Codex, Gemini CLI, Antigravity, OpenCode, Cursor
  y sin agente). Nueva tabla de compatibilidad por agente.
- **Puntero `GEMINI.md`** (para Gemini CLI / Antigravity, que leen `GEMINI.md`, no
  `AGENTS.md`), fino y sin duplicar contenido — apunta a `AGENTS.md`. Junto con
  `CLAUDE.md`, mantiene UNA sola fuente de verdad (patrón adaptador de ponytail).
- **check_consistencia.py C7**: verifica que `AGENTS.md` exista y que los punteros
  `CLAUDE.md`/`GEMINI.md` existan y lo referencien (la portabilidad no se rompe en
  silencio). Validado: los scripts corren sin ningún entorno de agente.

## 2026-07-10 (sin release)

- **Fix rutas largas en Windows (MAX_PATH 260)**: `scaffold_pbip.py` fallaba con
  `FileNotFoundError` al escribir el árbol `.Report/.SemanticModel` (que agrega
  ~90 caracteres de profundidad propia) cuando la carpeta de salida era honda;
  los validadores fallaban igual al leer. Ahora los tres scripts
  (`scaffold_pbip.py`, `validar_modelo.py`, `validar_pbip.py`) normalizan la ruta
  con el prefijo `\\?\` en Windows (incl. UNC). Detectado con el smoke test de CI
  corrido en Windows con salida profunda. _Fuente: docs de Microsoft sobre
  "Maximum Path Length Limitation" (Win32)._

## 2026-07 (v0.4.0)

- **Nuevo módulo IA / Copilot** (`references/preparar-datos-ia.md` + skill
  `powerbi-ia-copilot`): deja el modelo **AI-ready** para que respondan bien Copilot
  y los agentes LLM/MCP — descripciones, sinónimos/linguistic, y las 3 funciones
  oficiales "Prep data for AI" (AI instructions, verified answers, AI data schemas) +
  "Approved for Copilot". _Fuente: Microsoft Learn "Prepare your data for AI"._
- **Descripción en cada medida** como estándar, con la sintaxis TMDL **oficial `///`**
  (comentario encima del measure, no una propiedad `description:`): `scaffold_pbip.py`
  y ambos ejemplos la generan; nueva regla **R12** en `validar_modelo.py` (medida sin
  `///`). Es el metadato que leen Copilot y los agentes. _Fuente: Microsoft Learn —
  TMDL overview (descriptions con `///`) + Copilot semantic models._
- **Fix de validación de color**: `generar_theme.py` ahora RECHAZA hex inválidos
  (p. ej. `--primario azul`) antes de escribir, en vez de colar `"azul"` al
  `theme.json` (que Power BI rechazaría). Detectado probando entradas inválidas.
- **Seguridad RLS/OLS** (`references/seguridad-rls.md`): patrón recomendado RLS
  dinámico con `USERPRINCIPALNAME()`, OLS para columnas sensibles, y cómo probarlo
  (usuarios externos). Cableado en `powerbi-modelado-dax` y en la entrega.
  _Fuente: Microsoft Learn (RLS guidance) + Tabular Editor._
- **Field parameters** añadidos a `fase4-modelado.md` (elegir métrica/dimensión en
  un slicer). _Fuente: SQLBI / Microsoft._
- **Precisión PBIR**: default desde enero 2026 (Desktop y Service), **aún en preview**,
  GA planificada Q3 2026 (antes decía "Desktop desde marzo"). _Fuente: Power BI blog._
- **Consistencia de docs**: `validar_pbip` es P1–**P7** (no P1–P6) en README, AGENTS,
  auditoría y entrega; `validar_modelo` es R1–**R12**.

## 2026-07 (v0.3.0)

- **Fix definitivo "no respeta mis colores"**: `init_proyecto.py` ahora EXIGE elegir
  tema (`--marca` / `--tema` nuevo / `--sin-marca` explícito) — se eliminó el default
  neutro silencioso; acepta un `theme.json` ya generado; los skills obligan a pasar
  `--tema` al scaffold. Nueva regla **P7** en `validar_pbip.py`: detecta tema presente
  pero no cableado en `report.json` (colores sin aplicar) y viceversa.
- **Seguridad**: `scaffold_pbip.py` sanitiza `--nombre` (bloquea path traversal `../`
  y caracteres inválidos — verificado con test). `generar_datos_ejemplo.py` ya no
  escribe rutas locales absolutas en `modelo-ejemplo.m` (placeholder + sugerencia en
  consola): sin fugas de username en archivos versionables.
- **Repo profesional**: `LICENSE` (MIT), CI de GitHub Actions (compila scripts, valida
  manifiestos, smoke test end-to-end, valida ejemplos R1–R11/P1–P7, chequeo anti-fugas),
  `CONTRIBUTING.md`, `SECURITY.md`, `docs/` (guia-de-uso, pruebas — antes PRUEBAS.md).
- **`AGENTS.md`** (estándar multi-agente): el repo ahora funciona con Codex, Gemini CLI,
  OpenCode, Cursor, etc. — guía canónica con reglas duras, scripts y mapa de references;
  `CLAUDE.md` apunta a él. _Fuente: convención AGENTS.md del ecosistema de agentes._
- **La marca del usuario vive en SU proyecto** (no dentro del plugin, que se borra al
  actualizar): skills `powerbi-marca`/`powerbi-builder`/`powerbi-mvp` y
  `assets/marca/README.md` actualizados.
- **`example/` regenerado profesional**: `Demo-Ventas`/`Demo-Salud` sin espacios en
  carpetas de proyecto, tema desde la marca de ejemplo ("Tema Empresa Ejemplo", ya no
  "reemplazar"), sin rutas locales; ambos validan R1–R11 y P1–P7.

## 2026-06

- **Skill 100% brand-agnostic.** Ninguna marca activa por defecto; hay una marca de
  ejemplo genérica en `assets/marca/ejemplos/ejemplo-corporativo.json` (`activa: false`).
  La Fase 1 captura la marca de la empresa del usuario. _Fuente: requisito de diseño
  (skill reutilizable por cualquier empresa) + patrón de tokens de marca._
- **Datos de ejemplo y scaffold multi-dominio** (`--dominio ventas|rrhh|finanzas|salud|generico`).
  _Fuente: Kimball (modelo estrella) — el dominio es intercambiable, la estructura no._
- **Nueva fase "Datos y fuentes (M)"** (`references/datos-fuentes-y-m.md`) +
  generador `scripts/generar_conexion_m.py` para Excel/SharePoint/SQL/Databricks/Fabric.
  _Fuente: Chris Webb (query folding) + guía oficial de Power Query (Microsoft)._
- **Nivel de proyecto** (básico/intermedio/complejo) como segundo eje en `SKILL.md`,
  centrado en el dashboard PBIP como entregable. _Fuente: Microsoft (modos Import/DQ/
  Direct Lake, RLS, incremental refresh)._
- **Sistema de plantillas vivas**: encabezado `actualizado:`/`fuentes:` por plantilla,
  este CHANGELOG y `references/mantenimiento-de-plantillas.md`. Principio "no inventar:
  todo traza a fuente oficial y se mantiene vigente". _Fuente: política del proyecto._
- **Fixes de tooling Windows**: `validar_modelo.py` ya no falla al imprimir en consola
  cp1252; preset de tema renombrado a "Callout Destacado" (genérico).
- **Reestructurado como PLUGIN de Claude Code**: 10 skills especializados bajo
  `skills/` (`powerbi-builder` orquestador + uno por fase + `powerbi-auditoria`);
  `.claude-plugin/plugin.json`; scripts/assets/references compartidos vía
  `${CLAUDE_PLUGIN_ROOT}`. _Fuente: spec oficial de plugins de Claude Code; patrón de
  superpowers / skills-for-fabric / ponytail._
- **Fase 7 (rendimiento)**: skill `powerbi-rendimiento` + `references/rendimiento-y-mantenimiento.md`;
  `validar_modelo.py` amplía a **R8–R11** (sumarizable visible, dateTime fuera del
  calendario, relaciones bidireccionales, columnas calculadas). _Fuente: SQLBI /
  VertiPaq Analyzer, DAX Studio, Tabular Editor BPA._
- **Bootstrap** `scripts/init_proyecto.py`: arma `proyecto-<nombre>/` (estructura de
  fases + tema + datos de ejemplo + `.pbip` base) en un comando. _Fuente: convención del framework._
- **Purga de datos privados** (confidencialidad): el repo no contiene marcas ni
  reportes de ninguna empresa real; marca de ejemplo → `ejemplo-corporativo.json`;
  `example/` con muestras públicas oficiales (`example/README.md`) + plantillas
  generadas (ventas, salud).
- **Fix `editar_theme.py`**: salida reconfigurada a UTF-8 (evita crash en consola
  Windows cp1252 con símbolos `✔/→/•`), mismo arreglo aplicado antes a `validar_modelo.py`.
- **`PRUEBAS.md`**: guía de pruebas en 3 niveles (scripts / Power BI Desktop / plugin).
- **Fix corrupción de report.json con tema custom**: `scaffold_pbip.py` ahora incluye
  `reportVersionAtImport` (visual/page/report) en `themeCollection.customTheme`, que es
  **requerido** por `ThemeMetadata`. Sin él, Power BI Desktop rechazaba el informe.
  _Fuente: schema oficial report/3.x (verificado)._ + `formatos-pbip.md` documenta
  "qué es FIJO vs qué VARÍA" y las propiedades requeridas que no se pueden omitir.
- **`validar_pbip.py`** (nuevo): valida el lado REPORTE (PBIR) — JSON válido, `$schema`,
  `themeCollection` completo (P2/P3), `pages.json` coherente — para atrapar la
  corrupción ANTES de abrir en Power BI. Cableado en `powerbi-auditoria`.
- **Etapa 7 — Entrega**: skill `powerbi-entrega` + `references/entrega-git-y-mcp.md`
  con **dos caminos** (sin Git: publicar directo / con Git: GitHub + Fabric Git
  integration rama `main`↔workspace), versionado, MVP→producción y MCP. + `.gitignore`
  (PBIP: ignora `**/.pbi/`) y `.claude-plugin/marketplace.json` para instalar el plugin.
  _Fuente: Microsoft Learn (PBIP, Fabric CI/CD Git, publicar/refresco/RLS)._
- **README "Cómo se usa (3 perfiles)"**: validar/auditar (experto) · crear de cero ·
  guiado (no técnico).
