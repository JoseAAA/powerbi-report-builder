# Fase 5 — Visualización y storytelling

> Plantilla viva · actualizado 2026-07-26 · **toda regla normativa lleva URL**.
> Lo que no tiene fuente citable va marcado `[HEURÍSTICO]` o `[NO VERIFICADO]` y
> **no es exigible**. Fuentes: Microsoft Learn (docs + Training), W3C/WCAG 2.2,
> IBCS (parte pública), NN/g, Perceptual Edge, ColorBrewer.
> Ver `mantenimiento-de-plantillas.md` y `estado-fuentes.json`.

Objetivo: páginas que comunican UN mensaje cada una, con notación consistente,
entregadas como especificación de layout o como edición PBIR.

## 0. Lo que esta reference corrigió de sí misma (2026-07)

Cuatro cosas que llevaba **como reglas** y no tienen fuente oficial. Están aquí
para que nadie las reintroduzca creyendo que se perdieron:

| Retirado | Por qué |
|---|---|
| ~~"6-8 visuales máximo por página"~~ | Microsoft dice *"limit the number of visuals… to only what is necessary"* — **sin número**. El único límite numérico oficial es el duro del servicio: **1 000 visuales por página** |
| ~~"no pie con más de 5 categorías"~~ | La cifra oficial es **3–6 slices** |
| ~~"grilla de 8 px"~~ | Microsoft documenta gridlines y snap-to-grid, pero **no publica el paso de la rejilla** |
| ~~"patrón Z" como estructura narrativa~~ | No hay fuente. Lo citable es *"lo más importante arriba-izquierda"* (Training) y el **patrón F** de NN/g |

Y una que hay que degradar, no borrar: la **notación de escenarios IBCS**
(Real sólido / Plan delineado / Forecast achurado) pasa a `[NO VERIFICADO]` — la
regla `UN 3.2` existe, pero no se leyó su tabla normativa. Ver §6.

Lista completa al final, en §8.

---

## 1. Accesibilidad — primero, no al final

**No existe Accessibility Checker en Power BI Desktop.** Lo que hay es un
checklist manual, y por eso estas reglas hay que aplicarlas a mano.
[desktop-accessibility-creating-reports](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports)

