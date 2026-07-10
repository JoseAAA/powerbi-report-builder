# Power BI Report Builder — Skill para Claude

> 🇪🇸 Asistente experto end-to-end para crear reportes de Power BI con las
> mejores prácticas actuales (2026): desde el problema de negocio hasta los
> archivos PBIP, incluyendo datos de ejemplo y un proyecto `.pbip` base.
> 🇬🇧 *End-to-end expert skill for building Power BI reports with current best
> practices — from business discovery to a runnable PBIP project. Content in Spanish.*

## ¿Qué hace?

Guía (y ejecuta) el **flujo completo por fases**. Se adapta a quién lo usa: modo
guiado (no técnico, cero jerga, pasos de clic) o modo experto (edita archivos,
listo para Git).

1. **Marca** — lee un **archivo de marca guardado y reutilizable**
   (`assets/marca/`), te dice qué colores tiene tu empresa y, si no son los
   correctos, los captura (logo, manual, `.pbip` o hex) y los **guarda una sola
   vez** para no volver a preguntar. Genera el `theme.json` (con `$schema`,
   semáforos, style presets 2026) y verifica contraste WCAG. Funciona para
   cualquier empresa: el archivo de marca es intercambiable.
2. **Descubrimiento** — design workshop con plantilla de agenda y dinámicas.
3. **KPIs/OKRs** — ficha por indicador, validada contra datos (✅/⚠️/❌).
4. **Modelado y DAX** — estrella, **nomenclatura de negocio** (sin `DIM_/FACT_`,
   con citas), VAR/RETURN, calculation groups, DAX UDF (GA 2026), field parameters,
   patrón Num/Den, `description` en cada medida, **RLS/OLS**, y un validador BPA-lite.
5. **Visualización** — storytelling IBCS + patrón Z, style presets y visual
   calculations (2026); edita PBIR directamente.
6. **MVP rápido** — genera **datos de ejemplo + código M para pegar** y un
   **proyecto `.pbip` base** listo para abrir y modificar.
