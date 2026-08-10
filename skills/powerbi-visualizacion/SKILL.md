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

<HARD-GATE>
Si vas a crear paginas o visuales NUEVOS, el plan tiene que estar aprobado antes
(`scripts/plan_reporte.py`). Ajustar visuales existentes no necesita gate.
</HARD-GATE>

Reglas de oro (las normativas llevan fuente en la reference):
- **Accesibilidad primero**, no al final: `altText` en todo visual que informe
  (≤250 caracteres), contraste de texto **≥4.5:1**, forma distinta por serie
  —el color nunca es el unico canal— y `tabOrder` explicito. No hay Accessibility
  Checker en Desktop: es checklist manual.
- **Lo mas importante arriba-izquierda** (LTR). El titulo dice la **conclusion**,
  no el tema.
- **Cero graficos 3D.** Pie o donut solo con **3-6 slices**.
- **Limites duros del formato**: 1 000 paginas, 1 000 visuales/pagina, 300 MB;
  **>500 archivos degrada la autoria**. Tablas y matrices: **Top N** o el filtro
  mas restrictivo que permita la pregunta.
- **Tema aplicado, sin hex sobrescritos por visual.** Nunca inventes claves de
  tema: el validador oficial las rechaza.
- Si el usuario sube su PBIP, edita los `visual.json` (NUNCA renombres la propiedad
  `name` interna — rompe bookmarks; ver `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md`).
  Trabaja en una rama y **no hagas commit automatico**; el usuario revisa.

**No cites como norma lo que no tiene fuente.** La reference trae la lista de
afirmaciones rechazadas; las cuatro que mas circulan y **no** debes usar como
regla: "maximo 6-8 visuales por pagina", "grilla de 8 px", "patron Z de lectura" y
la notacion de escenarios IBCS (real solido / plan delineado). Si las propones,
di que son convencion del proyecto, no estandar citado.

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
