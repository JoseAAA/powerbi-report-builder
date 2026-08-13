#!/usr/bin/env python3
"""
scaffold_pbip.py - Genera un PROYECTO POWER BI PBIP MÍNIMO Y VÁLIDO desde cero.

Crea un esqueleto de modelo en estrella (TMDL) + un reporte PBIR, listo para
abrir y modificar en Power BI Desktop (formato CY26 / PBIR, marzo 2026+). Es
GENERICO Y MULTI-DOMINIO: elige el dominio con --dominio (no esta atado a
ninguna empresa ni sector). Si pasas --tema, aplica ese tema de marca.

El formato (rutas, $schema y versiones) se clonó de un proyecto PBIP real CY26.
No se inventaron URLs de schema ni versiones.

USO
---
  # esqueleto generico con el base theme (sin tema custom)
  python scaffold_pbip.py --nombre "Mi Reporte"

  # dominio + tema de marca custom (genéralo antes con generar_theme.py)
  python scaffold_pbip.py --nombre "Reporte Ventas" --dominio ventas \
      --salida /tmp/pbip-prueba --tema /tmp/mi_theme.json

ARGUMENTOS
----------
  --nombre   Nombre del reporte (requerido). Da nombre a la carpeta y los items.
  --dominio  ventas | rrhh | finanzas | salud | generico (default: generico).
  --salida   Carpeta destino (default: carpeta actual).
  --tema     Ruta a un theme.json (opcional). Si se pasa, se coloca como tema
             custom en StaticResources/RegisteredResources y se referencia en
             report.json vía themeCollection.customTheme. Si no, se usa el base
             theme CY26SU02.

MODELO ESTRELLA GENERADO (nombres de negocio, sin prefijos dim_/fact_)
----------------------------------------------------------------------
  Calendario   tabla de fecha (marcada con dataCategory=Time). NO usa Auto date/time.
  <Dim1>       dimensión 1 (según dominio: Region, Sede, Departamento, …).
  <Dim2>       dimensión 2 con columna de agrupación (Producto, Servicio, …).
  Indicador    dimensión de indicadores: qué mide cada fila del hecho. NO es
               opcional — el hecho es "alto" (una fila por indicador), así que
               sin ella las medidas suman porcentajes junto con importes.
  <Hecho>      hecho: Fecha, claves a las dimensiones, Num, Den (claves ocultas).
  _ Medidas    tabla de medidas oculta con medidas DAX conscientes del indicador
               (VAR/RETURN, DIVIDE, guarda HASONEVALUE y una medida principal
               filtrada con CALCULATE).

ORIGEN DE LOS DATOS (dos modos)
-------------------------------
  con --datos <carpeta>  las particiones LEEN los CSV de esa carpeta a través
                         del parámetro RutaBase (expressions.tmdl). Es el modo
                         normal: abres el .pbip, refrescas y ves tus datos; si
                         corriges un CSV y refrescas, el reporte cambia.
  sin --datos            particiones con #table(...) inline. Esqueleto que abre
                         sin ninguna fuente externa.

Solo usa la librería estándar de Python (json, os, uuid, argparse, shutil,
secrets).
"""
import argparse
import json
import os
import re
import secrets
import shutil
import sys
import uuid

# Catalogo de dominios compartido con generar_datos_ejemplo.py (fuente unica).
# Antes estaba duplicado en los dos scripts y divergio en TODOS los dominios.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arquetipos  # noqa: E402
from dominios import (  # noqa: E402
    DOMINIOS, TABLA_INDICADOR, esquema_csv, filas_indicador, orden_tablas,
)

# ---------------------------------------------------------------------------
# CONSTANTES DE FORMATO — clonadas 1:1 de un proyecto PBIP real CY26
# (no inventar: estos $schema y versiones salen de inspeccionar un ejemplo real)
# ---------------------------------------------------------------------------
SCHEMA_PBIP        = "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json"
SCHEMA_PLATFORM    = "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json"
SCHEMA_PBIR        = "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json"
SCHEMA_REPORT      = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json"
SCHEMA_REPORT_VER  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json"
SCHEMA_PAGES       = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
SCHEMA_PAGE        = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_VISUAL      = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
SCHEMA_PBISM       = "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json"

# Versiones tal cual aparecen en el ejemplo
PBIP_VERSION         = "1.0"
PLATFORM_VERSION     = "2.0"
PBIR_VERSION         = "4.0"
PBISM_VERSION        = "4.2"
REPORT_VERSION_META  = "2.0.0"
COMPAT_LEVEL         = 1600
# reportVersionAtImport del base theme (idéntico al ejemplo)
THEME_REPORT_VERSIONS = {"visual": "2.6.0", "report": "3.1.0", "page": "2.3.0"}
BASE_THEME_NAME      = "CY26SU02"


# ---------------------------------------------------------------------------
# El catalogo de dominios vive en `dominios.py` (importado arriba). Estuvo
# duplicado aqui y en generar_datos_ejemplo.py, y los dos diccionarios
# divergieron en TODOS los dominios: ventas declaraba 6 productos en los CSV
# y 4 en el TMDL, salud 8 servicios vs 4. Resultado: los datos de ejemplo y
# el .pbip describian modelos distintos.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Particiones M: leer los CSV de ejemplo, o datos inline como respaldo
#
# El modelo puede nacer de dos maneras:
#   con --datos  -> las particiones leen los CSV reales via el parametro
#                   RutaBase. Es el modo normal: el .pbip que abres muestra
#                   exactamente los datos que hay en la carpeta, y si corriges
#                   un CSV basta refrescar para ver el cambio.
#   sin --datos  -> particiones con #table(...) inline (pocas filas). Sirve para
#                   un esqueleto que abre sin ninguna fuente externa.
#
# Antes solo existia el segundo modo, asi que generar datos y generar el .pbip
# producian artefactos desconectados: el reporte mostraba 6 filas inventadas
# mientras miles de filas reales quedaban huerfanas en la carpeta de al lado.
# ---------------------------------------------------------------------------
M_IND = "\t\t\t\t"  # indentacion de una expresion M dentro de una particion TMDL

# Formato canonico de porcentaje que exige la regla oficial PERCENTAGE_FORMATTING
# de Microsoft (BPARules.json), literal: no vale "0.0%;-0.0%;0.0%".
FMT_PORCENTAJE = "#,0.0%;-#,0.0%;#,0.0%"


def _nombre_archivo_tema(nombre_tema):
    """
    Nombre de archivo para el tema incrustado, derivado del nombre del tema.

    Microsoft exige que el `name` interno del tema, `customTheme.name`, y el
    `name`/`path` del item de resourcePackages sean IDENTICOS y terminen en
    ".json". Como ese valor es a la vez nombre de archivo en disco, hay que
    sanearlo: se quitan los caracteres invalidos en Windows y los separadores de
    ruta (evita escribir fuera de RegisteredResources).
    """
    base = (nombre_tema or "theme_custom").strip()
    if base.lower().endswith(".json"):
        base = base[:-5]
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", base).strip(" .")
    base = re.sub(r"\s+", " ", base)
    if not base:
        base = "theme_custom"
    return base[:80] + ".json"


