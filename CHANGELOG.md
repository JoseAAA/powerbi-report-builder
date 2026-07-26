# CHANGELOG — powerbi-report-builder

Registro de cambios de criterio y de plantillas. Cada entrada: fecha · qué cambió
· fuente que lo respalda. Ver `references/mantenimiento-de-plantillas.md`.

## 2026-07-26 — el catalogo del modelo son las reglas OFICIALES de Microsoft

En vez de escribir nuestras propias "mejores practicas", el validador del modelo
consume el **`BPARules.json` oficial** de `microsoft/Analysis-Services`: 71 reglas
con `ID` estable, `Severity`, `Scope`, `Expression` y, en 30 de ellas, la URL de
referencia dentro de la propia regla.

### Añadido

- **`scripts/tmdl.py`**: parser de TMDL (objetos, propiedades, expresiones,
  descripciones `///`, indentacion con tabs o espacios). Las reglas se evaluan
  sobre datos, no sobre cadenas. Motivo concreto: con regex ya me colé una vez
  (`[\w ]+` capturaba un espacio y reportaba medidas "cualificadas" que no lo
  estaban).
- **`scripts/catalogo_reglas.py`**: 26 reglas implementadas — **25 oficiales de
  Microsoft + 1 propia** — cada una con `fuente` como **campo obligatorio**.
  `verificar_catalogo()` falla si a una regla le falta la fuente, si una de
  severidad ALTA se apoya solo en un nivel 5 de la jerarquia de autoridad, o si la
  copia local de `BPARules.json` no coincide con su SHA-256 fijado.
- **`references/bpa/BPARules.json`** + `.sha256`: copia fijada del catalogo oficial.
- **6 reglas oficiales EXCLUIDAS a proposito, con el motivo escrito** en
  `EXCLUIDAS` (que esten declaradas y no simplemente ausentes hace la decision
  auditable). La mas importante: **`DATECOLUMN_FORMATSTRING` exige literalmente
  `mm/dd/yyyy`**, el formato de EE. UU. En un reporte es-ES eso es incorrecto —
  mostraria 03/07 como 7 de marzo. Aplicarla a ciegas empeoraria el producto.
- **`PBI-NAME-01`**, regla propia: las reglas oficiales basadas en nombres
  INGLESES no disparan en español. `MONTH_(AS_A_STRING)_MUST_BE_SORTED` busca
  "MONTH", asi que nunca ve una columna `Mes` sin `sortByColumn` — y un slicer de
  meses sin ordenar sale alfabetico (Abril, Agosto, Diciembre...) y el reporte
  parece roto.
- **CI**: guarda del catalogo, y comparacion de la copia local con upstream
  reportando reglas nuevas / retiradas / modificadas por ID.

### Corregido (hallazgos del catalogo sobre nuestro propio generador)

- **`PERCENTAGE_FORMATTING`**: nuestras medidas usaban `0.0%;-0.0%;0.0%` y la
  regla oficial exige literalmente `#,0.0%;-#,0.0%;#,0.0%`. Es una convencion, no
  una correccion, pero es de Microsoft y cumplirla es gratis: generadores alineados.
- **`OBJECTS_WITH_NO_DESCRIPTION`**: las 5 tablas generadas no tenian descripcion
  `///`. Se añadieron, y explican el modelo (grano del hecho, para que sirve la
  dimension Indicador, por que filtrar por el calendario). Las leen Copilot y los
  agentes: es la misma razon por la que R12 ya las exigia en las medidas.
- **Bug en mi propia regla nueva**: `PBI-NAME-01` reportaba
  `Calendario[Trimestre]` porque "MES" es subcadena de "TRI-MES-TRE". Se exige
  limite de palabra. La regla oficial no tiene el problema porque en ingles
  "MONTH" casi no aparece dentro de otra palabra.
- **Duplicados suprimidos**: R1, R3, R6 y R12 ceden a su equivalente oficial
  cuando el catalogo esta disponible (y se evaluan como respaldo si no lo esta).
  Reportar el mismo problema dos veces con codigos distintos es ruido, y la
  version oficial ademas trae cita.

