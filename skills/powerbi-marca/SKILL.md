---
name: powerbi-marca
description: >
  Fase 1 — Marca y tema visual de Power BI. USAR cuando el usuario habla de
  colores, logo, identidad o paleta de su empresa, pide "crea/cambia el theme",
  modo oscuro, o sube un manual de marca / logo / presentacion (.thmx) / .pbip /
  theme.json para extraer o aplicar colores.
---

# Fase 1 — Marca y tema (theme.json)

Objetivo: un `theme.json` accesible que capture la identidad de la empresa,
generado desde un **archivo de marca** reutilizable. El skill **no trae marca por
defecto**: la captura una vez y la reutiliza.

Flujo:
1. **Busca marca activa EN EL PROYECTO DEL USUARIO** (directorio de trabajo:
   `./marca-*.json`, `./01-marca/`, o donde el usuario indique) — un archivo con
   `"activa": true`. Si existe, confirma sus colores reales antes de usarla.
2. **Si no hay**: NO inventes; captura la marca del usuario — logo / presentacion
   (.thmx) / manual / hex / .pbip existente (analiza imagenes visualmente y
   CONFIRMA los hex).
3. **Guarda la marca EN SU PROYECTO** (nunca dentro del plugin: los plugins se
   actualizan y borran lo guardado ahi): copia
   `${CLAUDE_PLUGIN_ROOT}/assets/marca/_plantilla-marca.json` →
   `<su-proyecto>/01-marca/<empresa>.json`, llenala y pon `"activa": true`.
4. **Genera el tema**:
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/generar_theme.py" --marca <ruta a <empresa>.json> --salida theme.json`
   - Cambios puntuales sobre un theme existente: `scripts/editar_theme.py`.
5. **Ese theme.json se pasa SIEMPRE** a `scaffold_pbip.py --tema` /
   `init_proyecto.py --tema`: los colores del usuario no se pierden en silencio.

Detalle (estructura del theme, $schema, style presets, WCAG, errores comunes):
`${CLAUDE_PLUGIN_ROOT}/references/fase1-branding.md`. Marca y plantilla:
`${CLAUDE_PLUGIN_ROOT}/assets/marca/README.md`.

Fundamento: WCAG (W3C), ColorBrewer (daltonismo), theme schema (Microsoft).