def m_texto(valor):
    """
    Literal de texto para Power Query M.

    OJO: M **no** usa la barra invertida como caracter de escape. En M la ruta
    se escribe tal cual, `"C:\\Datos\\archivo.csv"` en Python == C:\\Datos... en
    disco se ve como C:\\Datos\\archivo.csv y M lo lee literal. Por eso NO se
    puede usar json.dumps() aqui: duplicaria cada barra y el modelo buscaria
    una ruta inexistente con dobles separadores.

    Lo unico que hay que escapar es la comilla doble, duplicandola, y los
    caracteres de control, que en M van con la sintaxis #(...).
    """
    return '"' + valor.replace('"', '""') + '"'


def _particion_encabezado(tabla):
    return f"\tpartition {tq(tabla)} = m\n\t\tmode: import\n\t\tsource =\n"


def particion_csv(tabla, columnas, filtro=None):
    """
    Particion que lee '<tabla>.csv' relativo al parametro compartido RutaBase.

    Usa Csv.Document + File.Contents con Encoding=65001 (UTF-8) porque los CSV
    se escriben con BOM para que Excel y Power BI lean las tildes. Los tipos
    salen de `dominios.esquema_csv`, la misma fuente que usa el codigo M, de
    modo que el modelo y los datos no puedan declarar tipos distintos.
    """
    tipos = ",\n".join(
        '{}        {{"{}", {}}}'.format(M_IND, col, tipo) for col, tipo in columnas)
    paso_final = '#"Tipo cambiado"'
    extra = ""
    if filtro:
        extra = (
            f',\n{M_IND}    // {filtro["nota"]}\n'
            f'{M_IND}    #"Filas filtradas" = Table.SelectRows(#"Tipo cambiado", '
            f'{filtro["expr"]})')
        paso_final = '#"Filas filtradas"'
    return (
        _particion_encabezado(tabla)
        + f"{M_IND}let\n"
        + f"{M_IND}    Origen = Csv.Document(\n"
        + f'{M_IND}        File.Contents(RutaBase & "\\{tabla}.csv"),\n'
        + f"{M_IND}        [Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]\n"
        + f"{M_IND}    ),\n"
        + f"{M_IND}    EncabezadosPromovidos = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),\n"
        + f'{M_IND}    #"Tipo cambiado" = Table.TransformColumnTypes(EncabezadosPromovidos, {{\n'
        + tipos + "\n"
        + f"{M_IND}    }}){extra}\n"
        + f"{M_IND}in\n"
        + f"{M_IND}    {paso_final}\n"
    )


def particion_inline(tabla, tipo_table, filas):
    """Particion con datos inline #table(...): esqueleto sin fuente externa."""
    return (
        _particion_encabezado(tabla)
        + f"{M_IND}let\n"
        + f"{M_IND}    Origen = #table(\n"
        + f"{M_IND}        type table [{tipo_table}],\n"
        + f"{M_IND}        {{\n"
        + filas + "\n"
        + f"{M_IND}        }}\n"
        + f"{M_IND}    )\n"
        + f"{M_IND}in\n"
        + f"{M_IND}    Origen\n"
    )


def tmdl_expressions(ruta_datos):
    """
    expressions.tmdl con el parametro compartido RutaBase.

    Sin este archivo no hay forma de parametrizar la ruta de los CSV: las
    particiones tendrian que llevar la ruta absoluta incrustada. Es un
    parametro de Power Query de verdad (IsParameterQuery), asi que el usuario
    lo cambia desde Inicio > Transformar datos > Administrar parametros sin
    tocar una sola consulta.

    Sintaxis oficial de TMDL para expresiones compartidas:
      expression <Nombre> = <valor> meta [IsParameterQuery=true, Type=..., ...]
    (Microsoft Learn - Tabular Model Definition Language, seccion del ejemplo
    `expression Server = "localhost" meta [...]`).
    """
    valor = m_texto(ruta_datos)
    return (
        "/// Carpeta que contiene los CSV de datos. Cambiala desde Inicio >\n"
        "/// Transformar datos > Administrar parametros; todas las consultas la usan.\n"
        f"expression RutaBase = {valor} "
        "meta [IsParameterQuery=true, Type=\"Text\", IsParameterQueryRequired=true]\n"
        "\n"
        "\tannotation PBI_ResultType = Text\n"
    )


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def validar_nombre(nombre):
    """--nombre se usa como nombre de carpetas/archivos: rechaza separadores de
    ruta, '..' y caracteres invalidos en Windows (evita escribir fuera de --salida).
    """
    if not nombre or nombre != nombre.strip():
        raise SystemExit("ERROR: --nombre vacio o con espacios al inicio/fin.")
    if ".." in nombre or re.search(r'[<>:"/\\|?*\x00-\x1f]', nombre):
        raise SystemExit(
            "ERROR: --nombre contiene caracteres invalidos "
            "(/ \\ : * ? \" < > | o '..'). Usa letras, numeros, espacios o guiones.")
    return nombre


def nuevo_guid():
    """GUID nuevo (para lineageTag y logicalId)."""
    return str(uuid.uuid4())


def nombre_hex():
    """Nombre hex de 20 caracteres para páginas/visuales (igual al ejemplo)."""
    return secrets.token_hex(10)


def tq(name):
    """TMDL-quote: 'nombre' si tiene espacio, si no el nombre tal cual."""
    return f"'{name}'" if " " in name else name


def mq(name):
    """M-quote para identificadores en #table: #\"nombre\" si tiene espacio."""
    return f'#"{name}"' if " " in name else name


def ruta_io(ruta):
    """Ruta apta para E/S en Windows aunque supere MAX_PATH (260).

    El árbol .Report/.SemanticModel agrega ~90 caracteres de profundidad
    propia (StaticResources/, definition/pages/<id>/visuals/<id>/...), así
    que una carpeta de salida honda revienta el límite clásico. El prefijo
    \\\\?\\ lo desactiva; en otros SO la ruta vuelve tal cual.
    """
    if os.name != "nt":
        return ruta
    ruta = os.path.abspath(ruta)
    if ruta.startswith("\\\\?\\"):
        return ruta
    if ruta.startswith("\\\\"):  # UNC: \\server\share -> \\?\UNC\server\share
        return "\\\\?\\UNC" + ruta[1:]
    return "\\\\?\\" + ruta


