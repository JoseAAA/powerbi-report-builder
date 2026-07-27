---
name: powerbi-modelado-dax
description: >
  USAR cuando se crean o revisan tablas y relaciones, "crea las medidas", hay DAX
  que escribir o refactorizar, falta acordar nomenclatura, hay que configurar
  RLS/OLS, o se editan archivos .tmdl de un modelo semantico. NO usar si el
  problema es que el reporte va lento o pesa mucho (eso es powerbi-rendimiento),
  ni para traer los datos a la tabla (powerbi-datos-m).
---

# Fase 4 — Modelado estrella y DAX

Objetivo: modelo **estrella** limpio y medidas DAX organizadas, en TMDL.

Reglas de oro:
- **Esquema estrella siempre**; calendario dedicado marcado como date table;
  **Auto date/time APAGADO** (las tablas `LocalDateTable_` son la evidencia de
  que esta encendido — corrige).
- **Nomenclatura de negocio** (Microsoft/SQLBI/Tabular Editor): nombres legibles
  con espacios, SIN prefijos `DIM_`/`FACT_` ni snake_case. Ver
  `${CLAUDE_PLUGIN_ROOT}/references/nomenclatura.md`.
- **Medidas, no columnas calculadas** (salvo slicer/eje); **VAR/RETURN** en medidas
  no triviales; **DIVIDE()** en vez de `/`.
- Time intelligence repetitiva → **calculation group** (`CG_`); logica reutilizable
  con parametros → **DAX UDF**; elegir metrica/dimension en un slicer → **field
  parameters** (`FP_`).
- **Descripcion en cada medida** (comentario `///` encima del measure, sintaxis
  TMDL oficial — NO `description:`): frase de negocio. La leen Copilot y los agentes
  LLM/MCP; `validar_modelo.py` la exige en **R12**. Ver
  `${CLAUDE_PLUGIN_ROOT}/references/preparar-datos-ia.md`.
- **Seguridad**: si hay datos por usuario o campos sensibles, define **RLS/OLS**
  (patron dinamico con `USERPRINCIPALNAME()`): `${CLAUDE_PLUGIN_ROOT}/references/seguridad-rls.md`.
- Antes de entregar: `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py" <ruta .SemanticModel>`.

Detalle (sintaxis TMDL, patrones DAX, patron Num/Den, checklist BPA):
`${CLAUDE_PLUGIN_ROOT}/references/fase4-modelado.md`. Antes de tocar un PBIP:
`${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md`.


## Boundaries

Alcance: estructura del modelo (tablas, relaciones, estrella, calendario),
medidas DAX, nomenclatura, RLS/OLS. Termina con `validar_modelo.py` en verde.
Fuera de alcance: traer los datos → **powerbi-datos-m**. Optimizar un modelo que
va lento → **powerbi-rendimiento**. Como se ven las medidas en pantalla →
**powerbi-visualizacion**.
Este skill corrige numeros mal calculados; no persigue milisegundos.

Fundamento: Kimball (estrella), SQLBI (Russo/Ferrari), Tabular Editor BPA, Microsoft Learn.
