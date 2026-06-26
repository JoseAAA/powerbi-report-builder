# Fase 5 — Visualización y storytelling (IBCS + patrón Z)

> Plantilla viva · actualizado 2026-06 · fuentes: IBCS/SUCCESS (Hichert); Storytelling with Data (Knaflic); Stephen Few · ver `mantenimiento-de-plantillas.md`

Objetivo: páginas que comunican UN mensaje cada una, con notación
consistente, entregadas como especificación de layout o edición PBIR.

## 1. Estructura narrativa de la página (patrón Z)

El ojo occidental recorre: arriba-izquierda → arriba-derecha → diagonal →
abajo-derecha. Asignación de zonas en el lienzo 1280×720:

```
┌────────────────────────────────────────────────┐
│ TÍTULO + mensaje del periodo      filtros/fecha│  y: 0-60
├────────────────────────────────────────────────┤
│ [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]             │  y: 70-180  ← el "qué"
├────────────────────────────────────────────────┤
│ Visual principal (tendencia       │ Ranking /  │  y: 190-540 ← el "porqué"
│ o comparación vs meta)            │ composición│
├────────────────────────────────────────────────┤
│ Detalle / tabla con drill-through              │  y: 550-710 ← el "dónde actuar"
└────────────────────────────────────────────────┘
```

- El título NO es "Dashboard de Ventas": es el mensaje — "Ventas crecen 8%
  pero el margen cae en 2 categorías". Si el mensaje cambia con los datos,
  usa un título dinámico (medida DAX de texto).
- 1 mensaje por página. 6-8 visuales máximo. Lo que no quepa: página de
  exploración o drill-through.
- Grilla de 8 px; alinear bordes; mismo alto para tarjetas hermanas.

## 2. IBCS — fórmula SUCCESS aplicada a Power BI

| Regla | En la práctica |
|---|---|
| **Say** | Cada página y cada visual tiene un mensaje, no solo un tema. Título de visual = hallazgo ("Lima concentra 60% del gasto"), no descripción ("Gasto por sede"). |
| **Unify** | Notación semántica consistente en TODO el reporte: **Real = sólido**, **Presupuesto/Plan = delineado (outline)**, **Forecast = achurado/punteado**. Varianza positiva verde, negativa roja (ojo: un AUMENTO de costos es varianza negativa → rojo). Mismo color = mismo significado en todas las páginas. |
| **Condense** | Densidad útil: small multiples sobre 6 gráficos sueltos; etiquetas directas sobre leyendas cuando hay ≤3 series. |
| **Check** | Ejes que parten de cero en barras; misma escala en gráficos comparables lado a lado; no truncar ejes para dramatizar. |
| **Express** | El gráfico correcto: tendencia→línea; comparación entre categorías→barras horizontales ordenadas; composición→barras apiladas 100% o treemap (NO pie con >4 porciones); relación→dispersión; vs meta→bullet chart o barra con línea de meta. |
| **Simplify** | Quitar: bordes, sombras, fondos por visual, gridlines densas, decimales innecesarios, leyendas redundantes. Data-ink ratio alto. |
| **Structure** | Jerarquía visual del Z; navegación consistente (mismos filtros en el mismo lugar en todas las páginas). |

## 3. Tipos de página

- **Resumen ejecutivo** (default): el layout Z de arriba; responde "¿cómo
  vamos y dónde mirar?".
- **Exploración**: slicers ricos + visuales interactivos; para analistas.
- **Detalle / drill-through**: tabla con contexto desde el visual de origen.
- Regla: ejecutivos NO deberían necesitar tocar un slicer para entender la
  página de resumen.

## 4. Especificación de layout (entregable cuando no hay PBIP)

Por cada página, entrega una tabla:

| # | Visual | Tipo | Posición (x,y,w,h) | Medidas/campos | Mensaje |
|---|---|---|---|---|---|
| 1 | KPI Ventas | card | 40,70,280,100 | [Ventas Totales], [Var % vs LY] | crecimiento del mes |

Más: título de página, filtros de página, interacciones a desactivar.

## 5. Edición directa de PBIR (cuando el usuario sube su proyecto)

Lee primero `references/formatos-pbip.md`. Operaciones seguras:

- **Reposicionar/alinear**: editar `position` en cada `visual.json`. Útil
  para aplicar la grilla de 8 px a todo el reporte por script.
- **Estandarizar títulos**: `visual.visualContainerObjects.title` →
  `properties.text` (literal con comillas escapadas: `"'Texto'"`).
- **Copiar un visual a otra página**: copiar la carpeta del visual y
  generar un `name` nuevo de 20 caracteres hex para la copia (la ÚNICA
  excepción a "no tocar name": objetos NUEVOS necesitan name nuevo único).
- **Reordenar páginas**: `pages/pages.json` → `pageOrder`.
- Tras editar: validar cada JSON modificado y recordar al usuario abrir el
  .pbip en Desktop para verificación visual.

## 6. Accesibilidad y últimos retoques

- Orden de tabulación de visuales = orden de lectura.
- Texto alternativo en visuales clave.
- Tooltips con la definición del indicador (de la ficha de fase 3) para
  gobernanza de datos.
- Página oculta "Guía" con definiciones de cada KPI: barata de hacer y
  evita el 80% de las preguntas de "¿esto qué significa?".

## 7. Novedades 2026 (usalas cuando aporten)

- **Visual calculations (GA mayo 2026):** calculos sobre el resultado visible del visual (running total, % del total, moving average) sin crear medidas ni columnas. Para calculos de presentacion que no se reusan; deja en el modelo las medidas reutilizables.
- **Style presets en el theme:** estilos nombrados por tipo de visual (card destacada vs normal, textbox titulo/callout/cuerpo) aplicables desde el dropdown de estilo. Ver fase1-branding.
- **Exploration / perspectives:** vista de exploracion que expone un subconjunto del modelo sin recargar la pagina de resumen.

Fuente: Power BI March/May 2026 feature summaries (Microsoft Power BI Blog).
