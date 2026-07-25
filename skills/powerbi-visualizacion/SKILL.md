---
name: powerbi-visualizacion
description: >
  USAR cuando hay que decidir que visual usar y como se ve la pagina: "diseña la
  pagina", "cuenta una historia con los datos", "esto se ve mal", "esta muy
  cargado", alinear u ordenar visuales, aplicar IBCS, revisar accesibilidad, o
  editar .pbir/visual.json. NO usar para los colores de marca (eso es
  powerbi-marca) ni para escribir las medidas que alimentan el visual
  (powerbi-modelado-dax).
---

# Fase 5 — Visualizacion y storytelling

Objetivo: paginas que comunican **UN mensaje cada una**.

Reglas de oro:
- **Patron Z**: KPIs arriba, contexto al centro, detalle abajo.
- **IBCS / SUCCESS**: notacion consistente (real solido, plan delineado, forecast
  achurado; varianzas verde/rojo).
- Maximo ~6-8 visuales por pagina; aprovecha style presets y visual calculations.
- Antes de dar una pagina por lista, pasa el **checklist pre-flight de numeros duros**
  (grilla 8px, ≤6-8 visuales, no pie >5, barras desde cero, WCAG) — en la reference.
- Si el usuario sube su PBIP, edita los `visual.json` (NUNCA renombres la propiedad
  `name` interna — rompe bookmarks; ver `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md`).
  Trabaja en una rama y **no hagas commit automatico**; el usuario revisa.

Detalle: `${CLAUDE_PLUGIN_ROOT}/references/fase5-visualizacion.md`.


## Boundaries

Alcance: que visual responde cada pregunta, layout, jerarquia, orden de lectura,
etiquetas, accesibilidad y narrativa. Trabaja sobre `.pbir`/`visual.json`.
Fuera de alcance: la paleta de marca → **powerbi-marca**. Las medidas que
alimentan el visual → **powerbi-modelado-dax**.

**Cuando NO aplicar el criterio al pie de la letra:** IBCS y las reglas de
densidad asumen un lector que analiza. Si el usuario pide explicitamente un
tablero para una pantalla en pared, una portada para direccion, o un reporte que
se imprime, dilo y adapta: la regla existe para que se entienda, no al reves.
Nunca simplifiques quitando accesibilidad (contraste, texto alternativo, orden
de foco): eso no es densidad, es dejar gente fuera.

Fundamento: IBCS/SUCCESS (Hichert), *Storytelling with Data* (Knaflic), Stephen Few.
