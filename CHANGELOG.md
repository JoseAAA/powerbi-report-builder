# CHANGELOG — powerbi-report-builder

Registro de cambios de criterio y de plantillas. Cada entrada: fecha · qué cambió
· fuente que lo respalda. Ver `references/mantenimiento-de-plantillas.md`.

## 2026-07-26 — v0.7.0 · el plan se aprueba antes de construir

Peticion directa del usuario: *"antes de hacer los visuales creemos el plan de
forma muy facil de entender para que el usuario lo valide"*. Y dos bugs de
visuales encontrados con el CLI oficial de Microsoft, que hasta ahora no se
habia usado mas que para `validate`.

### Añadido — el PLAN antes que nada

- **`scripts/plan_reporte.py`**: el plan del reporte en **lenguaje de negocio**.
  Cero TMDL, cero PBIR, cero `visualType` en lo que el usuario lee. Dice que se
  mide, como se corta, **la historia de cada pagina** (como se lee de arriba a
  abajo), y **las decisiones que faltan** como casillas sin marcar.
  El plan no se aprueba con preguntas abiertas.
- **HARD-GATE en tres skills** (`powerbi-builder`, `powerbi-mvp`,
  `powerbi-visualizacion`): si el usuario va a obtener paginas y visuales NUEVOS,
  primero el plan y su aprobacion explicita.
  _(Propuesta→aprobacion de Fission-AI/OpenSpec; HARD-GATE de obra/superpowers.)_
- `init_proyecto.py` escribe `docs/plan.md` **antes** que el tema y los datos, y
  lo marca en la salida con `<- LEELO PRIMERO`.
- Regla dura #5 de AGENTS.md.

### Corregido — dos bugs de visuales que ningun schema podia ver

- **El `textbox` renderizaba una caja VACIA.** Su contenido va en
  `visual.objects.general[].properties.paragraphs`, no en el titulo del
  contenedor. El catalogo oficial lo confirma: `catalog describe textbox`
  devuelve `roles: {}` y `formattingObjects: [general, text, values]`.
  Poniendo solo `title` se veia una barra de titulo sobre una caja sin texto — y
  ahi es justo donde vive **el mensaje de la pagina**, que es lo que sostiene el
  storytelling. El fallo se llevaba por delante lo mas importante de la pagina.
- **Altura del textbox por debajo del minimo**: 40 px con fuente de 18 pt genera
  scrollbar. El validador oficial pide **≥45**; ahora son 48
  (`PBIR_TEXTBOX_HEIGHT_BELOW_FLOOR`).

### Verificado con el CLI oficial (mas alla de `validate`)

El `@microsoft/powerbi-report-authoring-cli` tiene mas comandos de los que
usabamos: `catalog`, `formatting`, `preview-visuals`, `preview-pages`, `doctor`.

- **`catalog describe <visualType>` da los nombres de rol EXACTOS** por visual.
  Se contrastaron los 7 tipos que genera el scaffold: `cardVisual→Data`,
  `lineChart→Category/Y`, `pivotTable→Rows/Columns/Values`, `tableEx→Values`,
  `slicer→Values`… **todos correctos**, incluido el `kind` (Measure vs Grouping).
- Hallazgo importante para el futuro: **el schema NO valida los nombres de rol**.
  `queryState` es `additionalProperties`, asi que un rol inventado pasa el schema
  Y pasa `validate`, pero Power BI lo ignora y el visual sale vacio. La unica
  fuente autoritativa es `catalog`: **nunca inferir roles de memoria**.
- `preview-visuals` confirma que el CLI ve los 14 visuales con su tipo correcto.

### Documentacion

- **README**: nueva seccion *"¿Esto para que me sirve? (en cristiano)"* para
  quien no sabe si esto le sirve, y *"Primero el plan, despues el reporte"* con
  el plan real de ejemplo. La transcripcion de *Miralo en accion* ahora empieza
  por el plan y su aprobacion.
- **AGENTS.md**: tabla de **trazabilidad** — de donde sale cada decision del
  framework (BPARules de Microsoft, WCAG, Kimball, SQLBI, OpenSpec, superpowers,
  ponytail, skills-for-fabric, power-automate-architect, caveman), y que va
  marcado `[HEURISTICO]` por no tener respaldo.

### Portabilidad verificada

Los scripts corren **sin ninguna variable de entorno de agente**. Los 13 skills
usan `${CLAUDE_PLUGIN_ROOT}` (que resuelve Claude Code); Codex, Gemini CLI,
OpenCode y Cursor operan por `AGENTS.md`, que usa rutas relativas.
Los 5 dominios generan plan + 14 visuales con altText y pasan P1-P9.

## 2026-07-26 — v0.6.0 · el generador produce un reporte, no un esqueleto