### Nota sobre el theme schema 2.156

Al subir de 2.143 a 2.156 aparece el aviso `PBIR_THEME_SCHEMA_UNREACHABLE` del
validador oficial: el CLI v0.1.4 conoce 2.143 pero no 2.156, asi que **se salta**
la validacion del tema (aviso, no error). Comprobado aislando la variable. Se
mantiene 2.156: fijar un schema viejo para complacer a una version de una
herramienta es al reves. Pendiente validar las claves del tema con stdlib para no
depender de que el CLI conozca la version.

## 2026-07-26 — vigilante de fuentes oficiales + theme schema al dia

"Todo sustentado en documentacion oficial y actualizada" pasa de intencion a
mecanismo: 15 fuentes declaradas, con TTL, y un script que detecta cuando
Microsoft las cambia.

### Añadido

- **`scripts/fuentes.py`**: registro de las 15 fuentes oficiales que sustentan el
  catalogo (repo, rama, ruta, TTL, y que reglas sustenta cada una). Todas
  confirmadas con peticion real a la API de GitHub. Tres cosas no eran lo que
  parecian: **DAX vive en `MicrosoftDocs/query-docs`** (no en `sql-docs` ni
  `bi-shared-docs`; `MicrosoftDocs/dax-docs` no existe), **`microsoft/Analysis-Services`
  usa rama `master`**, y los repos `*-pr` de MicrosoftDocs son privados.
- **Jerarquia de autoridad en 5 niveles** (`NIVELES_AUTORIDAD`): 1 Microsoft Learn ·
  2 repos oficiales de Microsoft · 3 estandar de organismo (W3C/IBCS) · 4 experto
  reconocido · 5 otro. **Una regla de severidad ALTA no puede sustentarse solo en
  un nivel 5.** Añadido a la regla dura #7.
- **`scripts/actualizar_catalogo.py`**: vigilante con **1 sola llamada HTTP por
  fuente** y sin token. `/contents` devuelve el **blob SHA de cada archivo**, asi
  que un inventario `{nombre: sha}` detecta agregados, eliminados **y
  modificados** sin tocar `/commits`. Para las fuentes cuyo contenido son
  carpetas (`pbir_schemas`, `skills_for_fabric`) se inventaria tambien el **tree
  SHA de cada subcarpeta**, que da deteccion recursiva con la misma llamada.
  Revision completa = 15 de las 60 llamadas/hora que permite GitHub sin token.
- **TTL por niveles, no global**: 7 dias las fuentes que se mueven mucho
  (`create-reports`, `guidance`), 30 las normales, 90 las casi inmoviles (spec de
  TMDL, `ms.date` 2023-12-27). Hay ~100x de diferencia de cadencia entre unas y
  otras; un TTL unico o revisa de mas o revisa de menos.
- **`references/estado-fuentes.json`**: lockfile con `ultima_revision` ISO y el
  inventario de cada fuente. Verificado en los dos sentidos: detecta modificados
  y eliminados, y respeta el TTL.
- Contrato para agentes: `--json` devuelve `pbi-builder/actualizar-catalogo@1`
  con exit codes estables (0 al dia · 1 hay cambios · 2 error de red/cuota).
- **Skill `powerbi-actualizar`**: TTL, interpretacion de cambios por tipo (pagina
  nueva / modificada / eliminada), **gate humano explicito** (no toca el catalogo
  sin OK), y una seccion honesta de lo que el mecanismo NO cubre (release plans,
  cambios de comportamiento sin cambio de doc, y que detectar que un archivo
  cambio no es lo mismo que verificar que la afirmacion citada sigue ahi).

### Corregido

- **Theme schema 13 versiones desactualizado**: el repo fijaba
  `reportThemeSchema-2.143.json` y upstream va por **2.156**. Comprobado antes de
  subirlo: el salto es puramente aditivo (2.156 añade `baseTheme` a nivel raiz, no
  elimina nada) y las 18 claves raiz de nuestros temas siguen reconocidas. Ahora
  la version esta en una constante (`SCHEMA_VERSION`) y la fuente `theme_schema`
  del vigilante avisa cuando aparezca otra.

