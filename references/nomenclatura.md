# Nomenclatura del modelo semantico (estandar del skill)

> Plantilla viva · actualizado 2026-06 · fuentes: SQLBI; Tabular Editor BPA (Power BI CAT); Chris Webb; Microsoft · ver `mantenimiento-de-plantillas.md`

Este es el **estandar de nombres** que el skill aplica y defiende. Esta basado
en la mejor practica actual de la comunidad y Microsoft, no en preferencias
arbitrarias. Fuentes al final.

## Principio rector

Los nombres deben ser **legibles, de negocio y consistentes**. El modelo es la
fuente de verdad: usa la terminologia que la gente del negocio realmente usa
("Ventas" vs "Ingresos" vs "Facturacion" — pregunta cual). Esto sirve a los
usuarios, a los desarrolladores y a los agentes de IA que consultan el modelo.

## Reglas

1. **Sin prefijos tecnicos `DIM_` / `FACT_` en tablas visibles.** Llama a las
   tablas por su nombre de negocio: `Cliente`, `Calendario`, `Ventas`,
   `Proveedor`. Para distinguir hechos de dimensiones, usa **table groups**
   (Tabular Editor) o el orden, no el nombre.
2. **Casing con espacios, no CamelCase ni snake_case.** `Estado de Orden`, no
   `OrderStatus` ni `estado_orden`. Nombres humanos, no de programacion.
3. **Sin abreviaturas ni acronimos** salvo los estandar del negocio (y esos,
   documentados en la descripcion del campo). `Margen Estandar`, no `Mg. Std.`.
4. **Sin numeros decorativos ni Unicode/emojis** en nombres de tabla, columna o
   carpeta.
5. **Columnas — convencion de sufijos:**
   - Clave de relacion (surrogate): `<Entidad> Key` → `Cliente Key`.
   - Identificador natural de negocio: `<Entidad> ID` → `Cliente ID`.
   - Texto descriptivo: `<Entidad> Nombre` → `Cliente Nombre`.
   - Booleano: `Es <Cosa>` → `Es Activo`, `Es Dia Habil`.
   - Role-playing (misma dim, dos roles): prefija el contexto →
     `Fecha Pedido Key`, `Fecha Entrega Key`.
6. **Medidas — sintaxis consistente de periodo / unidad / comparacion:**
   - Periodos: `Ventas (AA)` (ano anterior), `Ventas (PY)`; preferir formas
     faciles de extender (`(2AA)`).
   - Agregaciones: `Ventas YTD`, `Ventas MTD (AA)`.
   - Unidades: `Ventas (S/)`, `Margen (%)`, `Cantidad (und)`.
   - Comparaciones: `Ventas vs Ppto`, `Ventas vs AA`.
   - Nombres de negocio, nunca `SUM_ventas`, `mVentas`, `vw_...`.
7. **Prefijos SOLO para objetos tecnicos no expuestos al usuario:**
   - Calculation groups: `CG_Tiempo`.
   - Field parameters: `FP_Metricas`.
   - Tabla(s) de medidas ocultas: un nombre que ordene arriba, p. ej. `_ Medidas`
     (o `DAX_<Area>` si se prefiere agrupar por area — ver el ejemplo abajo).
   - Estos van **ocultos** (`isHidden`) o agrupados, no en la cara del usuario.
8. **Organiza, no solo nombres:** display folders en Title Case con prefijo
   numerico para ordenar (`01 Ventas`, `02 Margen`); descripciones y format
   strings en cada medida; sinonimos para Copilot/IA cuando el negocio usa
   varios terminos.

## Ejemplo: migrar un modelo con nomenclatura mezclada

Es comun encontrar modelos que mezclan dos estilos: uno con `dim_calendario` /
`fact_ventas` (snake_case con prefijo) y otro con PascalCase (`Calendario`,
`BaseTareas`). El estandar de arriba **reemplaza ambos** para reportes nuevos:
`Calendario`, `Sede`, `Servicio`, `Indicadores` (nombres de negocio, sin prefijo).

Para las **tablas de medidas**, `DAX_<Area>` (p. ej. `DAX_General`, `DAX_Ventas`)
es una convencion aceptable: son tablas tecnicas ocultas que agrupan medidas por
area. Si tu equipo ya la conoce, mantenla, pero **ocultalas** y pon display
folders adentro. La alternativa neutra del skill es `_ Medidas`.

Si refactorizas un modelo existente para aplicar esta nomenclatura, recuerda:
al renombrar campos hay que **re-enlazar (rebind) los visuales** de los reportes
que consumen el modelo, o se rompen.

## Fuentes

- Tabular Editor — *Naming conventions for Power BI semantic models* (Ruben Van
  de Voorde, may 2026): https://tabulareditor.com/blog/naming-conventions-for-power-bi-semantic-models
- Chris Webb — *Naming tables, columns and measures in Power BI*: https://blog.crossjoin.co.uk/2020/06/28/naming-tables-columns-and-measures-in-power-bi/
- SQLBI — *DAX naming conventions*: https://docs.sqlbi.com/dax-style/dax-naming-conventions
- Microsoft Learn — *Semantic model best practices*: https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices
