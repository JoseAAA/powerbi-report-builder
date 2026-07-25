---
name: powerbi-rendimiento
description: >
  USAR cuando algo YA construido va mal: "el reporte va lento", "el archivo pesa
  muchisimo", "tarda en abrir", el refresco tarda o falla, hay que bajar
  cardinalidad o memoria, o preparar el modelo para mantenerlo con poco esfuerzo.
  NO usar para diseñar el modelo desde cero (eso es powerbi-modelado-dax) ni si el
  problema es que un numero sale mal (eso es un error de DAX, no de rendimiento).
---

# Fase 7 — Rendimiento y mantenimiento

Objetivo: un modelo **rapido hoy y mantenible mañana**. El motor es VertiPaq:
manda el tamaño y la **cardinalidad** de las columnas, no el numero de filas.

Reglas de oro (mayor impacto primero):
- **Quita columnas sin uso** y **baja cardinalidad** (evita GUIDs/decimales; separa
  fecha y hora); fija **tipos minimos**; **oculta claves** del hecho.
- **Evita relaciones bidireccionales** y columnas calculadas sobre el hecho (hazlo en M).
- Escala con **refresco incremental** (`RangeStart`/`RangeEnd`) y **agregaciones**.
- Mide con **DAX Studio** + **VertiPaq Analyzer**.

Valida (reglas R8+): `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py" <ruta .SemanticModel>`.

Detalle: `${CLAUDE_PLUGIN_ROOT}/references/rendimiento-y-mantenimiento.md`.


## Boundaries

Alcance: tamaño del modelo, memoria, cardinalidad, tiempo de refresco y de
consulta, agregaciones, refresco incremental.
Fuera de alcance: diseñar el modelo desde cero → **powerbi-modelado-dax**.
Un numero que sale mal es un error de logica, no de rendimiento.

**No optimices sin medir.** Sin una medicion (tamaño por columna, tiempo de
consulta) cualquier cambio es una corazonada. Y no sacrifiques correccion ni
legibilidad del DAX por una mejora que nadie ha medido.

Fundamento: SQLBI / VertiPaq Analyzer, DAX Studio, Microsoft (optimization guide), Tabular Editor BPA.
