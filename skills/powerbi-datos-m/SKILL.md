---
name: powerbi-datos-m
description: >
  USAR cuando la pregunta es de donde salen los datos y como traerlos: "¿de donde
  saco los datos?", conectar Excel, CSV, SharePoint, SQL Server, Azure SQL,
  Synapse, Databricks o Fabric Lakehouse, decidir Import vs DirectQuery vs Direct
  Lake, o hace falta codigo M (query folding, parametros, refresco incremental).
  NO usar para medidas, relaciones ni DAX (eso es powerbi-modelado-dax).
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


## Boundaries

Alcance: origen de los datos y su transformacion — conexion, credenciales, modo
de almacenamiento, codigo M, folding, parametros, refresco incremental.
Termina cuando cada tabla del modelo tiene una consulta que devuelve su forma.
Fuera de alcance: relaciones, medidas y DAX → **powerbi-modelado-dax**.
Rendimiento del modelo ya cargado → **powerbi-rendimiento**.

Fundamento: query folding de Chris Webb + guia oficial de Power Query (Microsoft).
