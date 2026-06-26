# Datos y fuentes — conexión y Power Query M

> Plantilla viva · actualizado 2026-06 · fuentes: Chris Webb; Power Query docs (Microsoft Learn); Kimball · ver `mantenimiento-de-plantillas.md`

Lee esto cuando el usuario va a conectar **datos reales**. Para datos de
ejemplo / arranque rápido usa `datos-ejemplo-y-m.md`. Corre **entre la Fase 3
(KPIs) y la Fase 4 (Modelado)**. Entregable: una query M por tabla + el modo de
conexión decidido y documentado. Alimenta el modelado estrella.

## 1. Decide el MODO de conexión (antes del conector)

| Modo | Cuándo | Trade-off | Regla |
|---|---|---|---|
| **Import** | default; el dato cabe en memoria, refresco programado basta | consulta rápida, ocupa RAM | **Empieza aquí salvo razón clara** |
| **DirectQuery** | datos enormes o tiempo casi real; no se pueden copiar | lento por visual, presiona la fuente | solo si Import no es viable |
| **Direct Lake** (Fabric) | el dato ya vive en Lakehouse/Warehouse de Fabric | velocidad de Import + frescura de DQ | preferido si ya estás en Fabric |

Documenta el porqué en una línea: es lo primero que se mira al mantener.

## 2. Conectores por fuente (los más usados del mercado)

| Fuente | Conector M | Modo sugerido | Ojo con |
|---|---|---|---|
| Excel (local/OneDrive) | `Excel.Workbook(...)` | Import | ruta local rompe el refresh en Service → SharePoint/OneDrive + parámetro |
| SharePoint (archivo) | `Excel.Workbook(Web.Contents(urlSitio))` | Import | usa la URL del **sitio** + ruta relativa, no la del archivo |
| SharePoint (lista) | `SharePoint.Tables` | Import | columnas de sistema; expandir lookups |
| Carpeta de CSVs | `Folder.Files` + `Csv.Document` | Import | combina con función, no fila por fila |
| SQL Server / Azure SQL | `Sql.Database(srv, db)` | Import o DQ | **mantén el query folding**; conéctate a vistas, no `SELECT *` en M |
| Synapse | `Sql.Database` | Import o DQ | folding nativo |
| Databricks | conector nativo `Databricks.Catalogs` | DQ o Import | Unity Catalog; evita ODBC genérico |
| Fabric Lakehouse/Warehouse | `Lakehouse.Contents` | Direct Lake | ideal para Direct Lake |

## 3. Power Query M — reglas que ahorran mantenimiento y CPU

1. **Parametriza el origen** (servidor, base, URL del sitio, ruta) → un parámetro
   `pServidor`/`pSitio`; pasar dev↔prod es un clic, no editar 20 queries.
2. **Una query por tabla** del modelo; las intermedias quedan como queries
   *staging* con **Enable load = OFF** (no se cargan al modelo).
3. **Preserva el query folding**: filtra, quita columnas y renombra LO MÁS
   TEMPRANO posible, con pasos que la fuente sepa traducir a SQL. Verifica con
   *View Native Query*; si se apaga, ese paso corre en tu PC.
4. **Quita columnas que no usas** apenas entran (menos memoria, modelo más chico).
5. **Fija tipos una sola vez** al final de la limpieza; evita cadenas repetidas
   de *Changed Type* que rompen el folding.
6. **Nombra los pasos en lenguaje de negocio** ("Filtra activos", no "Filtered Rows1").
7. **Refresco incremental**: define parámetros `RangeStart`/`RangeEnd` (Date/Time)
   y filtra por ellos → Power BI particiona y solo refresca lo nuevo.
8. **Evita `Table.Buffer`** salvo que midas que ayuda; suele matar el folding.
9. ETL pesado (merge/group grandes) → empújalo a la fuente (vista SQL, notebook).
   M es para *dar forma*, no para transformación pesada.

## 4. Antipatrones (corrige si los ves)

- Ruta de archivo local fija → el refresh falla en el Service.
- `SELECT *` o traer la tabla entera y filtrar dentro de Power BI.
- Tipos/nombres puestos en M y otra vez en el modelo (duplicado que confunde).
- Una query gigante de 40 pasos en vez de staging + tablas limpias.

## 5. Entregable y validación

- **Genera el M base con el script** (no a mano, ahorra tokens y evita errores):
  `python scripts/generar_conexion_m.py --fuente sql --servidor pServidor --base <db> --tabla <vista>`
  — fuentes: `excel`, `sharepoint-archivo`, `sharepoint-lista`, `carpeta-csv`,
  `sql`, `databricks`, `fabric-lakehouse`; `--modo import|directquery|directlake`.
- Código M por tabla (pégalo en *Inicio → Transformar datos → Editor avanzado*),
  el modo de conexión decidido y los parámetros de origen.
- En fuentes SQL/DQ, confirma folding con *View Native Query*.
- Para arrancar sin la fuente real, salta a la Fase 6 (`datos-ejemplo-y-m.md`).

> Sigue con `fase4-modelado.md` + `nomenclatura.md` para convertir estas tablas
> en un modelo estrella con nombres de negocio.

## Fundamento (frameworks de la industria)

- **Query folding y M**: Chris Webb (Microsoft) + guía oficial de Power Query.
- **Modo de conexión / Direct Lake**: documentación de Microsoft Fabric / Power BI.
- **Destino estrella y nombres**: Kimball (modelado dimensional) + SQLBI / Tabular
  Editor BPA (Best Practice Analyzer, equipo Power BI CAT).
