# Mantenimiento de plantillas vivas

> Plantilla viva · actualizado 2026-06 · fuentes: Microsoft Learn; este skill

Las **plantillas** del skill (las `references/*.md` y los `assets/`) no son
estáticas: se mantienen **vigentes y trazables a fuentes oficiales**. Esto es lo
que hace que la herramienta dé "los mejores resultados que existen hoy" sin
inventar nada.

## Principio: no inventar, citar y actualizar

1. **Cada recomendación traza a una fuente** (documentación de Microsoft o un
   experto reconocido). Si no hay fuente, márcalo como *heurística* o quítalo.
   No escribas "mejor práctica" sin respaldo.
2. **Cada plantilla declara su vigencia** con un encabezado, justo bajo el título:
   ```
   > Plantilla viva · actualizado AAAA-MM · fuentes: <2-4 fuentes clave>
   ```
3. **Todo cambio de criterio se registra** en `CHANGELOG.md` (raíz del skill) con
   fecha y la fuente que lo motivó.

## Cómo actualizar una plantilla

1. Revisa la **fuente canónica** (lista abajo) para el tema.
2. Ajusta el contenido de la `reference`/`asset` y, si cambió un criterio,
   actualiza también el script o validador que lo aplica (`validar_modelo.py`,
   `generar_theme.py`, etc.).
3. Sube `actualizado: AAAA-MM` en el encabezado.
4. Anota en `CHANGELOG.md`: fecha · qué cambió · fuente.

## Fuentes canónicas a vigilar (por área)

| Área | Fuente oficial / experto |
|---|---|
| Power BI / Fabric / PBIP / TMDL / PBIR | **Microsoft Learn** + `microsoft/powerbi-desktop-samples`, `microsoft/skills-for-fabric` |
| Modelado dimensional (estrella) | **Kimball Group** |
| DAX y nomenclatura | **SQLBI** (Russo/Ferrari) · **Tabular Editor BPA** (equipo Power BI CAT) |
| Power Query / M / query folding | **Chris Webb** + guía oficial de Power Query |
| Visualización / storytelling | **IBCS / SUCCESS** (Hichert) · *Storytelling with Data* (Cole Nussbaumer Knaflic) · Stephen Few |
| Color / accesibilidad | **WCAG** (W3C) · ColorBrewer (Cynthia Brewer) |
| Descubrimiento / KPIs / OKR | Design Sprint (Google Ventures) · *Measure What Matters* (Doerr) · Balanced Scorecard (Kaplan & Norton) |
| Arquitectura del skill | **Anthropic Agent Skills** |

## Acumulación por uso (el skill "aprende")

Cada vez que se usa, se guardan ejemplos reales (anonimizados) en `assets/ejemplos/`:
marcas (`assets/marca/<empresa>.json`), fichas KPI buenas y descubrimientos. Así
crece una biblioteca de referencia sin re-preguntar ni re-derivar.

## Opción futura (no en el core hoy)

Un agente programado (`/schedule`) que revise periódicamente las fuentes y proponga
bumps de `actualizado:`. Se deja fuera por ahora para no añadir dependencia ni
complejidad; el flujo manual de arriba es suficiente y determinista.
