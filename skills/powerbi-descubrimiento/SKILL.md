---
name: powerbi-descubrimiento
description: >
  USAR cuando todavia no se sabe QUE medir: "tengo una reunion con el area", "no
  se que pedirles", "quieren un dashboard pero no se de que", hay que levantar
  requerimientos, entender decisiones y dolores, identificar usuarios, o preparar
  un taller. NO usar si ya hay una lista de indicadores sobre la mesa (eso es
  powerbi-kpis) ni si ya existe un modelo que revisar (powerbi-auditoria).
---

# Fase 2 — Descubrimiento (design workshop)

Objetivo: entender **problema, usuarios y decisiones** antes de pensar en
visuales. Pregunta por decisiones que se deben tomar y dolores actuales, no
"¿que quieres ver?".

- Usa la plantilla `${CLAUDE_PLUGIN_ROOT}/assets/plantilla-descubrimiento.md`.
- Para conducir la reunion: `${CLAUDE_PLUGIN_ROOT}/assets/plantilla-agenda-taller.md`.
- Entregable: un documento de descubrimiento (problema, personas, journey,
  decisiones) que alimenta la Fase 3 (KPIs).

Detalle y guion: `${CLAUDE_PLUGIN_ROOT}/references/fase2-descubrimiento.md`.


## Boundaries

Alcance: entender el problema de negocio antes de medirlo — decisiones, dolores,
usuarios, frecuencia. Termina con un documento de descubrimiento acordado.
Fuera de alcance: definir la formula o el grain de cada indicador →
**powerbi-kpis**. Tampoco modela ni escribe DAX.
Si el usuario ya llega con los KPIs claros, no lo obligues a pasar por aqui:
es una fase que se puede saltar en un proyecto basico.

Fundamento: Design Sprint (Google Ventures), Design Thinking (IDEO / d.school).