| Regla | Exigencia exacta | Fuente |
|---|---|---|
| **Alt text** en todo visual que transmita información | Describe el **insight**, no el aspecto (el lector ya anuncia título y tipo). Límite duro **250 caracteres**. Si el valor manda, usa `fx` con una medida en vez de texto estático | [MS accessibility](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports) |
| **Contraste de texto ≥ 4.5:1** | ≥3:1 solo si el texto es ≥18 pt, o ≥14 pt en negrita | [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum) |
| **Contraste no textual ≥ 3:1** | Controles y las partes del gráfico **necesarias** para entenderlo | [WCAG 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) |
| **El color nunca es el único canal** | Forma **distinta por serie** en línea, área, combo y scatter; o etiqueta directa | [WCAG 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color) |
| **`tabOrder` explícito** y coherente con el orden de lectura | Los elementos decorativos van **fuera** del tab order | [WCAG 2.4.3](https://www.w3.org/WAI/WCAG22/Understanding/focus-order) |

**Trampa de WCAG 2.5.8 (Target Size).** Exige **24×24 CSS px**, pero el canvas de
Power BI **escala** con *Fit to page*: un botón de 24 px de canvas en un lienzo
1920×1080 mostrado en un viewport de 1280 mide ~16 CSS px y **no cumple**. Corrige
por el factor de escala antes de dar un tamaño por bueno.
[WCAG 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum) ·
[display settings](https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-report-display-settings)

**Versión:** WCAG 2.2 es Recommendation del W3C desde el 12-dic-2024; Microsoft
aún cita 2.1 en su checklist. Los criterios 1.1.1, 1.4.1, 1.4.3, 1.4.11 y 2.4.3
son **idénticos** entre 2.1 y 2.2; **2.5.8 es nuevo en 2.2**.

Paletas seguras para daltonismo: [ColorBrewer](https://colorbrewer2.org/).

---

## 2. Límites duros del formato (no son estilo, son el producto)

[projects-report § considerations and limitations](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)

- **1 000 páginas** por reporte · **1 000 visuales** por página
- **1 000** archivos de resource package · **300 MB** de resource packages ·
  **300 MB** de todos los archivos del reporte
- **> 500 archivos**: degrada el rendimiento **de autoría** (no el de lectura)
- Tablas y matrices: aplica **Top N** o el filtro más restrictivo que la pregunta
  permita. [power-bi-optimization](https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization)

---

## 3. Estructura de la página

Lo **citable**: lo más importante **arriba-izquierda** en idiomas LTR
(arriba-derecha en RTL) — Microsoft Learn Training *Design effective reports*, y
el [patrón F de NN/g](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/).

`[HEURÍSTICO]` La plantilla de abajo es **nuestra**, no de Microsoft. Es un punto
de partida razonable para un lienzo 1280×720, no una norma:

```
┌────────────────────────────────────────────────┐
│ TÍTULO = el mensaje              filtros/fecha │  y: 0-60
├────────────────────────────────────────────────┤
│ [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]             │  y: 70-180   ← el "qué"
├────────────────────────────────────────────────┤
│ Visual principal (tendencia       │ Ranking /  │  y: 190-540  ← el "porqué"
│ o comparación vs meta)            │ composición│
├────────────────────────────────────────────────┤
│ Detalle / tabla con drill-through              │  y: 550-710  ← "dónde actuar"
└────────────────────────────────────────────────┘
```

Reglas **con fuente** que sí aplican al layout:

| Regla | Fuente |
|---|---|
| Bordes alineados: gridlines, snap-to-grid, smart guides y Align/Distribute | [gridlines-snap-to-grid](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-gridlines-snap-to-grid) |
| Canvas **explícito y el mismo** en todas las páginas (16:9 — 1280×720 o 1920×1080) | [display settings](https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-report-display-settings) |
| Slicers **en la misma posición en cada página** | Training |
| Tema aplicado y **cero hex sobrescritos por visual** | [report themes](https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom) |
| La conclusión clave **no puede depender de una interacción**: pre-filtra | checklist de accesibilidad de Microsoft |

Principios de composición citables (Training): colocación, balance —incluida la
**regla de tercios**, y la proporción áurea como *concepto guía*, no como
medida—, proximidad, contraste, repetición, espacio, tamaño, alineación, color y
consistencia.

**El título dice la conclusión, no el tema.** No "Dashboard de Ventas", sino
"Ventas crecen 8% pero el margen cae en 2 categorías". Si el mensaje cambia con
los datos, título dinámico con una medida DAX de texto.

`[HEURÍSTICO]` Densidad: si un visual no responde a la pregunta de la página,
sobra. Microsoft no publica un máximo — no lo inventes.

---

## 4. Elegir el visual — pregunta → visual

De [visualization types](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a),
del Training *Design effective reports* y de la página de cada visual.

| La pregunta del negocio | Visual | Regla clave |
|---|---|---|
| ¿Cuánto, comparando categorías? | `clusteredBarChart` si los nombres son largos; `clusteredColumnChart` para comparar periodos | barras y columnas son mejores para **comparar valores** |
| ¿Cómo evoluciona en el tiempo? | `lineChart` | necesita **eje X continuo**; con periodos sin dato la línea **inventa** tendencia → usa columnas |
| ¿Magnitud del cambio acumulado? | `areaChart` / `stackedAreaChart` | |
| ¿Dos métricas de escalas distintas? | `lineClusteredColumnComboChart` | admite uno o dos ejes Y |
| ¿Cambió el ranking? | `ribbonChart` | el valor más alto arriba en cada periodo |
| ¿Qué explica el delta? | `waterfallChart` | total acumulado con sumas y restas |
| ¿Parte de un todo? | `hundredPercentStackedBarChart`; `pieChart`/`donutChart` **solo con 3–6 slices** | no mezclar positivos y negativos en un pie |
| ¿Jerarquía con proporciones? | `treemap` | |
| ¿Conversión por etapas? | `funnel` | |
| ¿Correlación, clusters, outliers? | `scatterChart` | bubble para una 3ª dimensión |
| ¿Valores exactos? | `tableEx`; `pivotTable` si cruzas dimensiones y necesitas drill | |
| ¿Un solo número que importa? | `cardVisual` | **dale contexto**: un número solo no dice si es bueno |
| ¿Progreso hacia una meta, con tendencia? | `kpi` | requiere valor + objetivo + umbral; **ordena antes** de convertir |
| ¿Estado contra meta, sin tendencia? | `gauge` | con moderación: los tipos circulares no son ideales |
| ¿Qué dimensión explica la métrica? | `decompositionTreeVisual` | |
| ¿Qué factores influyen? | `keyDriversVisual` | |
| ¿El mismo patrón entre categorías? | **small multiples** sobre el visual base | |
| ¿Dónde ocurre? | `map` si los puntos están dispersos; `filledMap` por área administrativa | |
| ¿Referencia, promedio, percentil, pronóstico? | panel **Analytics** del visual | |
| ¿Cálculo propio del visual (running total, % del total)? | **visual calculations** | |

**Nunca gráficos 3D.** [dashboards-design-tips](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips)

**Ciclo de vida verificado:** el visual **Q&A (`qnaVisual`) se depreca en
diciembre de 2026** — no lo pongas en plantillas nuevas.

---

## 5. Arquetipos de página

**Microsoft no define arquetipos de página con nombre.** Se comprobó recorriendo
el índice completo de `guidance/`, las 11 unidades del Training y
`service-dashboards-design-tips`. La distinción siguiente importa:

### 5.1 Canónicos — Microsoft los parametriza

| Arquetipo | Parámetros **oficiales** | Fuente |
|---|---|---|
| **Página tooltip** | `Type = Tooltip`; **320 × 240 px**; diseñar en *Actual Size*; mismo tema; quitar los filtros de diseño antes de publicar; **siempre oculta**; **sin elementos interactivos** (ni slicers, ni botones, ni scroll) | [report-page-tooltips](https://learn.microsoft.com/en-us/power-bi/guidance/report-page-tooltips) |
| **Página drillthrough** | Mismo tema; sin filtros de diseño; **oculta**; **conservar el back button automático**; evitar visuales que den BLANK o error al aplicar el filtro | [report-drillthrough](https://learn.microsoft.com/en-us/power-bi/guidance/report-drillthrough) |
| **Layout móvil** | Flujo top→bottom; ancho máximo **323 pt**; **no** visuales lado a lado (salvo card/KPI/botones); gap **6–8 pt**; fuente **≥9 pt**; tamaños mínimos **XL 323×270**, **L 323×180**, **M 323×100**, **S 158×100 pt**; sin scrollbars dentro de los visuales | Microsoft Learn (mobile-optimized reports) |

### 5.2 De negocio — `[HEURÍSTICO]`, compuestos por nosotros

**No tienen fuente oficial como arquetipos.** Se apoyan en los principios de
composición del Training, pero la receta concreta es nuestra: dilo si el usuario
pregunta de dónde sale.

- **Resumen ejecutivo** — banda de KPIs arriba, tendencia principal, un desglose.
  Para quien decide y no explora.
- **Monitor operativo** — estado actual contra umbral; primero lo que requiere
  acción; refresco frecuente.
- **Análisis exploratorio** — slicers prominentes, drill y decomposition tree;
  densidad alta aceptable porque el lector viene a investigar.
- **Comparativa / benchmark** — mismo eje y misma escala entre lo que se compara;
  small multiples antes que N gráficos sueltos.

---

## 6. IBCS — qué es citable y qué no

La raíz `ibcs.com/standards/` solo muestra el gráfico SUCCESS, pero
**`/standards/page/N/` (62 páginas) sí expone el texto de las reglas gratis**. Se
verificaron literalmente 19 códigos y títulos: `SA 1`–`SA 5`, `ST 1.1`–`ST 3`,
`EX 1`–`EX 1.2`. El PDF completo es solo para miembros, y la licencia se declara
"Creative Commons" **sin especificar la variante**.

`[NO VERIFICADO]` **No prescribas la notación de escenarios IBCS** — el típico
"Real = sólido, Plan = delineado, Forecast = achurado". La regla `UN 3.2 Unify
scenarios` existe, pero **no se leyó su tabla normativa**. Puedes proponerla como
convención del proyecto si el usuario la acepta; no la presentes como estándar
citado.

Principios usables con su nombre correcto: **UNIFY** (misma cosa, misma
apariencia, en todas las páginas), **CONDENSE** (densidad útil: small multiples
antes que gráficos sueltos; etiquetas directas antes que leyenda con ≤3 series),
**CHECK** (ejes desde cero en barras, misma escala en comparables lado a lado, no
truncar para dramatizar), **SIMPLIFY** (quitar lo que no aporta).

---

## 7. Storytelling

Citable con URL pública: el **blog** de
[Storytelling with Data](https://www.storytellingwithdata.com/blog) y la
biblioteca gratuita de **Perceptual Edge** (Stephen Few), cuyos PDF sí son
enlazables. Los **libros** de Knaflic y Few **no** son fuente citable con URL:
Microsoft los recomienda por nombre, lo que los valida como bibliografía, no como
`fuente_url`.

Principios aplicables: un mensaje por página; el título dice la conclusión; quita
lo que no aporta (*declutter*); dirige la atención con contraste antes que
añadiendo color.

---

## 8. Sin fuente oficial — no lo uses como regla

| Afirmación frecuente | Estado |
|---|---|
| "Máximo 5–8 visuales por página" | **sin fuente** (Microsoft: "only what is necessary"; único número oficial: 1 000) |
| "Regla de los 5 segundos" | **sin fuente** |
| "Data-ink ratio ≥ X" | Tufte solo en libro; ningún umbral es citable |
| "Rejilla de 8 px / 12 columnas" | Microsoft documenta la rejilla, **no su paso** |
| "Proporción áurea 1.618 exacta entre bloques" | el Training lo menciona como concepto, no prescribe medidas |
| "Patrón Z de lectura" | **sin fuente**; lo citable es "arriba-izquierda primero" y el patrón F de NN/g |
| "Notación IBCS: negro=Actual, gris=PY, hachurado=Plan" | **no verificado**: falta leer la tabla de `UN 3.2` |
| "IBCS es CC-BY-SA" | IBCS dice "a Creative Commons license" sin variante |
| "Las gridlines deben cumplir 3:1 (WCAG 1.4.11)" | sobre-interpretación: difícilmente son partes **necesarias** para entender el contenido |
| "24×24 px de canvas cumple WCAG 2.5.8" | **falso por escalado** — ver §1 |
| "Existe un Accessibility Checker en Power BI Desktop" | **no existe**; hay checklist manual |
| "La familia `guidance/report-design-*` de Microsoft" | **no existe**: el contenido normativo de layout está en Microsoft Learn **Training** |
| `pageInformationAltName` como alt text de página | la propiedad **existe** en el esquema `page` 2.1.0, pero **no hay página de Learn que documente su semántica** |

---

## 9. Rutas PBIR para auditar (esquemas oficiales)

| Qué | Ruta JSON | Esquema |
|---|---|---|
| Alt text del visual | `visual.visualContainerObjects.general[].properties.altText` | `visualContainer` 2.9.0 |
| Orden de tabulación | `position.tabOrder` | `visualContainer` 2.9.0 |
| Título del visual | `visualContainerObjects.title[].properties.heading` | `visualContainer` 2.9.0 |
| Tamaño de página | `page.objects.pageSize.properties.pageSizeTypes` | `page` 2.1.0 |
| Página oculta | `page.visibility` | `page` 2.1.0 |
| Estilos de página del tema | `visualStyles.page` | theme schema 2.156 |

El esquema de temas declara **42 propiedades raíz** y **14 `textClasses`**; hay
**52 `visualType`** válidos. **Nunca inventes claves de tema**: el validador
oficial las rechaza (`PBIR_THEME_VISUAL_PROP_UNKNOWN`) — así se descubrió que
`visualHeaderTooltip` no era válida y estaba en todos nuestros temas generados.

**Regla del `$schema`:** al editar, **preserva el valor existente**; al crear un
archivo nuevo, **copia el `$schema` de un archivo hermano del mismo tipo**. No
inventes ni subas versiones por tu cuenta.

---

## 10. Deuda de investigación declarada

Para no confundir "no comprobado" con "no aplicable":

1. **IBCS `/standards/page/N/`** — leer UNIFY (notación de escenarios), CHECK,
   CONDENSE y SIMPLIFY, y capturar la variante exacta de la licencia CC. Es la
   pieza que falta para poder prescribir notación IBCS con fuente.
2. `pageInformationAltName`: buscar la página de Learn que lo documente.
3. WCAG 2.4.6, 1.4.12, 1.4.10 y 2.4.7, para cerrar el bloque de accesibilidad.
4. Esquemas `formattingObjectDefinitions` y `filterConfiguration`: detectar con
   precisión color literal vs `ThemeDataColor`, y la presencia de Top N.
5. `visualContainerMobileState` (`mobile.json`) para automatizar las reglas de
   layout móvil.
6. **Base theme Fluent 2** sigue en preview; al llegar a GA cambia varios defaults
   (títulos y subtítulos on, axis titles off, más padding) y con ellos las
   expectativas de varias reglas de tipografía y layout.