def escribir_json(ruta, obj):
    """Escribe un dict como JSON indentado y valida que reparsee."""
    ruta = ruta_io(ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    texto = json.dumps(obj, ensure_ascii=False, indent=2)
    json.loads(texto)  # validación temprana
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


def escribir_texto(ruta, texto):
    """Escribe texto plano (TMDL) en UTF-8."""
    ruta = ruta_io(ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


# ---------------------------------------------------------------------------
# TMDL — tablas del modelo estrella (parametricas por dominio)
# Indentación con TAB, una línea en blanco entre objetos hermanos.
# ---------------------------------------------------------------------------
def tmdl_calendario(dom, usar_csv):
    """
    Tabla Calendario marcada como tabla de fecha (dataCategory=Time).

    Con usar_csv lee Calendario.csv (rango real de los datos); sin el, construye
    el calendario inline con List.Dates. Incluye EsDiaHabil porque el CSV la
    trae: si el modelo no declarara la columna, la particion la cargaria como
    columna no tipada y el modelo quedaria distinto a los datos.
    """
    lt_tabla = nuevo_guid()
    lt_fecha = nuevo_guid()
    lt_anio = nuevo_guid()
    lt_mes = nuevo_guid()
    lt_nummes = nuevo_guid()
    lt_trim = nuevo_guid()
    lt_habil = nuevo_guid()
    if usar_csv:
        particion = particion_csv("Calendario", esquema_csv(dom)["Calendario"])
    else:
        particion = (
            _particion_encabezado("Calendario")
            + f"{M_IND}let\n"
            + f"{M_IND}    Fechas = List.Dates(#date(2024, 1, 1), 731, #duration(1, 0, 0, 0)),\n"
            + f'{M_IND}    Tabla = Table.FromList(Fechas, Splitter.SplitByNothing(), {{"Fecha"}}),\n'
            + f'{M_IND}    Tipo = Table.TransformColumnTypes(Tabla, {{{{"Fecha", type date}}}}),\n'
            + f'{M_IND}    Anio = Table.AddColumn(Tipo, "Año", each Date.Year([Fecha]), Int64.Type),\n'
            + f'{M_IND}    NumMes = Table.AddColumn(Anio, "NumMes", each Date.Month([Fecha]), Int64.Type),\n'
            + f'{M_IND}    Mes = Table.AddColumn(NumMes, "Mes", each Date.ToText([Fecha], "MMMM", "es-ES"), type text),\n'
            + f'{M_IND}    Trim = Table.AddColumn(Mes, "Trimestre", each "T" & Text.From(Date.QuarterOfYear([Fecha])), type text),\n'
            + f'{M_IND}    Habil = Table.AddColumn(Trim, "EsDiaHabil", each if Date.DayOfWeek([Fecha], Day.Monday) < 5 then "Si" else "No", type text)\n'
            + f"{M_IND}in\n"
            + f"{M_IND}    Habil\n"
        )
    return f"""/// Calendario de fechas continuo, marcado como tabla de fecha. Filtra por esta
/// tabla y no por la fecha del hecho: es lo que hace funcionar la inteligencia de tiempo.
table Calendario
\tdataCategory: Time
\tlineageTag: {lt_tabla}

\tcolumn Fecha
\t\tdataType: dateTime
\t\tisKey
\t\tformatString: Short Date
\t\tlineageTag: {lt_fecha}
\t\tsummarizeBy: none
\t\tsourceColumn: Fecha

\t\tannotation SummarizationSetBy = Automatic

\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn Año
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: {lt_anio}
\t\tsummarizeBy: none
\t\tsourceColumn: Año

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Mes
\t\tdataType: string
\t\tlineageTag: {lt_mes}
\t\tsummarizeBy: none
\t\tsourceColumn: Mes
\t\tsortByColumn: NumMes

\t\tannotation SummarizationSetBy = Automatic

\tcolumn NumMes
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: {lt_nummes}
\t\tsummarizeBy: none
\t\tsourceColumn: NumMes

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Trimestre
\t\tdataType: string
\t\tlineageTag: {lt_trim}
\t\tsummarizeBy: none
\t\tsourceColumn: Trimestre

\t\tannotation SummarizationSetBy = Automatic

\tcolumn EsDiaHabil
\t\tdataType: string
\t\tlineageTag: {lt_habil}
\t\tsummarizeBy: none
\t\tsourceColumn: EsDiaHabil

\t\tannotation SummarizationSetBy = Automatic

{particion}
\tannotation PBI_ResultType = Table
"""


def tmdl_dim1(dom, usar_csv):
    """Dimensión 1: columnas 'ID <dim1>' (clave) y <dim1>."""
    dim1, filas_dom = dom["dim1"]
    id1 = "ID " + dim1
    lt_tabla, lt_id, lt_nombre = nuevo_guid(), nuevo_guid(), nuevo_guid()
    if usar_csv:
        particion = particion_csv(dim1, esquema_csv(dom)[dim1])
    else:
        filas = ",\n".join(
            '%s            {%d, "%s"}' % (M_IND, i, n) for i, n in filas_dom)
        tipo = "{} = Int64.Type, {} = text".format(mq(id1), mq(dim1))
        particion = particion_inline(dim1, tipo, filas)
    return f"""/// Dimension {dim1}: atributo por el que se corta el negocio. Una fila por miembro.
table {tq(dim1)}
\tlineageTag: {lt_tabla}

\tcolumn '{id1}'
\t\tdataType: int64
\t\tisKey
\t\tformatString: 0
\t\tlineageTag: {lt_id}
\t\tsummarizeBy: none
\t\tsourceColumn: {id1}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn {tq(dim1)}
\t\tdataType: string
\t\tlineageTag: {lt_nombre}
\t\tsummarizeBy: none
\t\tsourceColumn: {dim1}

\t\tannotation SummarizationSetBy = Automatic

{particion}
\tannotation PBI_ResultType = Table
"""


def tmdl_dim2(dom, usar_csv):
    """Dimensión 2: 'ID <dim2>' (clave), <dim2> y la columna de agrupación."""
    dim2, col_grupo, filas_dom = dom["dim2"]
    id2 = "ID " + dim2
    lt_tabla, lt_id, lt_nombre, lt_grupo = (nuevo_guid(), nuevo_guid(),
                                            nuevo_guid(), nuevo_guid())
    if usar_csv:
        particion = particion_csv(dim2, esquema_csv(dom)[dim2])
    else:
        filas = ",\n".join(
            '%s            {%d, "%s", "%s"}' % (M_IND, i, n, g)
            for i, n, g in filas_dom)
        tipo = "{} = Int64.Type, {} = text, {} = text".format(
            mq(id2), mq(dim2), mq(col_grupo))
        particion = particion_inline(dim2, tipo, filas)
    return f"""/// Dimension {dim2}, con la columna {col_grupo} para agrupar y jerarquizar.
table {tq(dim2)}
\tlineageTag: {lt_tabla}

\tcolumn '{id2}'
\t\tdataType: int64
\t\tisKey
\t\tformatString: 0
\t\tlineageTag: {lt_id}
\t\tsummarizeBy: none
\t\tsourceColumn: {id2}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn {tq(dim2)}
\t\tdataType: string
\t\tlineageTag: {lt_nombre}
\t\tsummarizeBy: none
\t\tsourceColumn: {dim2}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn {tq(col_grupo)}
\t\tdataType: string
\t\tlineageTag: {lt_grupo}
\t\tsummarizeBy: none
\t\tsourceColumn: {col_grupo}

\t\tannotation SummarizationSetBy = Automatic

{particion}
\tannotation PBI_ResultType = Table
"""


def tmdl_indicador(dom, usar_csv):
    """
    Dimensión Indicador: qué mide cada fila del hecho.

    NO es opcional. El hecho es alto (una fila por indicador), asi que sin esta
    tabla la clave 'ID Indicador' no apunta a nada y cualquier medida suma
    porcentajes junto con importes absolutos. En el dominio ventas eso daba
    DIVIDE(SUM(Num), SUM(Den)) = 5226%, mezclando '% Margen' con
    'Ticket Promedio'. La columna Formato guarda el formatString sugerido por
    indicador, util para el patron de medida con formato dinamico.
    """
    ind = TABLA_INDICADOR
    id_ind = "ID " + ind
    lt_tabla, lt_id, lt_nombre, lt_tipo, lt_fmt = (
        nuevo_guid(), nuevo_guid(), nuevo_guid(), nuevo_guid(), nuevo_guid())
    if usar_csv:
        particion = particion_csv(ind, esquema_csv(dom)[ind])
    else:
        filas = ",\n".join(
            '%s            {%d, "%s", "%s", "%s"}' % (M_IND, i, n, t, f)
            for i, n, t, f in filas_indicador(dom))
        tipo = "{} = Int64.Type, {} = text, Tipo = text, Formato = text".format(
            mq(id_ind), mq(ind))
        particion = particion_inline(ind, tipo, filas)
    return f"""/// Que mide cada fila del hecho. Segmenta por esta tabla para leer un indicador a
/// la vez: sumar varios mezclaria porcentajes con importes absolutos.
table {tq(ind)}
\tlineageTag: {lt_tabla}

\tcolumn '{id_ind}'
\t\tdataType: int64
\t\tisKey
\t\tformatString: 0
\t\tlineageTag: {lt_id}
\t\tsummarizeBy: none
\t\tsourceColumn: {id_ind}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn {tq(ind)}
\t\tdataType: string
\t\tlineageTag: {lt_nombre}
\t\tsummarizeBy: none
\t\tsourceColumn: {ind}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Tipo
\t\tdataType: string
\t\tlineageTag: {lt_tipo}
\t\tsummarizeBy: none
\t\tsourceColumn: Tipo

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Formato
\t\tdataType: string
\t\tisHidden
\t\tlineageTag: {lt_fmt}
\t\tsummarizeBy: none
\t\tsourceColumn: Formato

\t\tannotation SummarizationSetBy = Automatic

{particion}
\tannotation PBI_ResultType = Table
"""


def _filas_hecho(dom):
    """
    Filas de muestra del hecho (solo modo inline, sin --datos):
    (fecha M, id_dim1, id_dim2, id_indicador, Num, Den).

    Incluye ID Indicador porque el hecho es alto: cada fila mide UN indicador.
    Se genera una fila por indicador y por fecha para que el modelo de muestra
    tenga la misma forma que los datos reales.
    """
    d1_ids = [r[0] for r in dom["dim1"][1]]
    d2_ids = [r[0] for r in dom["dim2"][2]]
    fechas = ["#date(2024, 1, 15)", "#date(2024, 2, 15)", "#date(2024, 3, 15)",
              "#date(2025, 1, 15)", "#date(2025, 2, 15)", "#date(2025, 3, 15)"]
    filas = []
    for i, fecha in enumerate(fechas):
        d1 = d1_ids[i % len(d1_ids)]
        d2 = d2_ids[i % len(d2_ids)]
        for ind_id, _nombre, (num_lo, num_hi), (den_lo, den_hi) in dom["indicadores"]:
            # Valores deterministas dentro del rango del indicador (sin random:
            # el esqueleto debe ser reproducible byte a byte).
            den = (den_lo + den_hi) // 2
            num = (num_lo + num_hi) // 2
            if ind_id in dom["pct"] and num > den:
                num = den
            filas.append("%s            {%s, %d, %d, %d, %d, %d}"
                         % (M_IND, fecha, d1, d2, ind_id, num, den))
    return ",\n".join(filas)


def tmdl_hecho(dom, usar_csv):
    """
    Tabla de hechos. Claves a las dimensiones ocultas; Num/Den ocultas.

    Grain: una fila por Fecha x dim1 x dim2 x indicador. La clave 'ID Indicador'
    es parte del grano, no un extra: sin ella no se puede saber que mide cada
    fila y las medidas suman indicadores incompatibles.
    """
    dim1 = dom["dim1"][0]
    dim2 = dom["dim2"][0]
    hecho = dom["hecho"]
    id1, id2 = "ID " + dim1, "ID " + dim2
    id_ind = "ID " + TABLA_INDICADOR
    lt_tabla, lt_fecha, lt_d1, lt_d2, lt_ind, lt_num, lt_den = (
        nuevo_guid(), nuevo_guid(), nuevo_guid(), nuevo_guid(),
        nuevo_guid(), nuevo_guid(), nuevo_guid())
    if usar_csv:
        particion = particion_csv(hecho, esquema_csv(dom)[hecho], filtro={
            "nota": "descarta registros sin denominador (evita dividir por 0).",
            "expr": "each [Den] <> null and [Den] > 0",
        })
    else:
        tipo = ("Fecha = date, {} = Int64.Type, {} = Int64.Type, "
                "{} = Int64.Type, Num = Int64.Type, Den = Int64.Type").format(
            mq(id1), mq(id2), mq(id_ind))
        particion = particion_inline(hecho, tipo, _filas_hecho(dom))
    return f"""/// Hecho {hecho}. Grano: una fila por fecha, {dim1}, {dim2} e indicador, con el patron
/// Num/Den. Las claves y las metricas base van ocultas: consulta el modelo con las medidas.
table {tq(hecho)}
\tlineageTag: {lt_tabla}

\tcolumn Fecha
\t\tdataType: dateTime
\t\tformatString: Short Date
\t\tlineageTag: {lt_fecha}
\t\tsummarizeBy: none
\t\tsourceColumn: Fecha

\t\tannotation SummarizationSetBy = Automatic

\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn '{id1}'
\t\tdataType: int64
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: {lt_d1}
\t\tsummarizeBy: none
\t\tsourceColumn: {id1}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn '{id2}'
\t\tdataType: int64
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: {lt_d2}
\t\tsummarizeBy: none
\t\tsourceColumn: {id2}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn '{id_ind}'
\t\tdataType: int64
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: {lt_ind}
\t\tsummarizeBy: none
\t\tsourceColumn: {id_ind}

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Num
\t\tdataType: int64
\t\tformatString: 0
\t\tisHidden
\t\tlineageTag: {lt_num}
\t\tsummarizeBy: sum
\t\tsourceColumn: Num

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Den
\t\tdataType: int64
\t\tformatString: 0
\t\tisHidden
\t\tlineageTag: {lt_den}
\t\tsummarizeBy: sum
\t\tsourceColumn: Den

\t\tannotation SummarizationSetBy = Automatic

{particion}
\tannotation PBI_ResultType = Table
"""


def medida_principal(dom):
    """Nombre y formato del primer indicador del dominio (el que usan las tarjetas)."""
    nombre = dom["indicadores"][0][1]
    formato = filas_indicador(dom)[0][3]
    return nombre, formato


def tmdl_medidas(dom):
    """
    Tabla de medidas oculta '_ Medidas'. Tabla calculada de una columna en blanco.

    Las medidas son CONSCIENTES DEL INDICADOR, y eso no es un adorno. El hecho
    guarda una fila por indicador, asi que un DIVIDE(SUM(Num), SUM(Den)) sin
    filtrar suma '% Margen' con 'Ticket Promedio' y devuelve 5226%. Dos defensas:

      1. 'Indicador %' exige UN solo indicador en contexto (HASONEVALUE) y
         devuelve BLANK si hay ambiguedad. Preferimos una celda vacia a un
         numero falso.
      2. Una medida explicita por el indicador principal, con CALCULATE, para
         que las tarjetas muestren siempre un valor correcto sin depender de
         que el usuario segmente.

    Fundamento: DIVIDE en vez de '/', VAR/RETURN, medidas en lugar de columnas
    calculadas, descripciones /// para Copilot y agentes (SQLBI, Microsoft,
    Tabular Editor BPA).
    """
    hecho = dom["hecho"]
    ind = TABLA_INDICADOR
    nombre_ppal, formato_ppal = medida_principal(dom)
    lt_tabla, lt_col = nuevo_guid(), nuevo_guid()
    lt_num, lt_den, lt_ind, lt_ppal = (
        nuevo_guid(), nuevo_guid(), nuevo_guid(), nuevo_guid())
    return f"""table '_ Medidas'
\tisHidden
\tlineageTag: {lt_tabla}

\t/// Suma del numerador del indicador (columna Num del hecho). Medida base para construir cocientes; no se muestra sola.
\tmeasure Numerador = ```
\t\t\tVAR Resultado = SUM ( {tq(hecho)}[Num] )
\t\t\tRETURN
\t\t\t    Resultado
\t\t\t```
\t\tformatString: #,0
\t\tdisplayFolder: Base
\t\tisHidden
\t\tlineageTag: {lt_num}

\t/// Suma del denominador del indicador (columna Den del hecho). Medida base para construir cocientes; no se muestra sola.
\tmeasure Denominador = ```
\t\t\tVAR Resultado = SUM ( {tq(hecho)}[Den] )
\t\t\tRETURN
\t\t\t    Resultado
\t\t\t```
\t\tformatString: #,0
\t\tdisplayFolder: Base
\t\tisHidden
\t\tlineageTag: {lt_den}

\t/// Valor del indicador seleccionado (Numerador / Denominador). Devuelve BLANK si hay mas de un indicador en contexto, porque sumar indicadores distintos (un porcentaje y un importe) daria un numero sin significado. Segmenta por Indicador para verlo.
\tmeasure 'Indicador %' = ```
\t\t\tVAR UnSoloIndicador = HASONEVALUE ( {tq(ind)}[{ind}] )
\t\t\tVAR Resultado = DIVIDE ( [Numerador], [Denominador] )
\t\t\tRETURN
\t\t\t    IF ( UnSoloIndicador, Resultado )
\t\t\t```
\t\tformatString: {FMT_PORCENTAJE}
\t\tdisplayFolder: Indicadores
\t\tlineageTag: {lt_ind}

\t/// {nombre_ppal}: indicador principal del reporte, filtrado explicitamente con CALCULATE. Muestra siempre un valor correcto aunque no haya segmentacion por Indicador.
\tmeasure '{nombre_ppal}' = ```
\t\t\tVAR Resultado =
\t\t\t    CALCULATE (
\t\t\t        DIVIDE ( [Numerador], [Denominador] ),
\t\t\t        {tq(ind)}[{ind}] = "{nombre_ppal}"
\t\t\t    )
\t\t\tRETURN
\t\t\t    Resultado
\t\t\t```
\t\tformatString: {formato_ppal}
\t\tdisplayFolder: Indicadores
\t\tlineageTag: {lt_ppal}

\tcolumn Valor
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: {lt_col}
\t\tsummarizeBy: none
\t\tsourceColumn: [Valor]

\t\tannotation SummarizationSetBy = Automatic

\tpartition '_ Medidas' = calculated
\t\tmode: import
\t\tsource = ```
\t\t\t\tSELECTCOLUMNS ( {{ BLANK() }}, "Valor", BLANK() )
\t\t\t\t```

\tannotation PBI_ResultType = Calculated
"""


def tmdl_relationships(rels):
    """Genera relationships.tmdl con relaciones dimensión->hecho.
    rels: lista de tuplas (from_tabla, from_col, to_tabla, to_col).
    fromColumn es el lado * (hecho) y toColumn el lado 1 (dimensión).
    Tablas y columnas con espacios se citan con comillas simples.
    """
    bloques = []
    for (from_t, from_c, to_t, to_c) in rels:
        guid = nuevo_guid()
        fc = f"{tq(from_t)}.{tq(from_c)}"
        tc = f"{tq(to_t)}.{tq(to_c)}"
        bloques.append(
            f"relationship {guid}\n"
            f"\tfromColumn: {fc}\n"
            f"\ttoColumn: {tc}\n"
        )
    return "\n".join(bloques)


def tmdl_model(nombre_modelo, tablas_orden, cultura, con_expresiones):
    """
    model.tmdl. Desactiva Auto date/time (__PBI_TimeIntelligenceEnabled = 0)
    para NO generar tablas LocalDateTable.

    `cultura` se aplica a culture y sourceQueryCulture. Antes estaba fijo en
    es-ES / es-PE: una cultura de un pais concreto incrustada en un framework
    generico, que nadie eligio. Ahora es un parametro con default neutro.

    `con_expresiones` agrega el `ref expression RutaBase` para preservar el
    orden de la coleccion en los round-trips de TMDL.
    """
    refs = "\n".join(f"ref table {tq(t)}" for t in tablas_orden)
    if con_expresiones:
        refs += "\n\nref expression RutaBase"
    orden_json = json.dumps(tablas_orden, ensure_ascii=False)
    return f"""model Model
\tculture: {cultura}
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: {cultura}
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_QueryOrder = {orden_json}

annotation PBI_ProTooling = ["TMDLView_Desktop","DevMode"]

{refs}
"""


# ---------------------------------------------------------------------------
# Reporte PBIR
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Constructor generico de visuales, con altText OBLIGATORIO.
#
# `PBI-A11Y-01` (alt text en todo visual que transmita informacion) es la regla de
# mayor severidad del catalogo de visualizacion, y este generador la incumplia en
# el 100% de los visuales que producia. Ahora el alt es un parametro requerido:
# no se puede construir un visual sin el.
#
# El alt describe el INSIGHT, no el aspecto — el lector de pantalla ya anuncia
# titulo y tipo de visual. Limite duro de 250 caracteres.
# learn.microsoft.com/power-bi/create-reports/desktop-accessibility-creating-reports
# ---------------------------------------------------------------------------

def _lit(valor):
    """Propiedad literal de PBIR: el valor de texto va entre comillas simples."""
    return {"expr": {"Literal": {"Value": f"'{valor}'"}}}


def campo_medida(entidad, propiedad):
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": entidad}},
                              "Property": propiedad}},
        "queryRef": f"{entidad}.{propiedad}",
        "nativeQueryRef": propiedad,
    }


