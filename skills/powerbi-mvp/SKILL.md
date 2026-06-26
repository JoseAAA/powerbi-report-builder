---
name: powerbi-mvp
description: >
  Fase 6 — MVP rapido: datos de ejemplo + .pbip base. USAR cuando el usuario
  quiere "datos de ejemplo", "un .pbip base", "arrancar ya sin la fuente real",
  un proyecto Power BI minimo para abrir y modificar, o un MVP/demo. Multi-dominio.
---

# Fase 6 — MVP rapido (datos de ejemplo + .pbip base)

Objetivo: que el usuario abra y toque algo en minutos, sin esperar la fuente real.

1. **Datos de ejemplo + codigo M** (dominio seleccionable):
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/generar_datos_ejemplo.py" --salida datos-ejemplo --dominio <ventas|rrhh|finanzas|salud|generico>`
   → CSVs de un modelo estrella (patron Num/Den) + `modelo-ejemplo.m` para pegar.
2. **Proyecto .pbip base** (modelo estrella TMDL + reporte PBIR con tema):
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_pbip.py" --nombre "<Reporte>" --dominio <dominio> --tema theme.json`
   → abre en Power BI Desktop y se empieza a modificar.
   **`--tema` va SIEMPRE** (generalo antes con `powerbi-marca`); omitelo SOLO si
   el usuario acepta explicitamente los colores por defecto de Power BI.

Para arrancar un proyecto completo de una empresa nueva:
`python "${CLAUDE_PLUGIN_ROOT}/scripts/init_proyecto.py" --nombre "<X>" --dominio <d> --marca <m>|--tema <t>|--sin-marca`
(exige elegir el tema: los colores del usuario nunca se ignoran en silencio).
Al terminar, valida: `validar_modelo.py` (R1–R11) y `validar_pbip.py` (P1–P7).

Detalle y como adaptar a un negocio: `${CLAUDE_PLUGIN_ROOT}/references/datos-ejemplo-y-m.md`.

Fundamento: Kimball (estrella), Power Query (Microsoft).
