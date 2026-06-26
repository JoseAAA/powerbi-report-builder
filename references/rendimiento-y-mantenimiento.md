# Rendimiento y mantenimiento del modelo

> Plantilla viva · actualizado 2026-06 · fuentes: SQLBI / VertiPaq Analyzer; DAX Studio; Microsoft (optimization guide); Tabular Editor BPA · ver `mantenimiento-de-plantillas.md`

Objetivo: un modelo **rápido hoy y fácil de mantener mañana**. El motor de Power BI
es **VertiPaq** (columnar, en memoria): el rendimiento depende sobre todo del
tamaño y la cardinalidad de las columnas, no del número de filas.

## 1. VertiPaq — lo que más pesa (en orden de impacto)

| Práctica | Por qué | Cómo |
|---|---|---|
| **Quita columnas que no uses** | cada columna ocupa memoria aunque nadie la mire | elimínalas en Power Query (lo antes posible) |
| **Baja la cardinalidad** | columnas con muchos valores únicos no comprimen | evita IDs/GUIDs y decimales innecesarios; redondea |
| **Separa fecha y hora** | un datetime al segundo = cardinalidad altísima | columna Fecha (date) + columna Hora aparte si hace falta |
| **Tipos correctos y mínimos** | int comprime mejor que texto/decimal | fija tipos en M; usa enteros para claves |
| **Oculta claves y columnas técnicas** | limpieza + evita usos incorrectos | `isHidden` en claves del hecho y columnas Num/Den |
| **Evita relaciones bidireccionales** | recalculan en ambos sentidos, lentas y ambiguas | usa single + `CROSSFILTER`/`TREATAS` puntual si hace falta |
| **Evita columnas calculadas** sobre el hecho | se materializan y pesan | hazlo en M (folding) o como medida |

## 2. Modos y refresco (escala)

- **Import** comprime y es rápido; refresco programado. Default.
- **DirectQuery / Direct Lake** para datos enormes o frescura: cuida que la fuente
  haga el trabajo; menos transformaciones en el modelo.
- **Refresco incremental** (`RangeStart`/`RangeEnd`): particiona y solo refresca lo
  nuevo → refrescos cortos y baratos.
- **Agregaciones** (tablas agregadas) para hechos muy grandes: el motor resuelve lo
  agregado y cae al detalle solo si hace falta.

## 3. DAX que rinde

- Mide con **DAX Studio** (Server Timings) y revisa el modelo con **VertiPaq
  Analyzer** (tamaño por columna, cardinalidad).
- `DIVIDE()` en vez de `/`; `VAR` para no recalcular; evita funciones que rompen el
  motor de almacenamiento (iteradores innecesarios sobre el hecho).
- Evita `FILTER` sobre tablas grandes cuando un argumento de filtro booleano basta.

## 4. Mantenibilidad (futuro)

- **Nomenclatura de negocio** y `displayFolder` (un modelo legible se mantiene solo).
- **Descripciones y formatString** en cada medida; sinónimos para Copilot/IA.
- **Documenta el modelo** (medidas, relaciones, origen) y versiónalo en Git (PBIP).
- Un cambio de criterio se registra en el `CHANGELOG.md`.

## 5. Reglas automatizables (las revisa `validar_modelo.py`, R8+)

- **R8** columnas de **alta cardinalidad** sumarizables y visibles (candidatas a ocultar/quitar).
- **R9** columnas `dateTime` con hora en el hecho (separar fecha/hora).
- **R10** relaciones **bidireccionales** declaradas (`crossFilteringBehavior: bothDirections`).
- **R11** columnas **calculadas** sobre tablas de hechos (mover a M o medida).

Ejecuta: `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py" <ruta .SemanticModel>`.
