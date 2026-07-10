# Fase 4 — Modelado estrella y medidas DAX

> Plantilla viva · actualizado 2026-06 · fuentes: Kimball; SQLBI (Russo/Ferrari); Tabular Editor BPA; Microsoft Learn · ver `mantenimiento-de-plantillas.md`

Objetivo: modelo semantico limpio (estrella) y medidas DAX organizadas,
entregadas como TMDL listo para pegar o como edicion directa del PBIP.

> La **nomenclatura** (nombres de tablas, columnas, medidas) tiene su propia
> referencia con citas: `references/nomenclatura.md`. Es el estandar del skill
> (nombres de negocio, sin `DIM_`/`FACT_`, sin snake_case). Leela junto con esta.

## 1. Esquema estrella

- **Fact**: una tabla por proceso de negocio, una fila por evento en la grain de
  la ficha del KPI. Solo claves + metricas + fechas. Sin texto descriptivo.
- **Dimensiones**: atributos de corte (Producto, Proveedor, Sede, Calendario).
  Una fila por miembro, con clave unica.
- **Calendario dedicado siempre**: tabla de fechas continua, marcada como date
  table, con Año, Mes, NumMes (para ordenar el nombre del mes), Trimestre,
  EsDiaHabil. **Apaga Auto date/time** del archivo: las tablas `LocalDateTable_`
  y `DateTableTemplate_` son la evidencia de que esta encendido (mala practica:
  infla el modelo y duplica jerarquias).
- Relaciones 1→* desde dimension a fact, filtro en una direccion. Bidireccional
  solo con justificacion escrita (casi nunca).
- Role-playing (Fecha Pedido vs Fecha Entrega): una relacion activa +
  USERELATIONSHIP, o duplica la dimension si ambas vistas son de uso constante.
- Copo de nieve: aplanar a la dimension salvo jerarquias enormes.

Checklist al revisar el modelo del usuario:
- [ ] ¿Relaciones muchos-a-muchos evitables?
- [ ] ¿Columnas de fact con texto largo? (mover a dimension o eliminar)
- [ ] ¿Auto date/time apagado y calendario propio marcado? (¿hay LocalDateTable_?)
- [ ] ¿Columnas innecesarias importadas? (cada columna pesa en memoria)
- [ ] ¿Tipos correctos? (claves como entero cuando se pueda)

### Patron Num/Den (indicadores como cociente)

Muy util en salud y operaciones: el fact guarda dos
columnas, `Num` (numerador) y `Den` (denominador), por indicador. Un solo fact
sirve a muchos indicadores y agrega bien a cualquier nivel:

```dax
Numerador  = SUM(Indicadores[Num])
Denominador = SUM(Indicadores[Den])
Indicador % =
VAR _num = [Numerador]
VAR _den = [Denominador]
RETURN
    DIVIDE(_num, _den)
```

Filtra el indicador con una dimension `Tipo Indicador` o con medidas dedicadas
por indicador. Evita columnas calculadas de ratio fila a fila (promedios de
promedios incorrectos).

## 2. Medidas DAX — patrones

### Base + variantes

Una **medida base** por concepto; las variantes la referencian:

```dax
Ventas = SUM(Ventas[Importe])
Ventas YTD = TOTALYTD([Ventas], 'Calendario'[Fecha])
Ventas (AA) = CALCULATE([Ventas], DATEADD('Calendario'[Fecha], -1, YEAR))
Ventas vs AA % =
VAR _actual = [Ventas]
VAR _aa     = [Ventas (AA)]
RETURN
    DIVIDE(_actual - _aa, _aa)
```

### VAR / RETURN en toda medida no trivial

Cada VAR se evalua una sola vez (rendimiento), el codigo se lee de arriba abajo
(legibilidad) y puedes retornar una intermedia para depurar. Convenciones:
- Prefijo `_` en variables (`_actual`, `_filtrado`).
- Una variable por concepto con nombre claro; nada de `_x`, `_tmp`.
- `DIVIDE()` en vez de `/` (maneja division por cero).
- Las VAR son constantes una vez evaluadas: el contexto de filtro se captura al
  definirlas, no al usarlas (error clasico: definir una VAR fuera de un
  CALCULATE esperando que el CALCULATE la modifique).

### Organizacion en el modelo

- Tabla(s) de medidas **ocultas**: `_ Medidas` (neutra) o `DAX_<Area>`
  (agrupando por area). Que floten arriba con el prefijo y esten `isHidden`.
- `displayFolder` por area con prefijo numerico: `01 Ventas`, `02 Margen`.
- `formatString` SIEMPRE por medida (`#,0`, `0.0%`, `#,0.00`).
- Nombres de negocio (`Ventas`, `Indicador %`), no `SUM_Ventas` ni `mVentas`.
- Oculta (`isHidden`) las columnas numericas crudas del fact que ya tienen
  medida (evita el `Sum of Importe` arrastrable).

