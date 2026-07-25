---
name: powerbi-kpis
description: >
  USAR cuando hay indicadores que definir o validar: "estos son los KPIs", "¿tenemos
  datos para esto?", "¿como se calcula esto?", falta acordar formula, grain, meta o
  dueño, o hay que convertir objetivos de negocio en algo medible. NO usar si aun
  no se sabe que le duele al area (eso es powerbi-descubrimiento) ni para escribir
  el DAX de la medida (powerbi-modelado-dax).
---

# Fase 3 — KPIs / OKRs validados

Objetivo: una **ficha de indicador** por KPI, validada contra datos:
✅ Disponible / ⚠️ Parcial / ❌ Sin datos. **Meta y dueño nunca faltan.**

- Plantilla: `${CLAUDE_PLUGIN_ROOT}/assets/ficha-kpi.md`.
- Los ❌ (sin datos) NO avanzan a modelado: se documentan como **deuda de datos**.
- Entregable: fichas KPI que alimentan el modelado (Fase 4) y la visualizacion.

Detalle: `${CLAUDE_PLUGIN_ROOT}/references/fase3-kpis.md`.


## Boundaries

Alcance: convertir objetivos en indicadores medibles — nombre, formula, grain,
meta, dueño, frecuencia — y verificar que los datos existan.
Fuera de alcance: escribir el DAX (→ **powerbi-modelado-dax**) y conseguir la
fuente (→ **powerbi-datos-m**).
No apruebes un KPI sin dueño ni grain: sin eso, la medida no se puede escribir
sin adivinar.

Fundamento: OKR (Doerr/Google), Balanced Scorecard (Kaplan & Norton).
