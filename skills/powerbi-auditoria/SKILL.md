---
name: powerbi-auditoria
description: >
  Auditoria de un proyecto Power BI existente. USAR cuando el usuario sube o
  apunta a una carpeta PBIP (.pbip + .SemanticModel + .Report) y pide "audita mi
  proyecto/modelo", "revisa las medidas", "¿esta bien hecho?", "refactoriza", o
  "valida contra buenas practicas".
---

# Auditoria de un PBIP existente

Objetivo: diagnosticar un proyecto contra las buenas practicas y entregar una
lista priorizada de hallazgos + correcciones.

Procedimiento:
1. **Lee primero** `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md` (no corromper el proyecto).
2. **Modelo + DAX**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py" <ruta .SemanticModel>`
   (R1–R12, incl. description para IA). Contrasta con `references/fase4-modelado.md`,
   `references/nomenclatura.md` y `references/preparar-datos-ia.md`.
3. **Reporte (PBIR)**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_pbip.py" <ruta .Report>`
   (P1–P7: JSON válido, `$schema`, tema completo y cableado, páginas) — evita la
   corrupción al abrir.
4. **Rendimiento**: aplica `references/rendimiento-y-mantenimiento.md` (cardinalidad,
   columnas sin uso, bidireccionales, fecha/hora).
5. **Visuales**: revisa los `visual.json` contra `references/fase5-visualizacion.md`
   (patron Z, IBCS, max 6-8 por pagina). NUNCA renombres la propiedad `name` interna.
6. **Marca/tema**: ¿usa un theme coherente? (`references/fase1-branding.md`).

Entrega: hallazgos por severidad (ALTA/MEDIA/BAJA) + el fix concreto por archivo.
Formato compacto por hallazgo: `[SEV] Rn archivo: problema -> fix`, y un resumen
numerico al final (cuantos ALTA/MEDIA/BAJA). Para modelos grandes, usa un subagente
que lea y devuelva solo el veredicto (ahorra tokens).

**Disciplina Git (antes de refactorizar)**: trabaja en una rama, valida con ambos
validadores antes y despues, y **nunca hagas commit automatico** — el usuario revisa
y confirma. Sugiere commit ANTES de cualquier edicion masiva.
