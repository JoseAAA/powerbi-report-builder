# CHANGELOG — powerbi-report-builder

Registro de cambios de criterio y de plantillas. Cada entrada: fecha · qué cambió
· fuente que lo respalda. Ver `references/mantenimiento-de-plantillas.md`.

## 2026-07

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
