# Entrega: publicar, versionar (Git) y conectar por MCP

> Plantilla viva · actualizado 2026-06 · fuentes: Microsoft Learn (PBIP, Fabric Git integration, publicar), Tabular Editor (MCP) · ver `mantenimiento-de-plantillas.md`

Objetivo: llevar el dashboard a producción. **Dos caminos según el perfil** — no
obligues a nadie a usar Git.

## Camino A — SIN Git (iniciante / no técnico): publicar directo

El más simple, cero herramientas extra:
1. En Power BI Desktop, abre el `.pbip` y pulsa **Publicar**.
2. Elige el **área de trabajo** (workspace) destino e inicia sesión.
3. En el Service: configura **credenciales** del origen y un **refresco programado**
   (si la fuente es on-premise, necesitas un **gateway** de datos).
Listo: el reporte y su modelo quedan en el Service. Requiere licencia **Pro** (o el
workspace en capacidad). No necesitas Git.

## Camino B — CON Git (experto): GitHub + Fabric Git integration

Versionas el PBIP en GitHub y **sincronizas la rama `main` con un workspace** de
Fabric/Power BI (Git integration), sin "subir" manualmente.

### B.1 Estructura para versionar
- Versiona las carpetas del PBIP: `<Reporte>.pbip`, `<Reporte>.Report/`,
  `<Reporte>.SemanticModel/`.
- **`.gitignore`** (ya incluido en el repo): ignora `**/.pbi/` (cache `cache.abf` +
  `localSettings.json`) — son locales, enormes y causan conflictos. *(Es lo que
  Power BI genera por defecto al guardar como proyecto.)*
- **Ramas**: `main` = producción; ramas de trabajo por feature; PR para revisar
  (con `validar_modelo.py` + `validar_pbip.py` en el PR/CI).

### B.2 Subir a GitHub
```bash
git init && git add . && git commit -m "feat: reporte inicial"
git branch -M main
git remote add origin https://github.com/<tu-org>/<tu-repo>.git
git push -u origin main
```

### B.3 Conectar la rama `main` al Power BI Service (Fabric Git integration)
1. Crea/usa un **workspace** en **capacidad Fabric (F-SKU) o Premium (P-SKU)**
   *(requisito para Git integration; sin capacidad, usa el Camino A)*.
2. Workspace → **Configuración → Integración con Git** → conecta **GitHub** →
   elige el repo y la rama **`main`** y la carpeta del proyecto.
3. **Sincroniza**: los ítems PBIP del repo aparecen como semantic model + report
   en el workspace. Cada commit en `main` se refleja con **Update**; cambios en el
   workspace se mandan con **Commit**.
4. Varios entornos → **deployment pipelines** (dev/test/prod) sobre workspaces por rama.

## De MVP a producción (cambia los datos de ejemplo por reales)

El `.pbip` base usa datos **inline** (sirve para publicar la demo). Para producción:
1. Reemplaza el origen inline por la **fuente real** (skill `powerbi-datos-m` /
   `generar_conexion_m.py`: SQL, SharePoint, Databricks, Fabric), **parametrizada**.
2. Credenciales + **refresco programado** (+ gateway si on-premise).
3. Si aplica: **RLS/OLS** (seguridad por usuario; patron dinamico con
   `USERPRINCIPALNAME()` — ver `references/seguridad-rls.md`) y **refresco
   incremental** (`RangeStart`/`RangeEnd`). **Prueba el RLS** iniciando sesion como
   el usuario real (para externos, "Ver como rol" no basta).
4. **Modelo listo para IA/Copilot** antes de exponerlo: descripciones, sinonimos y
   "Approved for Copilot" (ver `references/preparar-datos-ia.md`).

## Conectar por MCP (opcional, avanzado)

Para que un agente consulte/edite el modelo en vivo sin volcar todo al contexto:
conecta un **servidor MCP** del modelo semántico (p. ej. el MCP de **Tabular Editor**
o las capacidades agénticas de **Fabric/Power BI**). El agente llama funciones
(leer medidas, DAX query, metadatos) y recibe solo el resultado.

## Antes de publicar: valida

```bash
python scripts/validar_modelo.py "<...>.SemanticModel"   # modelo (R1–R12)
python scripts/validar_pbip.py   "<...>.Report"          # reporte (P1–P7)
```

## Fundamento (oficial)
- PBIP y `.gitignore` por defecto: Microsoft Learn — Power BI Desktop projects.
- Git integration (GitHub/Azure DevOps, capacidad, sync por rama): Microsoft Learn — Fabric CI/CD.
- Publicar desde Desktop / refresco / gateway / RLS: Microsoft Learn — Power BI Service.