def campo_columna(entidad, propiedad, activo=False):
    c = {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": entidad}},
                             "Property": propiedad}},
        "queryRef": f"{entidad}.{propiedad}",
        "nativeQueryRef": propiedad,
    }
    if activo:
        c["active"] = True
    return c


def visual(tipo, pos, alt, roles=None, titulo=None, orden_desc=None):
    """
    Un visual PBIR completo.

    tipo   : visualType (del cookbook de arquetipos.py, no inventado aqui)
    pos    : (x, y, w, h, tabOrder) — el tabOrder debe seguir el orden de lectura
             (WCAG 2.4.3)
    alt    : texto alternativo. OBLIGATORIO.
    roles  : {"Category": [campo...], "Y": [campo...]} segun el tipo de visual
    titulo : texto del titulo del visual (usa el mensaje, no el tema)
    """
    if not alt or not alt.strip():
        raise ValueError(
            f"visual '{tipo}' sin altText. Es la regla de accesibilidad de mayor "
            "severidad (PBI-A11Y-01): sin alt, un lector de pantalla solo anuncia "
            "el tipo de visual y el insight se pierde.")
    x, y, w, h, tab = pos
    name = nombre_hex()
    v = {"visualType": tipo, "drillFilterOtherVisuals": True}
    if roles:
        v["query"] = {"queryState": {
            rol: {"projections": campos} for rol, campos in roles.items() if campos}}
    if orden_desc:
        entidad, prop = orden_desc
        v["query"]["sortDefinition"] = {
            "sort": [{"field": {"Measure": {
                "Expression": {"SourceRef": {"Entity": entidad}},
                "Property": prop}}, "direction": "Descending"}],
            "isDefaultSort": True,
        }
    # altText vive en visualContainerObjects.general[].properties.altText
    objetos = {"general": [{"properties": {"altText": _lit(alt[:250])}}]}
    if titulo:
        objetos["title"] = [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": _lit(titulo),
        }}]
    v["visualContainerObjects"] = objetos
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": tab, "height": h, "width": w,
                     "tabOrder": tab},
        "visual": v,
    }