La brecha que quedaba no era de codigo: **no existia el conocimiento de diseño**
que el generador tenia que materializar. Ahora vive en `scripts/arquetipos.py`
como datos, y el scaffold construye las paginas desde ahi.

### El salto

| | antes | ahora |
|---|---|---|
| Paginas | 1 | **2** (Resumen + Detalle) |
| Visuales | 3 | **14** |
| Tipos de visual | 3 | **8** (card, line, bar, column, matriz, tabla, slicer, texto) |
| Visuales con `altText` | **0** | **14** |
| Slicers | 0 | **4** |

### Corregido — dos defectos que el conteo hace evidentes

- **`altText` en CERO visuales.** `PBI-A11Y-01` es la regla de MAYOR severidad del
  catalogo de visualizacion, la que la propia reference documenta como la #1, y el
  generador la incumplia en el 100% de lo que producia. Sin alt, un lector de
  pantalla solo anuncia el tipo de visual y el insight se pierde. Ahora el
  constructor de visuales **exige** el alt: `visual()` lanza excepcion si falta.
  Cada ranura de arquetipo declara el suyo, describiendo el **insight** y no el
  aspecto, con el limite duro de 250 caracteres.
- **No habia ningun slicer de `Indicador`.** La medida `Indicador %` esta defendida
  con `HASONEVALUE` y devuelve BLANK si hay mas de un indicador en contexto — asi
  que sin slicer era **una medida que el usuario no podia usar**. Se creo el
  problema en el commit del catalogo y se cierra aqui.

### Añadido

- **`scripts/arquetipos.py`**: el conocimiento de diseño como DATOS.
  - **COOKBOOK** *pregunta → visual*, con la regla y la fuente de cada eleccion
    (por que linea necesita eje continuo, por que barras si los nombres son
    largos, por que una tarjeta necesita contexto). Es la parte SUSTENTADA.
  - **ARQUETIPOS** con ranuras: rol, posicion, y plantilla de texto alternativo.
    El orden de la lista ES el orden de tabulacion, que debe seguir el orden de
    lectura (WCAG 2.4.3).
  - Marcados `heuristico=True` los de negocio, porque **Microsoft no define
    arquetipos de pagina con nombre**; los canonicos (tooltip 320x240,
    drillthrough, movil) si llevan parametros oficiales.
- **`validar_pbip.py` regla P9**: visual sin `altText` es hallazgo ALTA; alt de
  mas de 250 caracteres es MEDIA. Exentos los decorativos (shape, image,
  actionButton). Verificada en los dos sentidos.

### Verificado

- El reporte de 14 visuales pasa el **validador oficial de Microsoft** con
  `succeeded`, 0 errores y 0 avisos.
- Los 5 dominios generan las 2 paginas correctamente.
- C5 volvio a cazar las 8 referencias a `P1-P8` desactualizadas en la doc.

## 2026-07-26 — v0.5.0 · revision previa a pruebas reales

Repaso de extremo a extremo antes de ponerlo en manos de gente. Se ejecutaron
**todos** los comandos que aparecen en la documentacion, literalmente como estan
escritos, y los **5 dominios** (no solo ventas).

### Corregido

- **Contraste de los COLORES DE DATOS, no solo del texto.** `generar_theme.py` y
  `editar_theme.py` reportaban "AA OK" mirando unicamente texto sobre fondo. Pero
  WCAG 1.4.11 pide **>= 3:1** para las partes del grafico necesarias para
  entenderlo. En modo oscuro, el color primario de la marca de ejemplo quedaba a
  **1.97:1** sobre el fondo: una serie practicamente invisible, con el script
  diciendo OK. En modo claro tambien habia dos por debajo del umbral (2.13:1 y
  1.66:1). Ahora ambos scripts lo reportan al generar y al editar.
  Los colores son del usuario, asi que **se avisa, no se cambian en silencio** — y
  el aviso explica las tres salidas por orden de preferencia (aclarar el hex,
  reordenar la paleta, o usar el tema claro). No bloquea el bootstrap.
- **`evals/evals.json` apuntaba a la estructura vieja**: decia que la marca del
  usuario vive en `assets/marca/` del plugin, cuando desde el cambio de estructura
  vive en `<su-proyecto>/docs/marca.json`. Reescrito y ampliado de 2 a **10
  escenarios**, la mitad nacidos de fallos REALES de este ciclo: el MVP huerfano,
  el KPI en 5226%, la regla de visualizacion sin fuente, y la notacion IBCS no
  verificada. Añadidos escenarios de presion (publicar sin validar), de
  enrutamiento entre fases que se solapan, de usuario no tecnico, y de publicar
  sin Git.

### Verificado

- Los **13 comandos** documentados corren sin error tal como estan escritos.
- Los **5 dominios** (generico, ventas, rrhh, finanzas, salud) generan proyectos
  que pasan R1-R12 + 26 reglas oficiales / P1-P8 / E1-E6.
