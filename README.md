# 📊 Power BI Report Builder

![Licencia](https://img.shields.io/badge/Licencia-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Funciona con](https://img.shields.io/badge/funciona%20con-Claude%20·%20ChatGPT%20·%20Gemini%20·%20Codex%20·%20OpenCode-blueviolet)
![Dependencias](https://img.shields.io/badge/dependencias-0%20(solo%20stdlib)-brightgreen)
![Reglas](https://img.shields.io/badge/reglas-26%20oficiales%20de%20Microsoft-0078D4)

**Crea, audita y publica reportes de Power BI hablándole a tu asistente de IA en
español — de la idea de negocio al `.pbip` versionable, con datos que puedes tocar
desde el primer minuto.**

Son instrucciones reutilizables (skills) + scripts deterministas que le enseñan a
Claude Code, Codex, Gemini CLI u OpenCode a construir reportes siguiendo las
**reglas oficiales de Microsoft** (el `BPARules.json` del Best Practice Analyzer),
WCAG y los frameworks del sector (Kimball, SQLBI, IBCS). Para analistas y equipos
que quieren un reporte profesional sin memorizar 71 reglas.

---

## 🤔 ¿Esto para qué me sirve? (en cristiano)

Si haces reportes en Power BI, probablemente te pasa algo de esto:

- Empiezas de cero cada vez y **nunca sabes si lo estás haciendo bien**.
- Alguien te pide un tablero y **no sabes qué preguntarle**.
- Terminas el reporte y **te dicen que no era eso**.
- Hay 71 reglas oficiales de buenas prácticas y **nadie se las sabe**.

Esto es un ayudante que se sienta contigo: te hace las preguntas correctas,
**te enseña un plan antes de construir nada**, y cuando construye lo hace
siguiendo las reglas oficiales de Microsoft — y te dice de dónde salió cada una.

**No necesitas saber programar.** Le hablas en español a tu asistente de IA
(Claude, Codex, Gemini…) y él hace el trabajo.

---

## 📋 Primero el plan, después el reporte

Esta es la parte que más tiempo te ahorra. **Antes de crear un solo gráfico**,
recibes un plan en lenguaje de negocio que puedes leer en un minuto:

```text
# Plan del reporte — Ventas LATAM

> Esto es una propuesta, no el reporte. Léela, dime qué cambiar, y
> recién ahí lo construyo.

## 1. Qué vamos a medir
| Indicador            | Tipo       |
| % Margen ← el principal | Porcentaje |
| % Cumplimiento Meta  | Porcentaje |

## 3. Las páginas y su historia

### Página 1: Resumen
Para quien decide y no explora.

Cómo se lee:
- Entras y lo primero que ves es **cómo vamos** (las tarjetas de arriba).
- Justo debajo, **si eso mejora o empeora** con el tiempo.
- Al lado, **quién lo explica**: qué categorías tiran del resultado.
- Y abajo, **las cifras exactas** por si alguien las pide.

## 4. Lo que necesito que decidas
- [ ] ¿'% Margen' es de verdad el indicador que abre el reporte?
- [ ] ¿Hay una meta contra la que comparar?
```

Si algo no cuadra, lo dices y se cambia **antes** de construir. Corregir el plan
cuesta un minuto; rehacer un reporte de 14 visuales, una tarde.

*(Patrón de propuesta→aprobación de [OpenSpec](https://github.com/Fission-AI/OpenSpec)
y del gate de diseño de [superpowers](https://github.com/obra/superpowers).)*

---

## 👀 Míralo en acción

```text
Tú ▸ hazme un dashboard de ventas para arrancar hoy, sin esperar a que TI me dé la base

Agente ▸ Antes de construir, mira el plan (docs/plan.md):
         · Mide: % Margen (el principal), % Cumplimiento Meta, Ticket Promedio
         · Cortes: Región, Producto, Indicador, Calendario
         · Página 1 «Resumen»: cómo vamos → si mejora → quién lo explica → cifras
         · Página 2 «Detalle»: la matriz que localiza la causa
         ¿Le cambiamos algo? ¿'% Margen' es el que abre el reporte?

Tú ▸ está bien, dale

Agente ▸ Proyecto listo: mi-reporte/
         dominio: ventas | tema: marca | cultura: es-ES
         tema docs/theme.json : OK
         datos de ejemplo     : OK   (2.232 filas en 5 tablas)
         .pbip (en la raiz)   : OK   [lee los CSV de datos/]

         ANTES DE ABRIRLO — una vez por equipo, en Power BI Desktop:
         Archivo > Opciones > Caracteristicas en vista previa >
         marca «Almacenar informes con el formato de metadatos mejorado (PBIR)»

Tú ▸ ¿y qué tal quedó?

Agente ▸ 2 páginas (Resumen + Detalle), 14 visuales, 4 segmentadores.
         Validación:
           OK  Sin hallazgos (R1-R12 + 26 reglas oficiales de Microsoft)
           OK  Sin hallazgos en el reporte (P1-P9)
           OK  El .pbip lee los CSV, las claves tienen dimension
               y las medidas no mezclan indicadores

Tú ▸ los rangos no se parecen a mi negocio

Agente ▸ Edita datos/Ventas.csv y pulsa Actualizar en Power BI.
         El reporte cambia sin tocar el modelo. Cuando la forma te sirva,
         cambiamos el origen por tu SQL y las medidas siguen funcionando.
```

Abres el `.pbip`, pulsas **Actualizar** y ves **tus** datos — no seis filas de
relleno. Corriges un CSV, refrescas, y el reporte cambia. Ese bucle es el punto.

---

## 🚀 Instalación

**Prerrequisito único:** [Python 3.8+](https://www.python.org/downloads/). Cero
dependencias que instalar. Elige tu herramienta:
[Claude Code](#claude-code) · [Codex](#openai-codex) · [Gemini CLI](#gemini-cli) ·
[OpenCode](#opencode) · [sin agente](#sin-agente)

### Claude Code

```text
/plugin marketplace add JoseAAA/powerbi-report-builder
/plugin install powerbi-report-builder@powerbi-report-builder-marketplace
```
Para actualizarlo más adelante:
`/plugin marketplace update powerbi-report-builder-marketplace`
y luego `/plugin update powerbi-report-builder@powerbi-report-builder-marketplace`.

Entrada: **`powerbi-builder`** (orquestador). El resto de skills se activa solo
según la fase; no tienes que recordar nombres.

### OpenAI Codex

```bash
git clone https://github.com/JoseAAA/powerbi-report-builder.git
```
Abre la carpeta con Codex: lee **[AGENTS.md](AGENTS.md)**, la guía canónica
(reglas duras, tabla de scripts, mapa de references) y sabe operar igual.

### Gemini CLI

Igual que Codex: clona y abre la carpeta (`GEMINI.md` → `AGENTS.md`).

### OpenCode

Igual que Codex: clona y abre la carpeta (además lee `skills/`).

### ChatGPT · Claude.ai · Gemini (versión web)

No acceden a tu disco, pero **sí tienen sandbox de Python** — y como el proyecto
no usa ninguna dependencia externa, los scripts corren ahí.

1. Descarga el repo como ZIP (*Code → Download ZIP*) y súbelo al chat o Proyecto.
2. Pégale esto:

> Descomprime el ZIP. Lee `AGENTS.md`: es la guía canónica de este framework.
> Ejecuta `python scripts/prueba_rapida.py` para verificar que funciona.
> Después ayúdame a crear un reporte: **primero el plan**
> (`scripts/plan_reporte.py`), esperas mi aprobación, y recién luego construyes.

3. Al terminar, pídele el proyecto como ZIP para abrirlo en Power BI Desktop.

Lo único que no funciona ahí es `actualizar_catalogo.py` (necesita internet); el
catálogo de reglas ya viene en el repo. Detalle: [docs/probar.md](docs/probar.md).

### Sin agente

Los scripts funcionan solos, sin IA de por medio:
```bash
python scripts/init_proyecto.py --nombre "Mi Reporte" --dominio ventas --sin-marca
```
Guía completa en [docs/guia-de-uso.md](docs/guia-de-uso.md).

---

## 🏁 Primeros pasos

**Antes que nada, comprueba que todo funciona en tu máquina:**

```bash
python scripts/prueba_rapida.py
```

Ejecuta el flujo completo y **se autoverifica** — incluso mete fallos a propósito
para confirmar que los detecta. Termina en `TODO CORRECTO — 23 comprobaciones` o
te dice qué falló. No necesita internet.

Luego, tres formas de usarlo según lo que necesites hoy:

### A) Ya tengo un reporte y quiero saber si está bien hecho

No necesita nada más. Apunta a tu carpeta PBIP y dile al agente:

> *"audita este proyecto de Power BI: C:\proyectos\ventas"*

Recibes hallazgos por severidad, **cada uno con su fuente oficial**:

```text
[ALTA]  NUMERIC_COLUMN_SUMMARIZE_BY: Ventas[Num]: summarizeBy=sum (deberia ser none)
        [fuente: github.com/microsoft/Analysis-Services/.../BPARules.json]
[MEDIA] USE_THE_DIVIDE_FUNCTION_FOR_DIVISION: usa '/' en vez de DIVIDE()
        [fuente: learn.microsoft.com/power-bi/guidance/dax-divide-function-operator]
```

O directo en terminal:
```bash
python scripts/validar_modelo.py     "MiReporte.SemanticModel"   # R1-R12 + 26 oficiales
python scripts/validar_pbip.py       "MiReporte.Report"          # P1-P9
python scripts/verificar_cableado.py "MiReporte"                 # E1-E6
```

### B) Quiero un reporte desde cero

> *"quiero un dashboard de ventas para mi empresa"*

El orquestador detecta si eres técnico o no, y te lleva por las fases que hagan
falta — sin obligarte a pasar por todas. O arranca la base en un comando:

```bash
python scripts/init_proyecto.py --nombre "Ventas LATAM" --dominio ventas --marca mi-empresa.json
```

### C) Necesito enseñar algo hoy, sin tener los datos reales

> *"dame datos de ejemplo y un .pbip que ya los muestre"*

Genera CSVs y un `.pbip` **que los lee**. Editas un CSV, pulsas Actualizar en
Power BI y el reporte cambia: así iteras la forma del reporte antes de pelear con
la fuente real.

> **Un paso obligatorio, una sola vez por equipo:** en Power BI Desktop,
> *Archivo > Opciones > Características en vista previa >* marca **«Almacenar
> informes con el formato de metadatos mejorado (PBIR)»** y reinicia. Sin esa
> casilla, al guardar se pierde el detalle por visual y con él el diff en Git.
> ([fuente](https://learn.microsoft.com/power-bi/developer/projects/projects-report))

---

## 💬 Qué puedes pedirle (prompts de ejemplo)

| Quiero… | Escríbele a tu agente, por ejemplo |
|---|---|
| 🔍 **Auditar** mi proyecto | *"Audita este PBIP y dime qué está mal"* |
| 🎨 **Mi marca** en el reporte | *"Usa los colores de mi empresa, te paso el logo"* |
| 🧭 **No sé qué medir** | *"Tengo reunión con Comercial y no sé qué pedirles"* |
| 📐 **Definir KPIs** | *"Estos son los indicadores, ¿tenemos datos para calcularlos?"* |
| 🔌 **Conectar datos** | *"Los datos están en SharePoint / SQL / Databricks, ¿cómo los traigo?"* |
| 🧮 **Medidas DAX** | *"Crea las medidas con buenas prácticas y nomenclatura"* |
| 🖼️ **Diseñar la página** | *"Esto se ve cargado, ordénalo y cuéntame la historia"* |
| ⚡ **Va lento** | *"El reporte tarda muchísimo en abrir"* |
| 🤖 **Copilot** | *"Prepara el modelo para que Copilot responda bien"* |
| 🚀 **Publicar** | *"¿Cómo lo subo al Service?"* · *"Quiero versionarlo en GitHub"* |
| 🔄 **Criterio al día** | *"¿Hay novedades de Power BI? ¿El catálogo sigue vigente?"* |

Cada fase produce un **entregable editable** (theme JSON, TMDL, PBIR, CSV, M) que
alimenta la siguiente. Nunca capturas de pantalla.

---

## 📦 Qué obtienes

Un proyecto que Power BI y Git entienden, con el `.pbip` **en la raíz** — que es
donde lo busca Fabric Git Integration:

```text
mi-reporte/
├── Mi Reporte.pbip              ← el punto de entrada
├── Mi Reporte.SemanticModel/    ← modelo: tablas, relaciones, medidas (TMDL)
├── Mi Reporte.Report/           ← reporte: 2 páginas, 14 visuales (PBIR)
├── datos/                       ← los CSV que el modelo LEE de verdad
├── docs/                        ← tema, marca, descubrimiento, KPIs
└── LEEME.md  .gitignore
```

Sirve para **los dos caminos de publicación**, sin bifurcar nada:

- **Con Git:** commit y push a `main` → Fabric Git Integration → Service.
- **Sin Git:** abres el `.pbip` en Desktop y **Publicar**. No necesitas ningún
  sistema de versiones para empezar — que es la realidad de muchas empresas.

---

## 🧠 Cómo funciona (y por qué puedes confiar en el criterio)

- **El criterio no lo inventa la IA.** El validador del modelo **consume el
  `BPARules.json` oficial** de `microsoft/Analysis-Services` — 71 reglas con su ID,
  severidad y expresión. Implementamos 26, y **6 están excluidas a propósito con el
  motivo escrito**: p. ej. `DATECOLUMN_FORMATSTRING` exige literalmente
  `mm/dd/yyyy`, que en un reporte es-ES sería incorrecto.
- **Cada regla lleva su fuente, y es campo obligatorio.** `catalogo_reglas.py`
  falla si a una regla le falta la URL, o si una de severidad ALTA se apoya solo en
  un blog. Hay una **jerarquía de autoridad en 5 niveles** (Microsoft Learn > repos
  oficiales > estándar de organismo > experto reconocido > otro).
- **La documentación se vigila, no se supone.** `actualizar_catalogo.py` consulta
  **15 fuentes oficiales** con una sola llamada HTTP cada una y avisa qué páginas se
  agregaron, borraron o **modificaron**. TTL por fuente (7/30/90 días) según su
  cadencia real.
- **Si no hay fuente, se dice.** `fase5-visualizacion.md` documenta 13 afirmaciones
  populares **rechazadas por no tener respaldo** — incluida "máximo 6-8 visuales por
  página", que este mismo repo llegó a publicar como regla y no existe en ninguna
  doc de Microsoft.
- **Cuatro capas de validación**, no una: reglas propias (R1-R12, P1-P9), las 26
  oficiales de Microsoft, el cableado datos↔modelo (E1-E6), y **el validador oficial
  del fabricante** (`@microsoft/powerbi-report-authoring-cli`) como comprobación
  independiente en CI.
- **Accesibilidad por construcción**: el generador **no puede** crear un visual sin
  texto alternativo — lanza excepción. `altText` en los 14 visuales, `tabOrder`
  siguiendo el orden de lectura, y contraste verificado (texto **y** colores de
  datos: WCAG 1.4.3 y 1.4.11).
- **Cero dependencias y cero telemetría.** Solo librería estándar de Python. La
  única salida a red es opcional y sin credenciales: el vigilante consulta
  metadatos públicos en `api.github.com`.

---

## 🩺 Problemas comunes

| Problema | Solución |
|---|---|
| **Al guardar en Desktop desaparece la carpeta `definition/`** | Falta activar PBIR: *Archivo > Opciones > Características en vista previa > «Almacenar informes con el formato de metadatos mejorado»*, y reiniciar. |
| **Abro el `.pbip` y no carga los datos** | Moviste el proyecto. Corrige la ruta en *Inicio > Transformar datos > Administrar parámetros > **RutaBase***. |
| **Los colores se ven bien en Desktop pero mal al publicar** | Era un bug real, corregido: el nombre del tema debe llevar `.json` y coincidir en cuatro sitios. `validar_pbip.py` (regla **P8**) lo detecta. Regenera el tema. |
| **Un KPI da un número absurdo (miles por ciento)** | Estás sumando indicadores distintos. Necesitas la dimensión `Indicador` y una medida defendida con `HASONEVALUE` o `CALCULATE`. Pídele *"el KPI da 5226%, revísalo"*. |
| **La tarjeta sale en blanco** | La medida exige **un solo** indicador en contexto (a propósito: mejor vacío que falso). Usa el segmentador de `Indicador`, o la medida del indicador principal. |
| **El agente no toma la última versión** | Actualiza el plugin: `/plugin marketplace update …` → `/plugin update …`. |
| **`validar_modelo.py` avisa de que no pudo cargar el catálogo oficial** | Falta `references/bpa/BPARules.json`. Las reglas R1-R12 se evalúan igual; recupera el archivo con `git checkout`. |
| **GitHub devuelve 403 al actualizar el catálogo** | Se agotaron las 60 llamadas/hora que da sin token. Espera y reintenta: el TTL evita que pase en uso normal. |
| **Los datos de ejemplo no se parecen a mi negocio** | Están **para** eso: edita los CSV de `datos/` y pulsa Actualizar. Si necesitas otra forma, pide *"cambia el modelo de ejemplo a …"*. |
| **¿Puedo mostrar esto a un directivo?** | Los datos de ejemplo son **aleatorios**. Dilo antes de proyectarlos, o conecta la fuente real primero. |

---

## 📚 Documentación

- **Guía canónica para agentes:** [AGENTS.md](AGENTS.md) — reglas duras, scripts,
  mapa de references, y cómo se escribe un skill de este repo.
- **Fases (skills):** [Orquestador](skills/powerbi-builder/SKILL.md) ·
  [Marca](skills/powerbi-marca/SKILL.md) ·
  [Descubrimiento](skills/powerbi-descubrimiento/SKILL.md) ·
  [KPIs](skills/powerbi-kpis/SKILL.md) ·
  [Datos+M](skills/powerbi-datos-m/SKILL.md) ·
  [Modelado+DAX](skills/powerbi-modelado-dax/SKILL.md) ·
  [Visualización](skills/powerbi-visualizacion/SKILL.md) ·
  [MVP](skills/powerbi-mvp/SKILL.md) ·
  [Rendimiento](skills/powerbi-rendimiento/SKILL.md) ·
  [IA/Copilot](skills/powerbi-ia-copilot/SKILL.md) ·
  [Auditoría](skills/powerbi-auditoria/SKILL.md) ·
  [Entrega](skills/powerbi-entrega/SKILL.md) ·
  [Actualizador](skills/powerbi-actualizar/SKILL.md)
- **Formato PBIP/TMDL/PBIR (reglas anti-corrupción):** [formatos-pbip.md](references/formatos-pbip.md)
- **Criterio visual y accesibilidad:** [fase5-visualizacion.md](references/fase5-visualizacion.md)
  — incluye las 13 afirmaciones rechazadas por no tener fuente.
- **Nomenclatura citada:** [nomenclatura.md](references/nomenclatura.md) ·
  **RLS/OLS:** [seguridad-rls.md](references/seguridad-rls.md)
- **Publicar / Git / Service:** [entrega-git-y-mcp.md](references/entrega-git-y-mcp.md)
- **Uso paso a paso:** [docs/guia-de-uso.md](docs/guia-de-uso.md) ·
  **Pruebas:** [docs/pruebas.md](docs/pruebas.md)
- **Seguridad:** [SECURITY.md](SECURITY.md) · **Cambios:** [CHANGELOG.md](CHANGELOG.md)
- **Ejemplos ejecutables:** [example/](example/) — dos proyectos completos que
  pasan todos los validadores.

---

## 📐 Frameworks y fuentes

| Área | Fuente |
|---|---|
| Reglas del modelo | **`BPARules.json` oficial** (microsoft/Analysis-Services) — 71 reglas |
| Formato PBIP/TMDL/PBIR | Microsoft Learn + `microsoft/json-schemas` |
| Tema visual | theme schema oficial (`powerbi-desktop-samples`, v2.156) |
| Accesibilidad | WCAG 2.2 (W3C) + checklist de accesibilidad de Microsoft |
| Modelo dimensional | Kimball (esquema estrella) |
| DAX | Microsoft Learn DAX best practices · SQLBI (Russo/Ferrari) |
| Power Query / M | Microsoft Learn · Chris Webb |
| Visualización | Microsoft Learn (docs + Training) · IBCS (parte pública) · ColorBrewer |
| IA / Copilot | Microsoft "Prepare your data for AI" |

---

## 🤝 Contribuir y licencia

Issues y PRs bienvenidos — convenciones en [AGENTS.md](AGENTS.md) y
[CONTRIBUTING.md](CONTRIBUTING.md). Antes de abrir un PR:

```bash
python scripts/check_consistencia.py   # C1-C11: invariantes del repo
python scripts/catalogo_reglas.py      # toda regla con fuente
```

**JoseAAA** · [github.com/JoseAAA](https://github.com/JoseAAA) · MIT — ver [LICENSE](LICENSE)
