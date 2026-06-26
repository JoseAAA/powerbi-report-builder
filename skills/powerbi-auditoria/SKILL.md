---
name: powerbi-auditoria
description: >
  Auditoria de un proyecto Power BI existente. USAR cuando el usuario sube o
  apunta a una carpeta PBIP completa (.pbip + .SemanticModel + .Report) y pide
  "audita mi proyecto/modelo", "revisa las medidas", "esta bien hecho?",
  "refactoriza". Revisa modelo, DAX, rendimiento y visuales contra las buenas
  practicas del framework.
---

# Auditoria de un PBIP existente

Objetivo: diagnosticar un proyecto contra las buenas practicas y entregar una
lista priorizada de hallazgos + correcciones.

Procedimiento:
1. **Lee primero** `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md` (no corromper el proyecto).
2. **Modelo + DAX**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py" <ruta .SemanticModel>`
   (R1–R11). Contrasta con `references/fase4-modelado.md` y `references/nomenclatura.md`.
3. **Reporte (PBIR)**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_pbip.py" <ruta .Report>`
   (P1–P6: JSON válido, `$schema`, tema completo, páginas) — evita la corrupción al abrir.
3. **Rendimiento**: aplica `references/rendimiento-y-mantenimiento.md` (cardinalidad,
   columnas sin uso, bidireccionales, fecha/hora).
4. **Visuales**: revisa los `visual.json` contra `references/fase5-visualizacion.md`
   (patron Z, IBCS, max 6-8 por pagina). NUNCA renombres la propiedad `name` interna.
5. **Marca/tema**: ¿usa un theme coherente? (`references/fase1-branding.md`).

Entrega: hallazgos por severidad (ALTA/MEDIA/BAJA) + el fix concreto por archivo.
Para modelos grandes, usa un subagente que lea y devuelva solo el veredicto (ahorra tokens).

Sugiere **commit en Git antes** de cualquier edicion masiva.