- Bootstrap, los 2 ejemplos versionados y el validador **oficial de Microsoft**:
  0 errores. El unico aviso es `PBIR_THEME_SCHEMA_UNREACHABLE`, ya documentado:
  el CLI v0.1.4 es anterior al schema 2.156.
- Sin fugas de rutas personales en `*.m`, `*.json` ni `*.tmdl`.
- `plugin.json` a **0.5.0** (venia de 0.4.0 con 6 commits y un cambio de
  estructura sin compatibilidad encima).

## 2026-07-26 — fase5-visualizacion.md: de 0 URLs a 20, y cuatro reglas retiradas

La reference que definia el criterio visual **invocaba IBCS con 0 URLs** y
afirmaba como reglas cosas sin fuente. Es decir: el archivo que dice como se hace
un reporte profesional incumplia la regla dura #7 del propio repo.

### Retirado por no tener fuente oficial

- **"Maximo 6-8 visuales por pagina"** — estaba en 4 sitios, uno como item de
  checklist. Microsoft dice literalmente *"limit the number of visuals... to only
  what is necessary"*, **sin numero**. El unico numero oficial es el limite duro
  del servicio: 1 000 visuales por pagina.
- **"Grilla de 8 px"** — Microsoft documenta gridlines y snap-to-grid, pero **no
  publica el paso de la rejilla**.
- **"Patron Z de lectura"** — sin fuente. Lo citable es "lo mas importante
  arriba-izquierda" (Microsoft Learn Training) y el patron F de NN/g.
- **"Pie con maximo 5 categorias"** — la cifra oficial es **3-6 slices**.

### Degradado, no borrado

- **Notacion de escenarios IBCS** (real solido / plan delineado / forecast
  achurado) pasa a `[NO VERIFICADO]`: la regla `UN 3.2 Unify scenarios` existe,
  pero no se leyo su tabla normativa. Se puede proponer como convencion del
  proyecto; no como estandar citado.

### Añadido, con URL

- **Accesibilidad primero**: alt text (limite duro **250 caracteres**), contraste
  de texto **≥4.5:1** (≥3:1 solo si ≥18 pt o ≥14 pt bold), contraste no textual
  **≥3:1**, forma distinta por serie, `tabOrder` explicito. Con enlace al criterio
  WCAG 2.2 concreto, no a la home.
- **Trampa de WCAG 2.5.8**: exige 24×24 **CSS px**, pero el canvas de Power BI
  escala con *Fit to page* — un boton de 24 px de canvas en 1920×1080 sobre un
  viewport de 1280 mide ~16 CSS px y **no cumple**.
- **Limites duros de PBIR**: 1 000 paginas, 1 000 visuales/pagina, 300 MB, y
  **>500 archivos degrada la AUTORIA** (no la lectura).
- **Cookbook pregunta -> visual** con la regla clave de cada uno.
- **Arquetipos separados en dos categorias**, y la distincion importa: los
  **canonicos** (Microsoft los parametriza: tooltip **320×240**, drillthrough,
  movil **323 pt** con tamaños minimos XL/L/M/S) y los **de negocio**, marcados
  `[HEURISTICO]` porque **Microsoft no define arquetipos con nombre** — se
  comprobo recorriendo `guidance/`, las 11 unidades del Training y
  `service-dashboards-design-tips`.
- **IBCS con honestidad**: `/standards/page/N/` si expone el texto gratis (19
  codigos verificados: SA 1-SA 5, ST 1.1-ST 3, EX 1-EX 1.2); el PDF es de socios y
  la licencia se declara "Creative Commons" **sin variante**.
- **Seccion "Sin fuente oficial"** con 13 afirmaciones rechazadas, para que nadie
  las reintroduzca creyendo que se perdieron. Incluye dos correcciones de hecho:
  **no existe Accessibility Checker en Power BI Desktop** (es checklist manual) y
  **la familia `guidance/report-design-*` no existe** (el contenido normativo de
  layout esta en Microsoft Learn **Training**).
- **Rutas PBIR** exactas para automatizar la auditoria del reporte.
- **Deuda de investigacion declarada** (6 puntos), para no confundir "no
  comprobado" con "no aplicable".

### Guarda

- `check_consistencia.py` **C11**: toda reference normativa debe citar al menos una
  fuente con URL. La deuda esta **DECLARADA** en `SIN_CITAS_PENDIENTES` (5
  references) y **solo puede encoger**: si una de ellas empieza a citar, el check
  exige quitarla de la lista. Verificada en los dos sentidos.
- El skill `powerbi-visualizacion` repetia las mismas afirmaciones sin fuente:
  reescrito, y ahora nombra explicitamente las cuatro que no debe usar como regla.

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
