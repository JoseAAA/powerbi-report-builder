# Fase 1 — Marca y tema visual (theme.json)

> Plantilla viva · actualizado 2026-06 · fuentes: WCAG (W3C); ColorBrewer (C. Brewer); theme schema (Microsoft) · ver `mantenimiento-de-plantillas.md`

Objetivo: producir o modificar un `theme.json` valido, accesible y reutilizable,
generado desde un **archivo de marca guardado** (`assets/marca/<empresa>.json`).

## El flujo de colores (orden obligatorio)

1. **Lee la marca guardada.** Busca en `assets/marca/` el archivo con
   `"activa": true` y dile al usuario que marca tienes, en lenguaje claro.
2. **Confirma.** ¿Son los colores de su empresa?
   - Si → genera el tema (abajo) y entrega.
   - No / otra empresa → **captura** la paleta interactuando (logo, manual,
     .pbip/theme.json existente, o hex directos) y al final **propon guardar**
     la marca nueva (`_plantilla-marca.json` → `<empresa>.json`, `activa: true`).
3. La logica completa esta en `assets/marca/README.md`.

### Generar el tema desde la marca

```bash
python scripts/generar_theme.py --marca assets/marca/<empresa>.json --salida theme.json
```

Produce un `theme.json` con `$schema`, `dataColors`, colores estructurales,
semaforos, rampa de formato condicional, `textClasses` y `visualStyles`, y
verifica contraste WCAG. Sin archivo de marca puedes pasar colores sueltos
(`--primario`, `--paleta`, `--fuente`, `--modo`).

### Capturar la marca cuando no esta guardada

- **Manual de marca:** pide hex de primario, secundarios, acentos y la fuente.
- **Solo logo / web:** analiza la imagen, propone la paleta extraida y CONFIRMA
  los hex antes de generar.
- **.pbip / theme.json existente:** extrae `dataColors` y colores estructurales.
- **Sin marca definida:** usa el cuestionario y propon 2-3 paletas accesibles.

### Cuestionario cuando no hay marca

- ¿Sector y tono? (salud→confianza/calma; finanzas→sobriedad; retail→energia)
- ¿Un color que SI y uno que NO?
- ¿Se proyecta en sala, se lee en laptop, o ambos?
- ¿Audiencia con daltonismo conocido? (usa paleta segura para deuteranopia)

## Estructura del theme JSON (solo propiedades estandar)

Power BI ignora silenciosamente lo que no reconoce; el unico campo requerido es
`name`. Usa el `$schema` oficial para autocompletar y validar en VS Code.

```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.156.json",
  "name": "Tema de ejemplo",
  "dataColors": ["#1B4D77","#E25822","#50C878","#1987EC","#E1C955","#6B7A8F","#1076AA","#9C5BA8"],
  "good": "#2E8B57", "neutral": "#E1A30B", "bad": "#C0392B",
  "maximum": "#1B4D77", "center": "#84A9C0", "minimum": "#DCE6EF", "null": "#B3B0AD",
  "firstLevelElements": "#252423",
  "secondLevelElements": "#605E5C",
  "thirdLevelElements": "#DBE3EA",
  "fourthLevelElements": "#8A8886",
  "background": "#FFFFFF",
  "secondaryBackground": "#EAEFF4",
  "tableAccent": "#1B4D77",
  "textClasses": { },
  "visualStyles": { }
}
```

### Colores estructurales (que controla cada uno)

| Propiedad | Tambien llamada | Controla |
|---|---|---|
| `firstLevelElements` | foreground | texto principal: data labels, valores de tabla, callouts de card, titulos |
| `secondLevelElements` | foregroundNeutralSecondary | texto secundario: leyendas, ejes, encabezados de tabla |
| `thirdLevelElements` | backgroundLight | gridlines, grid de tabla, relleno de formas |
| `fourthLevelElements` | foregroundNeutralTertiary | atenuado: leyenda dimmed, categoria de card |
| `background` | — | fondo de visuales, items de dropdown, tooltips |
| `secondaryBackground` | backgroundNeutral | borde de grid de tabla, separadores |
| `tableAccent` | — | acento/borde de tablas y matrices |
| `good`/`neutral`/`bad` | — | KPI, waterfall, varianzas, formato condicional |
| `maximum`/`center`/`minimum`/`null` | — | gradientes de formato condicional |

