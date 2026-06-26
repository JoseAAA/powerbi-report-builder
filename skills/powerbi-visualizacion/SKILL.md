---
name: powerbi-visualizacion
description: >
  Fase 5 — Visualizacion y storytelling de un reporte Power BI. USAR cuando el
  usuario quiere diseñar las paginas, "contar una historia con los datos",
  ordenar visuales, aplicar IBCS, o editar archivos .pbir/visual.json de un
  reporte. Paginas que comunican UN mensaje cada una.
---

# Fase 5 — Visualizacion y storytelling

Objetivo: paginas que comunican **UN mensaje cada una**.

Reglas de oro:
- **Patron Z**: KPIs arriba, contexto al centro, detalle abajo.
- **IBCS / SUCCESS**: notacion consistente (real solido, plan delineado, forecast
  achurado; varianzas verde/rojo).
- Maximo ~6-8 visuales por pagina; aprovecha style presets y visual calculations.
- Si el usuario sube su PBIP, edita los `visual.json` (NUNCA renombres la propiedad
  `name` interna — rompe bookmarks; ver `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md`).

Detalle: `${CLAUDE_PLUGIN_ROOT}/references/fase5-visualizacion.md`.

Fundamento: IBCS/SUCCESS (Hichert), *Storytelling with Data* (Knaflic), Stephen Few.
