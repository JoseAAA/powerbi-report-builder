---
name: powerbi-entrega
description: >
  USAR cuando el reporte ya existe y hay que sacarlo a producción: "publicar",
  "subirlo al Service", "versionar en GitHub", "deployment pipelines", "Fabric Git
  integration", "¿como lo comparto?", o pasar de un MVP a datos reales (RLS,
  refresco programado, gateway). NO usar si el reporte todavia no esta terminado ni
  validado.
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


## Boundaries

Alcance: sacar a produccion — publicar, versionar, Git/Fabric Git Integration,
deployment pipelines, refresco programado, gateway, permisos.
Cubre los dos caminos: **con** control de versiones (repo → `main` → Fabric Git
Integration → Service) y **sin** el (Publicar desde Desktop, que es la realidad
de muchas empresas con solo una licencia de Service).
Fuera de alcance: construir o corregir el reporte → la fase que toque.
No publiques nada sin los validadores en verde ni sin el OK del usuario.

Fundamento: Microsoft Learn (PBIP, Fabric Git integration, publicar/refresco/RLS).
