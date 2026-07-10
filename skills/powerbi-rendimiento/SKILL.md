---
name: powerbi-rendimiento
description: >
  Fase 7 — Rendimiento y mantenimiento de un modelo de Power BI. USAR cuando el
  reporte "va lento", el modelo pesa mucho, hay que optimizar memoria/refresco,
  bajar cardinalidad, o preparar el modelo para mantenerlo facilmente (VertiPaq,
  refresco incremental, agregaciones).
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

Fundamento: SQLBI / VertiPaq Analyzer, DAX Studio, Microsoft (optimization guide), Tabular Editor BPA.
