# Marca activa (archivo intercambiable)

Esta carpeta guarda la **identidad visual por empresa** como archivos de
"design tokens" (colores, fuentes, tamaños, fondos). Es el lugar donde el
skill **recuerda los colores de la marca de una vez** para no volver a
preguntarlos en cada reporte.

> **Una instalación nueva NO trae ninguna marca activa.** El skill es genérico:
> en la Fase 1 captura la marca de *tu* empresa. Los archivos en `ejemplos/` son
> solo muestras (`activa: false`) para ver cómo se llena uno.
>
> **Tu marca vive en TU proyecto** (p. ej. `mi-reporte/docs/marca.json`),
> no dentro del plugin: los plugins se actualizan y borran lo guardado dentro.
> Esta carpeta del plugin solo aporta la **plantilla** y los **ejemplos**.

## Cómo funciona

1. El skill, al entrar a la fase de branding, **busca un archivo con
   `"activa": true`** en esta carpeta (ignora `ejemplos/`).
   - **Si lo encuentra** → le dice al usuario qué marca tiene guardada, citando
     sus colores reales, y confirma antes de usarla.
   - **Si no hay ninguna activa** (lo normal en una instalación nueva) → captura
     la marca de la empresa del usuario (logo, presentación/`.thmx`, manual,
     `.pbip` o hex) y propone guardarla como `<empresa>.json` con `activa: true`.
2. Con la marca lista → genera el `theme.json` con
   `scripts/generar_theme.py --marca <archivo>`.

## Archivos

| Archivo | Qué es |
|---|---|
| `_plantilla-marca.json` | **Punto de entrada**: plantilla para crear la marca de tu empresa (`activa: false`). |
| `ejemplos/ejemplo-corporativo.json` | Marca de **ejemplo** genérica bien llenada, para referencia (`activa: false`). |
| `<empresa>.json` | La marca que tú crees y actives (no viene incluida). |

## Crear / cambiar la marca activa

- **Tu empresa:** copia `_plantilla-marca.json` → `<empresa>.json`, llena los hex,
  pon `"activa": true` en ese archivo. **Solo un archivo debe estar activo a la
  vez** (los de `ejemplos/` siempre quedan en `false`).
- **Cambios puntuales** sobre un theme ya generado ("cambia el azul", "ponlo
  oscuro"): usa `scripts/editar_theme.py`.

## Estructura del archivo de marca

- `colores.primario` — color de marca dominante (medida principal, acentos).
- `colores.paletaDatos` — 8 colores para series de gráficos (`dataColors`).
- `colores.semaforo` — bueno / neutral / malo (KPI, varianzas, formato condicional).
- `colores.texto` — principal / secundario / atenuado (clases estructurales).
- `colores.fondo` — página / visual / grid.
- `colores.rampa` — máximo / centro / mínimo / nulo (formato condicional por gradiente).
- `tipografia` — familia, familia de títulos y tamaños base (callout/title/header/label).
- `modo` — `claro` u `oscuro`.

> Este archivo NO es el theme de Power BI. Es la **fuente de verdad** de la
> marca; `generar_theme.py` lo traduce al `theme.json` que Power BI importa
> (con `dataColors`, colores estructurales, `textClasses` y `visualStyles`).
> Separar ambos permite reusar la misma marca en muchos reportes y cambiar de
> empresa sin tocar la lógica del tema.