### Calculation groups vs DAX UDF

- **Calculation group** (`CG_Tiempo`): cuando la MISMA transformacion aplica a
  muchas medidas y el usuario la elige en un slicer. Caso tipico: time
  intelligence (Actual / YTD / AA / Var %) — 1 grupo reemplaza N×4 medidas.
  Seguridad: dentro de CALCULATE, aplica items solo sobre referencias a UNA
  medida, nunca sobre expresiones.
- **DAX UDF (user-defined function)**: logica con parametros reutilizada en
  varias medidas/columnas (redondeo de negocio, clasificacion ABC). **GA desde
  junio 2026** (requiere compatibility level 1702+); ya puedes proponerlas sin
  reservas si el Desktop esta actualizado.
- **Field parameters** (`FP_`): dejan que el usuario **elija en un slicer qué
  medida o qué dimension** ve el visual (p. ej. cambiar el eje entre Producto /
  Region / Cliente, o la metrica entre Ventas / Margen / Unidades). Uno o dos
  field parameters reemplazan varios visuales duplicados. Nombralos `FP_Metricas`,
  `FP_Dimensiones` y ocultalos del panel de campos. _Fuente: SQLBI / Microsoft
  (field parameters)._

### Seguridad (RLS / OLS)

Si el reporte debe mostrar **datos distintos por usuario** (cada gerente su sede,
cada vendedor su cartera) o **ocultar tablas/columnas sensibles** (salario, datos
medicos), se define en el modelo: **RLS** (filas) y **OLS** (tablas/columnas). El
patron recomendado es **RLS dinamico** con `USERPRINCIPALNAME()` + tabla de
seguridad. Detalle, TMDL de roles y buenas practicas: `references/seguridad-rls.md`.

## 3. TMDL — sintaxis esencial

```tmdl
table Indicadores
	lineageTag: <guid>

	measure 'Indicador %' = ```
			VAR _num = [Numerador]
			VAR _den = [Denominador]
			RETURN
			    DIVIDE(_num, _den)
			```
		formatString: 0.0%
		displayFolder: 01 Indicadores
		lineageTag: <guid>

	column Num
		dataType: double
		isHidden
		summarizeBy: sum
		sourceColumn: Num
		lineageTag: <guid>

	partition Indicadores = m
		mode: import
		source = ```
				let
				    Origen = ...
				in
				    Origen
				```
```

Reglas:
- Indentacion con TAB, consistente con el archivo existente.
- Expresion multilinea: abre con ``` tras el `=`, cuerpo con sangria adicional,
  cierra con ``` alineado al cuerpo.
- `lineageTag` es un GUID: al CREAR un objeto, genera uno
  (`python -c "import uuid; print(uuid.uuid4())"`); al EDITAR, no lo toques.
- Linea en blanco entre objetos hermanos.
- Relaciones en `relationships.tmdl`:

```tmdl
relationship <guid>
	fromColumn: Indicadores.'ID Sede'
	toColumn: Sede.'ID Sede'
```

## 4. Checklist BPA (subconjunto Power BI CAT)

`python scripts/validar_modelo.py <ruta .SemanticModel/definition>` verifica las
marcadas con ⚙; las demas revisalas tu:

- ⚙ Toda medida tiene `formatString`
- ⚙ Medida no trivial (>80 chars) usa VAR/RETURN
- ⚙ No hay `/` directa (usar DIVIDE) con denominador variable
- ⚙ Columnas de fact sumadas por medidas estan ocultas
- ⚙ Sin nombres de medida duplicados entre tablas
- ⚙ displayFolder presente en modelos con >10 medidas
- ⚙ Evidencia de Auto date/time (tablas LocalDateTable_)
- Evitar IFERROR (enmascara y penaliza; valida el dato antes)
- Evitar FILTER(tabla, …) completo como filtro de CALCULATE cuando basta un
  filtro booleano o FILTER(VALUES(col), …)
- Evitar columnas calculadas donde una medida o M resuelve lo mismo
- Relaciones bidireccionales documentadas o eliminadas
- TREATAS sobre INTERSECT/FILTER para relaciones virtuales

Si el usuario tiene Tabular Editor, recomiendale el BPA oficial completo (repo
`microsoft/Analysis-Services` BestPracticeRules) — este skill cubre el
subconjunto critico, no las ~60 reglas.

## Fuentes

- DAX UDF (GA jun 2026): https://learn.microsoft.com/en-us/dax/best-practices/dax-user-defined-functions
- Calculation groups: https://learn.microsoft.com/en-us/power-bi/transform-model/calculation-groups
- Nomenclatura: `references/nomenclatura.md`
