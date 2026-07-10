---
name: powerbi-datos-m
description: >
  Fase Datos — Conexion a fuentes y Power Query M. USAR cuando el usuario pregunta
  "¿de donde saco los datos?", va a conectar Excel, SharePoint, SQL Server,
  Azure SQL, Synapse, Databricks o Fabric Lakehouse, decide Import vs DirectQuery
  vs Direct Lake, o necesita codigo M (query folding, parametros, refresco
  incremental).
---

# Fase Datos — Conexion a fuentes y Power Query M

Objetivo: una query M por tabla, con el **modo de conexion** decidido y los
**origenes parametrizados**, lista para modelar.

Reglas de oro:
- Empieza en **Import** salvo razon clara (DirectQuery si es enorme/tiempo real;
  Direct Lake si ya estas en Fabric).
- **Preserva el query folding**: filtra, quita columnas y renombra temprano.
- **Parametriza** servidor/sitio/ruta; una query por tabla; staging con load OFF;
  refresco incremental con `RangeStart`/`RangeEnd`.

Genera el M base con el script (no a mano):
`python "${CLAUDE_PLUGIN_ROOT}/scripts/generar_conexion_m.py" --fuente <fuente> --tabla <t> [--modo import]`
(fuentes: excel, sharepoint-archivo, sharepoint-lista, carpeta-csv, sql, databricks, fabric-lakehouse).

Detalle (conectores, modos y antipatrones por fuente):
`${CLAUDE_PLUGIN_ROOT}/references/datos-fuentes-y-m.md`.

Fundamento: query folding de Chris Webb + guia oficial de Power Query (Microsoft).
