# Ejemplos BI — muestras públicas con buenas prácticas

Esta carpeta usa **muestras públicas y oficiales** (sin datos de ninguna empresa).
Dos tipos de ejemplo:

1. **Generados por este framework** (limpios por construcción: modelo estrella,
   nomenclatura de negocio, Auto date/time apagado, validados R1–R11). Genera uno con:
   ```
   python ../scripts/init_proyecto.py --nombre "Demo Ventas" --dominio ventas
   ```
2. **Descargables oficiales** (públicos) que siguen buenas prácticas — tabla abajo.

## Fuentes públicas oficiales recomendadas

| Fuente | Qué es | Formato | Por qué (buenas prácticas) |
|---|---|---|---|
| [microsoft/powerbi-desktop-samples](https://github.com/microsoft/powerbi-desktop-samples) | Reportes de muestra oficiales de Microsoft (Sales & Returns, Supply Chain…) + el **Report Theme JSON Schema** | PBIX / JSON | mantenidos por el equipo de Power BI; base oficial |
| [Power BI samples (Microsoft Learn)](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-datasets) | Datasets y reportes listos (Financial, Sales, etc.) | PBIX / PBIT / Excel | curados por Microsoft para aprender |
| [SQLBI — Contoso Data Generator](https://www.sqlbi.com/tools/contoso-data-generator/) | Generador del modelo **Contoso en estrella** (tamaño/distribución configurables) | PBIX / PBIT / CSV / Parquet / Delta | **estrella canónica** de Russo/Ferrari; el referente de buenas prácticas de modelado |
| [sql-bi/optimizing-dax-demos](https://github.com/sql-bi/optimizing-dax-demos) | Archivos demo del libro *Optimizing DAX* | PBIX | patrones DAX y rendimiento por SQLBI |
| [ContosoSalesForPowerBI (Download Center)](https://www.microsoft.com/en-us/download/details.aspx?id=46801) | Dataset Contoso Sales oficial | PBIX | dataset clásico de práctica |

## Referencias de buenas prácticas (no son archivos, son la doctrina)

- [PBIP — formato de proyecto](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview) (texto, versionable, lo que usa este framework)
- [Esquema estrella — guía oficial](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [El porqué del esquema estrella — SQLBI](https://www.sqlbi.com/articles/the-importance-of-star-schemas-in-power-bi/)

## Recomendación

Para **plantillas base** del repo: usa las **generadas por el framework** (garantizan las
buenas prácticas). Para **practicar con datos realistas**: descarga el **Contoso de SQLBI**
(estrella) o las muestras de **powerbi-desktop-samples**. Convierte cualquier PBIX a **PBIP**
(Archivo → Guardar como proyecto) para versionarlo y editarlo con este plugin.

> Nota: descarga tú los archivos públicos a tu máquina; aquí solo los enlazamos para
> evitar redistribuir binarios y respetar sus licencias.