def visual_texto(pos, alt, texto, tamano=18):
    """
    Cuadro de texto: el MENSAJE de la pagina.

    El contenido de un textbox NO va en el titulo del contenedor: va en
    `visual.objects.general[].properties.paragraphs`. El catalogo oficial lo
    confirma — `catalog describe textbox` devuelve `roles: {}` y
    `formattingObjects: [general, text, values]`, y `formatting search textbox`
    localiza la propiedad en `general.paragraphs`.

    Poniendo solo `title` se renderiza una **caja vacia con barra de titulo**: el
    mensaje de la pagina no aparece. Y el mensaje es justo lo que sostiene el
    storytelling ("el titulo dice la conclusion, no el tema"), asi que el fallo se
    llevaba por delante lo mas importante de la pagina.
    """
    x, y, w, h, tab = pos
    name = nombre_hex()
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": tab, "height": h, "width": w,
                     "tabOrder": tab},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": texto,
                                "textStyle": {
                                    "fontSize": f"{tamano}pt",
                                    "fontWeight": "bold",
                                },
                            }],
                        }],
                    },
                }],
            },
            "visualContainerObjects": {
                "general": [{"properties": {"altText": _lit(alt[:250])}}],
            },
            "drillFilterOtherVisuals": True,
        },
    }


