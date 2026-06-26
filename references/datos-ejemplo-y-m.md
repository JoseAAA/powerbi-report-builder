# Fase 6 — MVP rapido: datos de ejemplo + codigo M + .pbip base

> Plantilla viva · actualizado 2026-06 · fuentes: Kimball (estrella); Power Query (Microsoft) · ver `mantenimiento-de-plantillas.md`

Objetivo: que el usuario tenga algo que abrir y tocar en minutos, sin esperar a
que la fuente real este lista. Dos entregables que encajan entre si.

## 1. Datos de ejemplo + codigo Power Query M

`scripts/generar_datos_ejemplo.py` crea un modelo estrella de ejemplo listo para
un MVP, con la grain y el patron Num/Den. El **dominio es seleccionable** con
`--dominio` (ventas, rrhh, finanzas, salud, generico); por defecto `generico`.

```bash
python scripts/generar_datos_ejemplo.py --salida datos-ejemplo \
    [--dominio ventas] [--desde 2024-01-01] [--hasta 2026-06-14] [--filas N] [--ruta-base "C:\\datos"]
```

Genera:

| Archivo | Que es |
|---|---|
| `Calendario.csv` | Dimension fecha: Fecha, Año, Mes, NumMes, Trimestre, EsDiaHabil. |
| `Sede.csv` | Dimension sede (ID Sede, Sede). |
| `Servicio.csv` | Dimension servicio (ID Servicio, Servicio, Servicio Agrupado). |
| `Indicadores.csv` | **Hecho** con patron `Num`/`Den`: una fila por indicador/sede/servicio/mes. |
| `modelo-ejemplo.m` | Codigo Power Query **M listo para pegar**, una seccion por tabla. |

**El patron Num/Den** (numerador/denominador por indicador) es ideal cuando los
KPI son cocientes (% de ocupacion, % a tiempo, tasa de X): las medidas DAX hacen
`DIVIDE(SUM(Num), SUM(Den))`, con un solo hecho para muchos indicadores y
agregaciones correctas a cualquier nivel.

### Como usar el `modelo-ejemplo.m`

1. En Power BI Desktop: **Obtener datos → Consulta en blanco → Editor avanzado**.
2. Pega el bloque de la tabla (cada tabla es una consulta).
3. El codigo trae dos variantes por tabla:
   - **Activa:** lee el CSV local con `Csv.Document(File.Contents(...))`.
   - **Comentada:** una variante desde SharePoint con
     `Excel.Workbook(Web.Contents(url_archivo))` — descomenta cuando conectes la
     fuente verdadera. Los pasos estan en espanol ("Tipo cambiado", "Filas
     filtradas", "Otras columnas quitadas").
4. Marca `Calendario` como **tabla de fecha** y **apaga Auto date/time**
   (Opciones → Carga de datos). El `.m` te lo recuerda en un comentario.

## 2. Proyecto .pbip base

`scripts/scaffold_pbip.py` arma un proyecto PBIP minimo y valido, con el mismo
formato (schemas/versiones) que tus reportes CY26.

```bash
# 1) genera el tema desde la marca activa
python scripts/generar_theme.py --marca assets/marca/<empresa>.json --salida theme.json
# 2) arma el proyecto con ese tema
python scripts/scaffold_pbip.py --nombre "Mi Reporte" --tema theme.json --salida .
```

Genera `<Nombre>/` con:
- `<Nombre>.pbip` (manifiesto).
- `<Nombre>.SemanticModel/` — modelo estrella TMDL: `Calendario`, `Sede`,
  `Servicio`, `Indicadores` y `_ Medidas` (con `Numerador`, `Denominador`,
  `Indicador %` usando VAR/RETURN + DIVIDE). Auto date/time apagado; calendario
  marcado como date table; nomenclatura de negocio.
- `<Nombre>.Report/` — reporte PBIR con el tema de marca aplicado y una pagina
  con una card (`Indicador %`) y un grafico de barras por `Servicio`.

El usuario abre el `.pbip` en Power BI Desktop (marzo 2026+ con PBIP/PBIR
habilitado) y empieza a modificar.

### Notas y riesgos

- El scaffold usa particiones M inline (`#table(...)`) para que el modelo cargue
  sin fuente externa. Para datos mas realistas, reemplaza esas particiones por
  el `modelo-ejemplo.m` apuntando a los CSV.
- Power BI puede normalizar/regenerar archivos menores (diagramLayout, culture)
  en el primer guardado: es esperado, genera un diff inocuo.
- Siempre pasa `--tema` para fidelidad de marca; sin el, usa un tema base pobre.
- Antes de entregar, valida el modelo: `python scripts/validar_modelo.py
  "<Nombre>.SemanticModel/definition"`.

## Como adaptarlo al negocio real del usuario

1. Cambia las dimensiones de ejemplo por las reales (de la fase 2/3).
2. Ajusta la grain del hecho a la ficha de KPI (fase 3).
3. Sustituye Num/Den si el indicador no es un cociente (p. ej. montos: una sola
   columna de medida).
4. Conecta la fuente real descomentando la variante SharePoint del `.m`.