## 2026-07-25 — el tema se rompia al publicar (validador oficial de Microsoft)

Existe un validador **oficial y publico** de Microsoft para PBIR:
`npx @microsoft/powerbi-report-authoring-cli validate <ruta .Report>`. Lo corri
contra los `example/` del repo y encontro **2 errores que nuestros validadores no
veian**. Ambos corregidos, y ahora los detecta `validar_pbip.py` sin depender de npm.

### Corregido

- **El tema se aplicaba mal AL PUBLICAR EN EL SERVICE.** `customTheme.name` llevaba
  el nombre "bonito" del tema (p. ej. `"Tema corporativo"`). Power BI Desktop abre
  bien, asi que el bug era invisible en local, pero el reporte publicado aplica el
  tema incorrectamente. Cita literal del validador: *"Using the bare theme name
  causes the published report on the Power BI service to incorrectly apply the
  theme"*. Golpeaba justo la regla dura #3 — los colores del usuario se perdian en
  silencio, y en el peor momento: al llegar a produccion.
  (Diagnostico `PBIR_THEME_NAME_MISSING_JSON_EXT`.)
- **`visualHeaderTooltip.show` no es una propiedad de tema valida** y
  `generar_theme.py` la escribia en todos los temas
  (`PBIR_THEME_VISUAL_PROP_UNKNOWN`). Eliminada.

La regla exacta se determino **empiricamente**, probando tres variantes contra el
validador oficial: el `name` interno del theme.json, `customTheme.name`,
`resourcePackages[].items[].name` y `.path` deben ser los **cuatro identicos** y
terminar en `.json`. Con el `name` interno sin extension, falla. El `theme.json`
suelto conserva su nombre legible; solo la copia incrustada se reescribe.

### Añadido

- **`validar_pbip.py` regla P8**: los cuatro valores del nombre del tema deben
  coincidir y llevar `.json`. Equivale a `PBIR_THEME_NAME_MISSING_JSON_EXT` +
  `PBIR_THEME_FILE_NAME_MISMATCH`, en stdlib. Verificada en los dos sentidos.
- **CI: el validador oficial como segunda capa independiente** (`continue-on-error`,
  para no romper el contrato stdlib-only del repo si el paquete no esta disponible).
  Nuestros validadores comprueban nuestras reglas; este comprueba las de Microsoft.
- `check_consistencia.py`: "P1-P7" pasa a rango obsoleto en C5. La propia guarda
  cazo las 8 referencias desactualizadas en la documentacion.

### Nota de metodo

Este hallazgo confirma el patron del bug anterior: **nuestros validadores en verde
no significan producto correcto**. Ahi fue el MVP mostrando datos falsos; aqui, el
tema rompiendose solo en el Service. Cuando existe una herramienta del fabricante,
se corre — no se sustituye por reglas propias.

## 2026-07-25 — el MVP dejó de mentir (corrección de raíz)

Auditoría del flujo real (`init_proyecto.py` de punta a punta) contra la
documentación oficial de Microsoft. Los tres validadores daban **verde** mientras
el producto entregaba cifras falsas: validaban las reglas del propio framework,
no si el proyecto describía algo coherente.

### Corregido

- **El `.pbip` ahora LEE los datos generados.** Un comando producía tres
  artefactos desconectados: 2 232 filas en CSV, un `modelo-ejemplo.m` para pegar
  a mano, y un `.pbip` con **6 filas inventadas inline**. El usuario abría su
  mockup y veía datos falsos. Nuevo `scaffold_pbip.py --datos <carpeta>`: las
  particiones leen los CSV vía el parámetro `RutaBase`.
- **`expressions.tmdl` (nuevo).** El modelo no tenía este archivo, así que era
  *imposible* parametrizar la ruta de los datos. Sintaxis oficial:
  `expression RutaBase = "..." meta [IsParameterQuery=true, ...]`.
  _Fuente: Microsoft Learn — Tabular Model Definition Language._