def visual_card(measure_entity, measure_prop):
    """Tarjeta (cardVisual) que muestra una medida."""
    name = nombre_hex()
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": 40, "y": 40, "z": 0, "height": 160, "width": 360, "tabOrder": 0},
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": measure_entity}},
                                        "Property": measure_prop,
                                    }
                                },
                                "queryRef": f"{measure_entity}.{measure_prop}",
                                "nativeQueryRef": measure_prop,
                            }
                        ]
                    }
                }
            },
            "drillFilterOtherVisuals": True,
        },
    }


def visual_barras(cat_entity, cat_prop, measure_entity, measure_prop):
    """Gráfico de barras (clusteredBarChart): medida por categoría."""
    name = nombre_hex()
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": 40, "y": 240, "z": 1, "height": 320, "width": 600, "tabOrder": 1},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": cat_entity}},
                                        "Property": cat_prop,
                                    }
                                },
                                "queryRef": f"{cat_entity}.{cat_prop}",
                                "nativeQueryRef": cat_prop,
                                "active": True,
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": measure_entity}},
                                        "Property": measure_prop,
                                    }
                                },
                                "queryRef": f"{measure_entity}.{measure_prop}",
                                "nativeQueryRef": measure_prop,
                            }
                        ]
                    },
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Measure": {
                                    "Expression": {"SourceRef": {"Entity": measure_entity}},
                                    "Property": measure_prop,
                                }
                            },
                            "direction": "Descending",
                        }
                    ],
                    "isDefaultSort": True,
                },
            },
            "drillFilterOtherVisuals": True,
        },
    }


