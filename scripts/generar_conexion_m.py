#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_conexion_m.py — Genera codigo Power Query M correcto por FUENTE, para
conectar datos reales en Power BI, en vez de escribirlo a mano (ahorra tokens y
evita errores). Alineado 1:1 con references/datos-fuentes-y-m.md.

Principios que aplica (Chris Webb / guia oficial de Power Query):
  - Origen PARAMETRIZADO (servidor/sitio/ruta) -> cambiar dev<->prod es un clic.
  - Preserva el query folding en SQL/Databricks (conecta a vista, filtra temprano).
  - Tipado al final y pasos nombrados en lenguaje de negocio.

Fuentes soportadas (--fuente):
  excel              archivo Excel local / OneDrive
  sharepoint-archivo Excel en SharePoint (Web.Contents)
  sharepoint-lista   lista de SharePoint
  carpeta-csv        carpeta con muchos CSV (Folder.Files)
  sql                SQL Server / Azure SQL / Synapse (Sql.Database)
  databricks         Azure Databricks (conector nativo)
  fabric-lakehouse   Microsoft Fabric Lakehouse

Uso:
  python generar_conexion_m.py --fuente sql --servidor pServidor --base Ventas \\
      --esquema dbo --tabla vw_FactVentas --modo import
  python generar_conexion_m.py --fuente sharepoint-archivo --sitio pSitio \\
      --ruta "Documentos compartidos/Datos" --archivo Ventas.xlsx --hoja 2024
  python generar_conexion_m.py --fuente databricks --catalogo main \\
      --esquema ventas --tabla pedidos --modo directquery --salida pedidos.m

Argumentos comunes:
  --fuente        (requerido) ver lista de arriba
  --tabla         nombre de la tabla/consulta resultante (y del objeto en la fuente)
  --modo          import | directquery | directlake (default: import)
  --parametrizar  / --no-parametrizar   (default: parametrizar)
  --salida        archivo .m de salida (default: imprime en consola)

Argumentos por fuente (los que no apliquen se ignoran):
  --servidor --base --esquema           (sql)
  --sitio --ruta --archivo --hoja       (sharepoint-archivo)
  --lista                               (sharepoint-lista)
  --ruta                                (excel: ruta del archivo; carpeta-csv: carpeta)
  --catalogo --esquema --tabla          (databricks / fabric-lakehouse)