- **Dimensión `Indicador` (nueva).** El hecho es "alto" (una fila por indicador)
  y la clave `ID Indicador` **no apuntaba a ninguna tabla**, ni en los CSV ni en
  el TMDL. Al cablear los datos, `DIVIDE(SUM(Num), SUM(Den))` mezclaba
  `% Margen` con `Ticket Promedio` y daba **5226 %**. Con la dimensión y las
  medidas defendidas: `% Margen = 32.4 %`.
- **Medidas conscientes del indicador.** `Indicador %` exige un solo indicador
  en contexto (`HASONEVALUE`) y devuelve BLANK si hay ambigüedad — mejor una
  celda vacía que un número falso. Se añade una medida del indicador principal
  filtrada con `CALCULATE` para que las tarjetas muestren siempre un valor
  correcto sin depender de que el usuario segmente.
- **Catálogo de dominios unificado en `scripts/dominios.py`.** Estaba duplicado
  en los dos generadores y había divergido en **todos** los dominios (ventas: 6
  productos en los CSV vs 4 en el TMDL; salud: 8 servicios vs 4). Los CSV y el
  `.pbip` describían modelos distintos.
- **Columna `Año` alineada.** El CSV emitía `Anio` y el TMDL declaraba `Año`; al
  leer el CSV la partición no habría encontrado la columna. Se añade también
  `EsDiaHabil`, que el CSV traía y el modelo ignoraba.
- **`es-PE` / `es-ES` incrustados** en `scaffold_pbip.py` (modelo y `report.json`)
  → nuevo `--cultura`, default `es-ES`. Un país concreto dentro de un framework
  genérico que nadie había elegido.
- **Escapado de rutas en M.** `json.dumps` duplicaba las barras invertidas;
  Power Query **no** usa `\` como carácter de escape, así que el modelo habría
  buscado una ruta con separadores dobles. Nuevo helper `m_texto()`.

### Cambiado (ruptura de estructura, sin compatibilidad)

- **El `.pbip` va en la RAÍZ del proyecto.** Antes quedaba enterrado en
  `06-mvp/<Nombre>/` detrás de seis carpetas numeradas, **dos de ellas vacías**
  (`04-modelo/`, `05-diseno/`). Las fases numeradas eran la metodología del
  framework filtrándose al entregable del cliente. Estructura nueva:
  `.pbip` + `.SemanticModel/` + `.Report/` + `datos/` + `docs/`.
  Es lo que espera **Fabric Git Integration**, y sirve igual a quien publica
  directo desde Desktop sin ningún sistema de versiones.
- `example/` regenerado con la estructura nueva y `RutaBase` como placeholder
  (una ruta con el usuario dentro de un archivo versionado es fuga de datos).

### Añadido

- **`scripts/verificar_cableado.py`** (reglas **E1–E6**): guarda de regresión de
  este bug. Comprueba que el `.pbip` esté en la raíz, que exista `RutaBase`, que
  toda tabla con CSV disponible lo **lea**, que las columnas declaradas existan
  en la cabecera del CSV, que ninguna clave del hecho quede huérfana y que
  ninguna medida haga `DIVIDE` sin defensa por indicador. Verificado en los dos
  sentidos: pasa en los proyectos nuevos y **detecta el bug viejo**.
- **Instrucción PBIR que faltaba.** El repo no mencionaba en ningún sitio que
  hay que activar *Archivo > Opciones > Características en vista previa >
  «Almacenar informes con el formato de metadatos mejorado (PBIR)»*. Sin esa
  casilla, al guardar se pierde la carpeta `definition/` y el reporte vuelve a un
  `report.json` monolítico, sin diff por visual. Ahora va en el `LEEME.md` de
  cada proyecto generado y en la salida del bootstrap.
  _Fuente: Microsoft Learn — Power BI Desktop project report folder._
- `LEEME.md` por proyecto: activar PBIR, el bucle de mockup rápido (corregir un
  CSV → Actualizar) y las dos rutas de publicación (con Git → `main` → Fabric
  Git Integration; sin Git → Publicar desde Desktop).
- CI: chequeo de fugas extendido a `*.tmdl` y prueba de regresión de cableado.

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