### dataColors

- 8 colores minimo (Power BI cicla y autogenera si hay mas series).
- Color 1 = protagonista (medida principal).
- Alterna por contraste; serie 1 y 2 deben diferir en luminosidad (daltonismo),
  no solo en matiz.

### textClasses (4 primarias; las demas derivan)

```json
"textClasses": {
  "callout": { "fontFace": "Segoe UI Semibold", "fontSize": 34, "color": "#252423" },
  "title":   { "fontFace": "Segoe UI Semibold", "fontSize": 14, "color": "#252423" },
  "header":  { "fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#252423" },
  "label":   { "fontFace": "Segoe UI", "fontSize": 10, "color": "#252423" }
}
```

`callout` = numero grande de las cards; `label` = ejes/leyendas/valores. Fuentes
seguras: Segoe UI, Arial, Calibri, Tahoma, Verdana. Una fuente corporativa NO
instalada hace fallback feo: usa la mas parecida de la lista y dilo.

## Novedades 2026 (usalas cuando aporten)

- **Style presets:** un mismo visual puede tener varios presets nombrados en el
  theme (`visualStyles.<visual>.<preset>`), que aparecen en un dropdown del
  panel de formato. Utiles para "tarjeta destacada" vs "tarjeta normal", o
  estilos de textbox (titulo / callout / cuerpo). Define lo comun en el preset
  `"*"` y solo las diferencias en los nombrados.
- **Modern visual defaults (preview):** nuevos defaults de chart y mas presets;
  Microsoft publica el JSON base para modificar. Recomienda probar con el
  generador GMBH (themegenerator.point-gmbh.com) o PowerUI como UI visual.
- El generador del skill ya incluye un preset de ejemplo `"Callout Destacado"` en card.

## Accesibilidad (no negociable)

- Texto normal sobre su fondo: contraste >= 4.5:1 (WCAG AA); callouts >= 3:1.
- `generar_theme.py` calcula el ratio y ajusta el texto si falla.

## Editar un tema existente (`editar_theme.py`)

Cambios puntuales sin perder el resto (quirurgico). Operaciones combinables:
`--primario`, `--color-dato "N:#hex"`, `--bueno/--malo/--neutral`, `--fuente`,
`--modo claro|oscuro`, `--texto`, `--fondo`, `--fondo-pagina`, `--nombre`.
Reverifica contraste y, en modo guiado, traduce el "antes → despues" a una frase.

## Validacion y entrega

- Schema oficial versionado por release mensual en
  `microsoft/powerbi-desktop-samples` (carpeta "Report Theme JSON Schema").
  Ajusta el numero del `$schema` a la version del Desktop del usuario si lo sabe.
- Importar: Power BI Desktop → **Vista** → **Temas** → **Buscar temas** → el json.
- En PBIP: el tema va en `Report/StaticResources/RegisteredResources/` y se
  referencia en `report.json` (`themeCollection.customTheme`). El
  `scaffold_pbip.py` ya lo hace si pasas `--tema`.

## Errores comunes

- 3-4 dataColors → series repetidas en graficos grandes.
- Olvidar `good/bad/neutral` → semaforos con colores default que chocan.
- Rojo corporativo como color principal → todo "grita alerta"; reservalo para
  varianzas negativas.
- Fondo de pagina blanco puro + visual blanco puro → tarjetas no se distinguen;
  usa fondo de pagina gris muy claro (#F5-#F8).

## Fuentes

- Microsoft Learn — *Create custom report themes*: https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom
- Report Theme JSON Schema: https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema
- Modern visual defaults (preview): https://powerbi.microsoft.com/en-us/blog/deep-dive-into-modern-visual-defaults-and-customizing-theme-improvements-preview/