def visual_titulo(titulo):
    """Cuadro de texto como título de la página."""
    name = nombre_hex()
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": 40, "y": 8, "z": 2, "height": 28, "width": 600, "tabOrder": 2},
        "visual": {
            "visualType": "textbox",
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{titulo}'"}}},
                            "fontSize": {"expr": {"Literal": {"Value": "18D"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


# ---------------------------------------------------------------------------
# Generación completa
# ---------------------------------------------------------------------------
def generar(nombre, salida, tema, dominio, datos=None, cultura="es-ES",
            base_en_salida=False, ruta_base=None):
    """
    Genera el proyecto PBIP completo.

    datos          : carpeta con los CSV. Si se pasa, las particiones los leen
                     via el parametro RutaBase y el .pbip muestra los datos
                     reales al abrirlo. Si es None, datos inline (#table).
    cultura        : culture / sourceQueryCulture del modelo.
    base_en_salida : True deja el .pbip directamente en `salida` (estructura
                     plana, el .pbip en la raiz del proyecto, que es lo que
                     espera Fabric Git Integration). False mantiene la
                     subcarpeta <nombre>/.
    ruta_base      : valor literal para el parametro RutaBase. Por defecto se
                     usa la ruta absoluta de `datos`, que es lo correcto en la
                     maquina del usuario (abre y funciona). Para un proyecto que
                     se va a VERSIONAR como ejemplo publico hay que pasar un
                     placeholder: una ruta absoluta con el nombre de usuario
                     dentro de un archivo commiteado es fuga de datos.
    """
    dom = DOMINIOS[dominio]
    dim1 = dom["dim1"][0]
    dim2 = dom["dim2"][0]
    hecho = dom["hecho"]
    usar_csv = datos is not None

    base = salida if base_en_salida else os.path.join(salida, nombre)
    report_dir = os.path.join(base, f"{nombre}.Report")
    sm_dir = os.path.join(base, f"{nombre}.SemanticModel")

    archivos = []  # rutas creadas, para validar JSON al final

    # --- .pbip (manifiesto) ---
    pbip = {
        "$schema": SCHEMA_PBIP,
        "version": PBIP_VERSION,
        "artifacts": [{"report": {"path": f"{nombre}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    }
    ruta_pbip = os.path.join(base, f"{nombre}.pbip")
    escribir_json(ruta_pbip, pbip)
    archivos.append(ruta_pbip)

    # =====================================================================
    # SEMANTIC MODEL
    # =====================================================================
    plat_sm = {
        "$schema": SCHEMA_PLATFORM,
        "metadata": {"type": "SemanticModel", "displayName": nombre},
        "config": {"version": PLATFORM_VERSION, "logicalId": nuevo_guid()},
    }
    r = os.path.join(sm_dir, ".platform")
    escribir_json(r, plat_sm)
    archivos.append(r)

    pbism = {"$schema": SCHEMA_PBISM, "version": PBISM_VERSION, "settings": {}}
    r = os.path.join(sm_dir, "definition.pbism")
    escribir_json(r, pbism)
    archivos.append(r)

    # database.tmdl
    escribir_texto(
        os.path.join(sm_dir, "definition", "database.tmdl"),
        f"database\n\tcompatibilityLevel: {COMPAT_LEVEL}\n",
    )

    # model.tmdl
    tablas = orden_tablas(dom)
    escribir_texto(
        os.path.join(sm_dir, "definition", "model.tmdl"),
        tmdl_model(nombre, tablas, cultura, usar_csv),
    )

    # expressions.tmdl — parametro RutaBase (solo si las particiones leen CSV).
    # Sin este archivo no hay forma de parametrizar la ruta de los datos.
    if usar_csv:
        escribir_texto(
            os.path.join(sm_dir, "definition", "expressions.tmdl"),
            tmdl_expressions(ruta_base or os.path.abspath(datos)),
        )

    # tablas (nombre de archivo = nombre de tabla)
    tdir = os.path.join(sm_dir, "definition", "tables")
    escribir_texto(os.path.join(tdir, "Calendario.tmdl"), tmdl_calendario(dom, usar_csv))
    escribir_texto(os.path.join(tdir, f"{dim1}.tmdl"), tmdl_dim1(dom, usar_csv))
    escribir_texto(os.path.join(tdir, f"{dim2}.tmdl"), tmdl_dim2(dom, usar_csv))
    escribir_texto(os.path.join(tdir, f"{TABLA_INDICADOR}.tmdl"),
                   tmdl_indicador(dom, usar_csv))
    escribir_texto(os.path.join(tdir, f"{hecho}.tmdl"), tmdl_hecho(dom, usar_csv))
    escribir_texto(os.path.join(tdir, "_ Medidas.tmdl"), tmdl_medidas(dom))

    # relationships.tmdl — dimensión->hecho (1->*)
    rels = [
        (hecho, "Fecha", "Calendario", "Fecha"),
        (hecho, "ID " + dim1, dim1, "ID " + dim1),
        (hecho, "ID " + dim2, dim2, "ID " + dim2),
        (hecho, "ID " + TABLA_INDICADOR, TABLA_INDICADOR,
         "ID " + TABLA_INDICADOR),
    ]
    escribir_texto(
        os.path.join(sm_dir, "definition", "relationships.tmdl"),
        tmdl_relationships(rels),
    )

    # =====================================================================
    # REPORT (PBIR)
    # =====================================================================
    plat_rep = {
        "$schema": SCHEMA_PLATFORM,
        "metadata": {"type": "Report", "displayName": nombre},
        "config": {"version": PLATFORM_VERSION, "logicalId": nuevo_guid()},
    }
    r = os.path.join(report_dir, ".platform")
    escribir_json(r, plat_rep)
    archivos.append(r)

    pbir = {
        "$schema": SCHEMA_PBIR,
        "version": PBIR_VERSION,
        "datasetReference": {"byPath": {"path": f"../{nombre}.SemanticModel"}},
    }
    r = os.path.join(report_dir, "definition.pbir")
    escribir_json(r, pbir)
    archivos.append(r)

    # version.json
    r = os.path.join(report_dir, "definition", "version.json")
    escribir_json(r, {"$schema": SCHEMA_REPORT_VER, "version": REPORT_VERSION_META})
    archivos.append(r)

    # --- tema: custom (si --tema) o base CY26SU02 (como el ejemplo) ---
    report_json = {"$schema": SCHEMA_REPORT}

    if tema:
        with open(tema, "r", encoding="utf-8") as f:
            tema_obj = json.load(f)
        # CUATRO valores tienen que ser IDENTICOS y terminar en ".json":
        #   1. el `name` interno del theme.json incrustado
        #   2. `themeCollection.customTheme.name` de report.json
        #   3. `resourcePackages[].items[].name`
        #   4. `resourcePackages[].items[].path`  (= nombre del archivo en disco)
        #
        # Si el `name` no lleva .json, Power BI Desktop abre bien pero **el reporte
        # publicado en el Service aplica el tema incorrectamente**: los colores del
        # usuario se pierden en silencio justo al llegar a produccion. Si el `name`
        # interno del tema no coincide con la referencia, el tema no carga.
        #
        # Ambas reglas las verifica el validador oficial de Microsoft
        # (@microsoft/powerbi-report-authoring-cli): diagnosticos
        # PBIR_THEME_NAME_MISSING_JSON_EXT y PBIR_THEME_FILE_NAME_MISMATCH.
        # Comprobado empiricamente: name interno sin extension => falla.
        #
        # El theme.json SUELTO conserva su nombre legible ("Tema corporativo");
        # solo la COPIA incrustada se reescribe para cumplir la regla.
        tema_ref = _nombre_archivo_tema(tema_obj.get("name"))
        tema_obj = dict(tema_obj, name=tema_ref)
        rr_dir = os.path.join(report_dir, "StaticResources", "RegisteredResources")
        ruta_tema = os.path.join(rr_dir, tema_ref)
        escribir_json(ruta_tema, tema_obj)
        archivos.append(ruta_tema)
        # ThemeMetadata REQUIERE name + reportVersionAtImport + type (schema oficial
        # report/3.x). Omitir reportVersionAtImport corrompe el report.json al abrir.
        report_json["themeCollection"] = {
            "customTheme": {
                "name": tema_ref,
                "reportVersionAtImport": THEME_REPORT_VERSIONS,
                "type": "RegisteredResources",
            }
        }
        report_json["resourcePackages"] = [
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [
                    {"name": tema_ref, "path": tema_ref, "type": "CustomTheme"}
                ],
            }
        ]
    else:
        bt_dir = os.path.join(report_dir, "StaticResources", "SharedResources", "BaseThemes")
        base_theme = {"name": BASE_THEME_NAME, "dataColors": [
            "#118DFF", "#12239E", "#E66C37", "#6B007B", "#E044A7",
            "#744EC2", "#D9B300", "#D64550"
        ]}
        ruta_bt = os.path.join(bt_dir, f"{BASE_THEME_NAME}.json")
        escribir_json(ruta_bt, base_theme)
        archivos.append(ruta_bt)
        report_json["themeCollection"] = {
            "baseTheme": {
                "name": BASE_THEME_NAME,
                "reportVersionAtImport": THEME_REPORT_VERSIONS,
                "type": "SharedResources",
            }
        }
        report_json["resourcePackages"] = [
            {
                "name": "SharedResources",
                "type": "SharedResources",
                "items": [
                    {"name": BASE_THEME_NAME, "path": f"BaseThemes/{BASE_THEME_NAME}.json", "type": "BaseTheme"}
                ],
            }
        ]

    report_json["settings"] = {
        "useStylableVisualContainerHeader": True,
        "defaultDrillFilterOtherVisuals": True,
        "useEnhancedTooltips": True,
        # Mismo locale que el modelo (antes estaba fijo en es-PE, un pais
        # concreto incrustado en un framework generico que nadie eligio).
        "locale": cultura,
    }
    r = os.path.join(report_dir, "definition", "report.json")
    escribir_json(r, report_json)
    archivos.append(r)

    # --- páginas y visuales, construidas desde los ARQUETIPOS ---
    #
    # Antes esto eran 3 visuales fijos en una pagina, sin altText y sin ningun
    # slicer. Dos consecuencias: incumplia la regla de accesibilidad de mayor
    # severidad en el 100% de los visuales, y la medida 'Indicador %' (defendida
    # con HASONEVALUE) devolvia BLANK porque no habia forma de elegir un
    # indicador. Ahora las paginas salen de `arquetipos.py`, que declara ranuras
    # con su alt y su orden de lectura.
    pages_dir = os.path.join(report_dir, "definition", "pages")
    nombre_ppal, _fmt = medida_principal(dom)
    otros = [n for _i, n, _a, _b in dom["indicadores"]][1:3]
    ind = TABLA_INDICADOR

    paginas = []
    for clave in ("resumen", "detalle"):
        arq = arquetipos.arquetipo(clave)
        page_name = nombre_hex()
        visuales = []
        for tab, ranura in enumerate(arq["ranuras"]):
            rol, pregunta, x, y, w, h, alt_tpl = ranura
            pos = (x, y, w, h, tab)
            alt = arquetipos.alt_de(alt_tpl, nombre_ppal, dim1, dim2)
            tipo = arquetipos.visual_para(pregunta)

            if rol == "titulo":
                titulo = (f"{arq['titulo']} — {nombre_ppal}" if clave == "resumen"
                          else f"{arq['titulo']} por {dim2} y mes")
                # El ancho sale del TEXTO, no de un numero fijo: con un titulo
                # largo el cuadro se quedaba corto y Power BI lo recortaba.
                ancho = arquetipos.ancho_titulo(titulo, maximo=w)
                visuales.append(visual_texto((x, y, ancho, h, tab), alt, titulo))
            elif rol == "slicer_indicador":
                # La pieza que faltaba: sin este slicer, 'Indicador %' es BLANK.
                visuales.append(visual(tipo, pos, alt, titulo=ind,
                                       roles={"Values": [campo_columna(ind, ind, True)]}))
            elif rol == "slicer_anio":
                visuales.append(visual(tipo, pos, alt, titulo="Año",
                                       roles={"Values": [campo_columna("Calendario", "Año", True)]}))
            elif rol == "slicer_dim1":
                visuales.append(visual(tipo, pos, alt, titulo=dim1,
                                       roles={"Values": [campo_columna(dim1, dim1, True)]}))
            elif rol.startswith("kpi_"):
                idx = int(rol[-1]) - 1
                medida = nombre_ppal if idx == 0 else (
                    otros[idx - 1] if idx - 1 < len(otros) else nombre_ppal)
                visuales.append(visual(tipo, pos, alt, titulo=medida,
                                       roles={"Data": [campo_medida("_ Medidas", medida)]}))
            elif rol == "tendencia":
                visuales.append(visual(
                    tipo, pos, alt, titulo=f"{nombre_ppal} por mes",
                    roles={"Category": [campo_columna("Calendario", "Mes", True)],
                           "Y": [campo_medida("_ Medidas", nombre_ppal)]}))
            elif rol == "ranking":
                visuales.append(visual(
                    tipo, pos, alt, titulo=f"{nombre_ppal} por {dim2}",
                    roles={"Category": [campo_columna(dim2, dim2, True)],
                           "Y": [campo_medida("_ Medidas", nombre_ppal)]},
                    orden_desc=("_ Medidas", nombre_ppal)))
            elif rol == "detalle":
                visuales.append(visual(
                    tipo, pos, alt, titulo=f"{nombre_ppal} por {dim1}",
                    roles={"Values": [campo_columna(dim1, dim1, True),
                                      campo_medida("_ Medidas", nombre_ppal)]}))
            elif rol == "matriz":
                visuales.append(visual(
                    tipo, pos, alt, titulo=f"{nombre_ppal}: {dim2} por mes",
                    roles={"Rows": [campo_columna(dim2, dim2, True)],
                           "Columns": [campo_columna("Calendario", "Mes", True)],
                           "Values": [campo_medida("_ Medidas", nombre_ppal)]}))
            elif rol == "comparacion":
                visuales.append(visual(
                    tipo, pos, alt, titulo=f"{nombre_ppal} por {dim1} y año",
                    roles={"Category": [campo_columna(dim1, dim1, True)],
                           "Series": [campo_columna("Calendario", "Año")],
                           "Y": [campo_medida("_ Medidas", nombre_ppal)]}))

        page = {
            "$schema": SCHEMA_PAGE,
            "name": page_name,
            "displayName": arq["titulo"],
            "displayOption": "FitToPage",
            "height": arquetipos.CANVAS["height"],
            "width": arquetipos.CANVAS["width"],
        }
        r = os.path.join(pages_dir, page_name, "page.json")
        escribir_json(r, page)
        archivos.append(r)
        for vname, vobj in visuales:
            r = os.path.join(pages_dir, page_name, "visuals", vname, "visual.json")
            escribir_json(r, vobj)
            archivos.append(r)
        paginas.append(page_name)

    r = os.path.join(pages_dir, "pages.json")
    escribir_json(r, {
        "$schema": SCHEMA_PAGES,
        "pageOrder": paginas,
        "activePageName": paginas[0],
    })
    archivos.append(r)

    return base, archivos


def main():
    ap = argparse.ArgumentParser(
        description="Genera un proyecto Power BI PBIP mínimo y válido (modelo estrella + PBIR)."
    )
    ap.add_argument("--nombre", required=True, help="Nombre del reporte (requerido).")
    ap.add_argument("--dominio", default="generico", choices=sorted(DOMINIOS),
                    help="Dominio del modelo de ejemplo (default: generico).")
    ap.add_argument("--salida", default="./", help="Carpeta destino (default: actual).")
    ap.add_argument("--tema", help="Ruta a theme.json (opcional, tema custom de marca).")
    ap.add_argument("--datos", help=(
        "Carpeta con los CSV (la que genera generar_datos_ejemplo.py). Si se pasa, "
        "las particiones del modelo LEEN esos CSV via el parametro RutaBase, asi el "
        ".pbip muestra los datos reales al abrirlo. Sin este argumento el modelo "
        "trae datos inline de muestra."))
    ap.add_argument("--cultura", default="es-ES", help=(
        "culture / sourceQueryCulture del modelo (default: es-ES)."))
    ap.add_argument("--en-raiz", dest="en_raiz", action="store_true", help=(
        "Deja el .pbip directamente en --salida en vez de crear una subcarpeta "
        "<nombre>/. Es lo que espera Fabric Git Integration."))
    ap.add_argument("--ruta-base", dest="ruta_base", help=(
        "Valor literal del parametro RutaBase (default: la ruta absoluta de "
        "--datos). Usa un placeholder si el proyecto se va a versionar en "
        "publico: una ruta con tu nombre de usuario en un archivo commiteado "
        "es fuga de datos."))
    args = ap.parse_args()
    validar_nombre(args.nombre)

    if args.datos and not os.path.isdir(args.datos):
        ap.error(f"--datos no es una carpeta: {args.datos}")

    base, archivos = generar(args.nombre, args.salida, args.tema, args.dominio,
                             datos=args.datos, cultura=args.cultura,
                             base_en_salida=args.en_raiz,
                             ruta_base=args.ruta_base)

    # Validación final: cada .json generado debe reparsear
    errores = 0
    for ruta in archivos:
        if ruta.endswith((".json", ".pbip", ".pbir", ".pbism", ".platform")):
            try:
                with open(ruta_io(ruta), "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                print(f"  JSON INVÁLIDO: {ruta}  ->  {e}")
                errores += 1

    print(f"Proyecto generado en: {base}  (dominio: {args.dominio})")
    print(f"Archivos JSON validados: {len(archivos)} ({errores} con error)")
    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