Solo libreria estandar.
"""
import argparse
import sys


def _param(valor, nombre_param, parametrizar):
    """Devuelve la referencia a usar en M: el parametro si --parametrizar y el
    valor parece un nombre de parametro o esta vacio; si no, un literal entre
    comillas. Regla simple: si el usuario pasa algo que empieza con 'p' y sin
    espacios, se trata como parametro; en --no-parametrizar siempre literal."""
    if valor and (not parametrizar):
        return '"%s"' % valor
    if valor and valor[:1] == "p" and " " not in valor and valor[1:2].isupper():
        return valor  # ya es un nombre de parametro (pServidor, pSitio…)
    if valor:
        return '"%s"' % valor
    return nombre_param  # placeholder de parametro


# --------------------------------------------------------------------------- #
# Constructores por fuente -> devuelven (cuerpo_let, lista_parametros, notas)
# --------------------------------------------------------------------------- #

def m_excel(a):
    ruta = _param(a.ruta, "pRutaArchivo", a.parametrizar)
    hoja = a.hoja or a.tabla or "Hoja1"
    cuerpo = f'''    // Ruta local: rompe el refresh en el Service. Prefiere OneDrive/SharePoint.
    Origen = Excel.Workbook(File.Contents({ruta}), null, true),
    Hoja = Origen{{[Item="{hoja}", Kind="Sheet"]}}[Data],
    Encabezados = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),
    // Quita columnas que no uses lo antes posible (menos memoria):
    // Limpias = Table.SelectColumns(Encabezados, {{"Col1","Col2"}}),
    #"Tipos" = Table.TransformColumnTypes(Encabezados, {{ /* {{"Col", type text}} */ }})'''
    params = [("pRutaArchivo", "ruta del archivo Excel")] if ruta == "pRutaArchivo" else []
    notas = ["Excel local no refresca en el Service: sube el archivo a SharePoint/OneDrive y usa --fuente sharepoint-archivo."]
    return cuerpo, '#"Tipos"', params, notas


def m_sharepoint_archivo(a):
    sitio = _param(a.sitio, "pSitio", a.parametrizar)
    ruta = a.ruta or "Documentos compartidos"
    archivo = a.archivo or (a.tabla + ".xlsx" if a.tabla else "Datos.xlsx")
    hoja = a.hoja or a.tabla or "Hoja1"
    cuerpo = f'''    // Usa la URL del SITIO (no la del archivo) + ruta relativa.
    Origen = Excel.Workbook(Web.Contents({sitio}, [RelativePath="{ruta}/{archivo}"]), null, true),
    Hoja = Origen{{[Item="{hoja}", Kind="Sheet"]}}[Data],
    Encabezados = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),
    #"Tipos" = Table.TransformColumnTypes(Encabezados, {{ /* {{"Col", type text}} */ }})'''
    params = [("pSitio", "URL del sitio SharePoint, p.ej. https://empresa.sharepoint.com/sites/Datos")] if sitio == "pSitio" else []
    return cuerpo, '#"Tipos"', params, []


def m_sharepoint_lista(a):
    sitio = _param(a.sitio, "pSitio", a.parametrizar)
    lista = a.lista or a.tabla or "MiLista"
    cuerpo = f'''    Origen = SharePoint.Tables({sitio}, [ApiVersion = 15]),
    Lista = Origen{{[Title="{lista}"]}}[Items],
    // Expande lookups y quita columnas de sistema que no uses.
    #"Tipos" = Table.TransformColumnTypes(Lista, {{ /* {{"Col", type text}} */ }})'''
    params = [("pSitio", "URL del sitio SharePoint")] if sitio == "pSitio" else []
    return cuerpo, '#"Tipos"', params, ["Las listas traen columnas de sistema (Author, Created…). Quita las que no uses."]


def m_carpeta_csv(a):
    ruta = _param(a.ruta, "pRutaCarpeta", a.parametrizar)
    cuerpo = f'''    Origen = Folder.Files({ruta}),
    SoloCSV = Table.SelectRows(Origen, each Text.EndsWith([Name], ".csv")),
    LeerCSV = Table.AddColumn(SoloCSV, "Datos", each
        Table.PromoteHeaders(
            Csv.Document([Content], [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            [PromoteAllScalars=true])),
    Combinados = Table.Combine(LeerCSV[Datos]),
    #"Tipos" = Table.TransformColumnTypes(Combinados, {{ /* {{"Col", type text}} */ }})'''
    params = [("pRutaCarpeta", "carpeta que contiene los CSV")] if ruta == "pRutaCarpeta" else []
    return cuerpo, '#"Tipos"', params, ["Todos los CSV deben compartir el mismo esquema de columnas."]


def m_sql(a):
    servidor = _param(a.servidor, "pServidor", a.parametrizar)
    base = _param(a.base, "pBase", a.parametrizar)
    esquema = a.esquema or "dbo"
    tabla = a.tabla or "MiTabla"
    cuerpo = f'''    // Conecta a una VISTA, no SELECT * en M. Filtra/quita columnas temprano
    // para PRESERVAR el query folding (clic derecho > View Native Query).
    Origen = Sql.Database({servidor}, {base}),
    Tabla = Origen{{[Schema="{esquema}", Item="{tabla}"]}}[Data]
    // , Filtrado = Table.SelectRows(Tabla, each [Anio] >= 2023)  // folding-friendly'''
    params = []
    if servidor == "pServidor":
        params.append(("pServidor", "nombre/host del servidor SQL"))
    if base == "pBase":
        params.append(("pBase", "nombre de la base de datos"))
    notas = ["Mantén el folding: no uses Table.Buffer ni transformaciones que la fuente no pueda traducir a SQL."]
    if a.modo == "directquery":
        notas.append("DirectQuery: la fuente debe soportarlo; cada visual consulta en vivo. Configura el modo de la tabla en el modelo, no en M.")
    return cuerpo, "Tabla", params, notas


def m_databricks(a):
    host = "pHost"
    httppath = "pHttpPath"
    catalogo = _param(a.catalogo, "pCatalogo", a.parametrizar)
    esquema = a.esquema or "default"
    tabla = a.tabla or "mi_tabla"
    cuerpo = f'''    // Conector nativo Databricks (Unity Catalog). Evita ODBC generico.
    Origen = Databricks.Catalogs({host}, {httppath}, []),
    Cat = Origen{{[Name={catalogo}]}}[Data],
    Esq = Cat{{[Name="{esquema}"]}}[Data],
    Tabla = Esq{{[Name="{tabla}"]}}[Data]'''
    params = [
        ("pHost", "server hostname de Databricks (adb-....azuredatabricks.net)"),
        ("pHttpPath", "HTTP Path del SQL Warehouse / cluster"),
    ]
    if catalogo == "pCatalogo":
        params.append(("pCatalogo", "catalogo de Unity Catalog"))
    notas = ["Para volumenes grandes considera DirectQuery sobre un SQL Warehouse."]
    if a.modo == "directlake":
        notas.append("Direct Lake aplica a tablas Delta en OneLake (Fabric), no a Databricks directo.")
    return cuerpo, "Tabla", params, notas


def m_fabric_lakehouse(a):
    tabla = a.tabla or "mi_tabla"
    cuerpo = f'''    // Lakehouse de Fabric. Para Import/DirectQuery via M:
    Origen = Lakehouse.Contents([]),
    Ws = Origen{{[workspaceId = pWorkspaceId]}}[Data],
    Lh = Ws{{[lakehouseId = pLakehouseId]}}[Data],
    Tabla = Lh{{[Id="{tabla}", ItemKind="Table"]}}[Data]'''
    params = [
        ("pWorkspaceId", "GUID del workspace de Fabric"),
        ("pLakehouseId", "GUID del Lakehouse"),
    ]
    notas = []
    if a.modo == "directlake":
        notas.append("Direct Lake es el modo PREFERIDO en Fabric: el modelo lee las tablas Delta de OneLake directamente, SIN codigo M. Usa este M solo si necesitas Import/DirectQuery.")
    return cuerpo, "Tabla", params, notas


CONSTRUCTORES = {
    "excel": m_excel,
    "sharepoint-archivo": m_sharepoint_archivo,
    "sharepoint-lista": m_sharepoint_lista,
    "carpeta-csv": m_carpeta_csv,
    "sql": m_sql,
    "databricks": m_databricks,
    "fabric-lakehouse": m_fabric_lakehouse,
}


def render(a):
    cuerpo, paso_final, params, notas = CONSTRUCTORES[a.fuente](a)
    nombre = a.tabla or "Consulta"

    lineas = []
    lineas.append("// " + "=" * 72)
    lineas.append(f"// Power Query M  |  fuente: {a.fuente}  |  modo: {a.modo}")
    lineas.append(f"// Tabla/consulta: {nombre}")
    lineas.append("// Pegar en: Inicio > Transformar datos > Editor avanzado (una consulta por tabla).")
    if params:
        lineas.append("//")
        lineas.append("// PARAMETROS a crear (Inicio > Administrar parametros):")
        for nom, desc in params:
            lineas.append(f"//   {nom:<14} {desc}")
    for n in notas:
        lineas.append(f"// NOTA: {n}")
    lineas.append("// " + "=" * 72)
    lineas.append("let")
    lineas.append(cuerpo)
    lineas.append("in")
    lineas.append(f"    {paso_final}")
    return "\n".join(lineas) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Genera codigo Power Query M por fuente (parametrizado, folding-friendly).")
    ap.add_argument("--fuente", required=True, choices=sorted(CONSTRUCTORES))
    ap.add_argument("--tabla", help="Nombre de la tabla/consulta resultante.")
    ap.add_argument("--modo", default="import",
                    choices=["import", "directquery", "directlake"])
    ap.add_argument("--parametrizar", dest="parametrizar", action="store_true", default=True)
    ap.add_argument("--no-parametrizar", dest="parametrizar", action="store_false")
    # por fuente
    ap.add_argument("--servidor")
    ap.add_argument("--base")
    ap.add_argument("--esquema")
    ap.add_argument("--sitio")
    ap.add_argument("--ruta")
    ap.add_argument("--archivo")
    ap.add_argument("--hoja")
    ap.add_argument("--lista")
    ap.add_argument("--catalogo")
    ap.add_argument("--salida", help="Archivo .m de salida (default: consola).")
    args = ap.parse_args()

    texto = render(args)
    if args.salida:
        with open(args.salida, "w", encoding="utf-8", newline="") as f:
            f.write(texto)
        print(f"OK  M -> {args.salida}  (fuente: {args.fuente}, modo: {args.modo})")
    else:
        sys.stdout.write(texto)


if __name__ == "__main__":
    main()
