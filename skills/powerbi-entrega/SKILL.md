---
name: powerbi-entrega
description: >
  Entrega y producción de un reporte Power BI. USAR cuando el usuario dice
  "publicar", "subir a producción", "versionar en GitHub", "conectar con el
  Service", "deployment pipelines", "Fabric Git integration", pregunta cómo
  entregar, o cómo pasar de un MVP a datos reales (RLS, refresco, gateway).
---

# Entrega y producción

Lleva el dashboard a producción. **Elige el camino según el perfil** (no obligues a Git):

- **SIN Git (iniciante / no técnico):** Power BI Desktop → **Publicar** → elegir
  workspace → configurar credenciales + refresco (gateway si la fuente es on-premise).
  Requiere licencia Pro. Cero herramientas extra.
- **CON Git (experto):** versiona el PBIP en GitHub y **sincroniza la rama `main`
  con un workspace** vía **Fabric Git integration** (requiere capacidad F/P-SKU);
  ramas por feature + PR con validadores; deployment pipelines dev/test/prod.

**De MVP a producción:** cambia los datos inline por la fuente real
(`powerbi-datos-m`), añade refresco/gateway, y si aplica RLS + refresco incremental.

**Antes de publicar, valida:**
`python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py" <...>.SemanticModel`
y `python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_pbip.py" <...>.Report`.

Detalle (pasos de Git, conexión GitHub↔Service, `.gitignore`, MCP, fuentes oficiales):
`${CLAUDE_PLUGIN_ROOT}/references/entrega-git-y-mcp.md`.

Fundamento: Microsoft Learn (PBIP, Fabric Git integration, publicar/refresco/RLS).