7. **IA / Copilot** — deja el modelo **AI-ready** (descripciones, sinónimos, "Prep
   data for AI", Approved for Copilot) para que Copilot y los agentes LLM/MCP
   respondan bien.

Trabaja sobre el formato **PBIP** (TMDL + PBIR), estándar de Power BI 2026.

## Sistema de marca (genérico, para cualquier empresa)

El skill **no trae ninguna marca activa por defecto**. En la Fase 1 captura la
identidad de *tu* empresa (logo, presentación/`.thmx`, manual, `.pbip` o hex) y
la guarda una sola vez como `assets/marca/<empresa>.json` con `"activa": true`,
para no volver a preguntarla. La carpeta `assets/marca/ejemplos/` trae marcas de
**ejemplo** (`activa: false`) solo como referencia de cómo se llena el archivo.

## Instalación

Es un **plugin de Claude Code** que empaqueta varios skills especializados (uno por
fase) más scripts y assets compartidos.

**Claude Code:** instálalo como plugin desde el repo (`/plugin`), o para desarrollo
local apunta Claude Code a esta carpeta. El skill de entrada es `powerbi-builder`
(orquestador); los demás se activan solos según la fase.

**Claude.ai / Desktop:** cada carpeta de `skills/<nombre>/` puede subirse como skill
individual; `powerbi-builder` es el punto de entrada.

**Otros agentes (Codex, Gemini CLI, OpenCode, Cursor…):** clona el repo y abre tu
agente en esta carpeta: leerán **[AGENTS.md](AGENTS.md)** (la guía canónica
multi-agente) y podrán usar scripts y references igual. Sin dependencias.

## Cómo se usa (3 perfiles)

- **Solo validar / auditar (experto):** ¿tu reporte sigue las buenas prácticas?
  Apunta el skill `powerbi-auditoria` a tu carpeta PBIP, o corre directo:
  `python scripts/validar_modelo.py <...>.SemanticModel` y
  `python scripts/validar_pbip.py <...>.Report` → hallazgos por severidad (R1–R12 / P1–P7).
- **Crear de cero (una idea → reporte):** el orquestador `powerbi-builder` te lleva
  fase por fase; o arranca la base en un comando:
  `python scripts/init_proyecto.py --nombre "Mi Reporte" --dominio ventas`.
- **No técnico (modo guiado):** describe lo que quieres en lenguaje de negocio
  ("un reporte de ventas para mi jefe"); el skill edita por dentro y te entrega el
  `.pbip` listo, con pasos de clic.

## Uso (prompts que lo activan)

- "Quiero crear un reporte de Power BI para el área de Compras"
- "Genera el theme con los colores de mi empresa"
- "Dame datos de ejemplo y un .pbip base para arrancar"
- "Aquí está mi carpeta PBIP, audita el modelo y las medidas"
- "Crea las medidas DAX con buenas prácticas"

## Estructura

```
powerbi-report-builder/                 # plugin (la raíz del repo)
├── .claude-plugin/  (plugin.json · marketplace.json)
├── .github/workflows/ci.yml            # CI: compila + valida ejemplos + anti-fugas
├── AGENTS.md                           # guía canónica multi-agente (Codex/Gemini/OpenCode/…)
├── README.md · CHANGELOG.md · LICENSE · CONTRIBUTING.md · SECURITY.md
├── docs/  (guia-de-uso.md · pruebas.md)
├── skills/                             # un skill por fase (autodescubiertos)
│   ├── powerbi-builder/                # ENTRADA: perfil + nivel + enruta
│   ├── powerbi-marca/                  # Fase 1
│   ├── powerbi-descubrimiento/         # Fase 2
│   ├── powerbi-kpis/                   # Fase 3
│   ├── powerbi-datos-m/                # Datos + M
│   ├── powerbi-modelado-dax/           # Fase 4
│   ├── powerbi-visualizacion/          # Fase 5
│   ├── powerbi-mvp/                    # Fase 6
│   ├── powerbi-rendimiento/            # Fase 7
│   ├── powerbi-ia-copilot/            # preparar el modelo para IA/Copilot
│   ├── powerbi-auditoria/              # auditar un PBIP existente
│   └── powerbi-entrega/               # publicar / Git / Service / producción
├── references/                         # conocimiento citado (plantillas vivas)
│   ├── formatos-pbip.md · nomenclatura.md · mantenimiento-de-plantillas.md
│   ├── fase1-branding.md … fase5-visualizacion.md · seguridad-rls.md
│   ├── datos-fuentes-y-m.md · datos-ejemplo-y-m.md · rendimiento-y-mantenimiento.md
│   └── preparar-datos-ia.md · entrega-git-y-mcp.md
├── assets/
│   ├── marca/ (_plantilla-marca.json · ejemplos/ejemplo-corporativo.json · README.md)
│   ├── ejemplos/                       # acumulación por uso
│   └── ficha-kpi.md · plantilla-descubrimiento.md · plantilla-agenda-taller.md
└── scripts/                            # compartidos (stdlib): ${CLAUDE_PLUGIN_ROOT}/scripts
    ├── generar_theme.py · editar_theme.py   # marca → theme.json (WCAG)
    ├── generar_conexion_m.py                # M por fuente (sql/sharepoint/databricks/…)
    ├── generar_datos_ejemplo.py · scaffold_pbip.py   # datos + .pbip base (multi-dominio)
    ├── validar_modelo.py · validar_pbip.py  # BPA-lite modelo (R1–R12) + reporte (P1–P7)
    ├── init_proyecto.py                     # bootstrap proyecto-<nombre>/
    └── check_consistencia.py                # guarda de invariantes del repo (CI)
```

## Frameworks y fuentes

- Formato PBIP/TMDL/PBIR y theme schema (Microsoft Learn + `powerbi-desktop-samples`)
- Nomenclatura: Tabular Editor (2026), Chris Webb, SQLBI, Microsoft
- BPA del equipo Power BI CAT; DAX UDF (GA jun 2026); visual calculations (GA 2026)
- IA/Copilot: Microsoft "Prepare your data for AI" (AI instructions, verified answers, AI data schemas)
- Seguridad: RLS/OLS (Microsoft Learn RLS guidance)
- IBCS® / fórmula SUCCESS; esquema estrella (Kimball)

## Licencia

MIT.
