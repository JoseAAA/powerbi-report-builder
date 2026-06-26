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
  <Hecho>      hecho: Fecha, claves a las dimensiones, Num, Den (claves ocultas).
  _ Medidas    tabla de medidas oculta con 3 medidas DAX (Numerador, Denominador,
               'Indicador %') usando VAR/RETURN y DIVIDE.

Todas las particiones son M en modo import y construyen los datos inline con
#table(...), así el modelo carga sin ninguna fuente externa.

Solo usa la librería estándar de Python (json, os, uuid, argparse, shutil,
secrets).
"""
import argparse
import json
import os
import re
import secrets
import shutil
import uuid

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
# Catalogo de dominios (compacto: nombres + filas de muestra para el #table).
# Estructura por dominio:
#   dim1  : (tabla, [(id, nombre)])
#   dim2  : (tabla, columna_grupo, [(id, nombre, grupo)])
#   hecho : nombre de la tabla de hechos
# La estructura del modelo es identica; solo cambian nombres y datos de muestra.
# ---------------------------------------------------------------------------
DOMINIOS = {
    "generico": {
        "dim1": ("Categoria", [(1, "Categoria A"), (2, "Categoria B"), (3, "Categoria C")]),
        "dim2": ("Segmento", "Grupo", [
            (1, "Segmento 1", "Grupo X"), (2, "Segmento 2", "Grupo X"),
            (3, "Segmento 3", "Grupo Y"), (4, "Segmento 4", "Grupo Y")]),
        "hecho": "Hechos",
    },
    "ventas": {
        "dim1": ("Region", [(1, "Norte"), (2, "Centro"), (3, "Sur"), (4, "Oriente")]),
        "dim2": ("Producto", "Categoria Producto", [
            (1, "Laptop", "Computo"), (2, "Monitor", "Computo"),
            (3, "Audifonos", "Accesorios"), (4, "Teclado", "Accesorios")]),
        "hecho": "Ventas",
    },
    "rrhh": {
        "dim1": ("Departamento", [(1, "Tecnologia"), (2, "Comercial"), (3, "Operaciones"), (4, "Finanzas")]),
        "dim2": ("Categoria", "Nivel", [
            (1, "Analista", "Profesional"), (2, "Especialista", "Profesional"),
            (3, "Jefe", "Mando"), (4, "Gerente", "Mando")]),
        "hecho": "Personal",
    },
    "finanzas": {
        "dim1": ("Centro de Costo", [(1, "CC Comercial"), (2, "CC Operaciones"), (3, "CC Administracion")]),
        "dim2": ("Cuenta", "Tipo Cuenta", [
            (1, "Ingresos", "Resultado"), (2, "Gastos Operativos", "Resultado"),
            (3, "CAPEX", "Inversion"), (4, "Provisiones", "Resultado")]),
        "hecho": "Movimientos",
    },
    "salud": {
        "dim1": ("Sede", [(1, "Sede Norte"), (2, "Sede Centro"), (3, "Sede Sur")]),
        "dim2": ("Servicio", "Servicio Agrupado", [
            (1, "Emergencia", "Atencion Critica"), (2, "Hospitalizacion", "Atencion Critica"),
            (3, "Consulta Externa", "Ambulatorio"), (4, "Quirofano", "Atencion Critica")]),
        "hecho": "Indicadores",
    },
}


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


def escribir_json(ruta, obj):
    """Escribe un dict como JSON indentado y valida que reparsee."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    texto = json.dumps(obj, ensure_ascii=False, indent=2)
    json.loads(texto)  # validación temprana
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


def escribir_texto(ruta, texto):
    """Escribe texto plano (TMDL) en UTF-8."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


# ---------------------------------------------------------------------------
# TMDL — tablas del modelo estrella (parametricas por dominio)
# Indentación con TAB, una línea en blanco entre objetos hermanos.
# ---------------------------------------------------------------------------
def tmdl_calendario():
    """Tabla Calendario marcada como tabla de fecha (dataCategory=Time).
    Datos inline con #table(...) para 2 años; sin fuente externa.
    """
    lt_tabla = nuevo_guid()
    lt_fecha = nuevo_guid()
    lt_anio = nuevo_guid()
    lt_mes = nuevo_guid()
    lt_nummes = nuevo_guid()
    lt_trim = nuevo_guid()
    return f"""table Calendario
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

\tpartition Calendario = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Fechas = List.Dates(#date(2024, 1, 1), 731, #duration(1, 0, 0, 0)),
\t\t\t\t    Tabla = Table.FromList(Fechas, Splitter.SplitByNothing(), {{"Fecha"}}),
\t\t\t\t    Tipo = Table.TransformColumnTypes(Tabla, {{{{"Fecha", type date}}}}),
\t\t\t\t    Anio = Table.AddColumn(Tipo, "Año", each Date.Year([Fecha]), Int64.Type),
\t\t\t\t    NumMes = Table.AddColumn(Anio, "NumMes", each Date.Month([Fecha]), Int64.Type),
\t\t\t\t    Mes = Table.AddColumn(NumMes, "Mes", each Date.ToText([Fecha], "MMM", "es-ES"), type text),
\t\t\t\t    Trim = Table.AddColumn(Mes, "Trimestre", each "T" & Text.From(Date.QuarterOfYear([Fecha])), type text)
\t\t\t\tin
\t\t\t\t    Trim

\tannotation PBI_ResultType = Table
"""


def tmdl_dim1(dom):
    """Dimensión 1: columnas 'ID <dim1>' (clave) y <dim1>."""
    dim1, filas_dom = dom["dim1"]
    id1 = "ID " + dim1
    lt_tabla, lt_id, lt_nombre = nuevo_guid(), nuevo_guid(), nuevo_guid()
    filas = ",\n".join(
        '\t\t\t\t            {%d, "%s"}' % (i, n) for i, n in filas_dom)
    tipo = "{} = Int64.Type, {} = text".format(mq(id1), mq(dim1))
    return f"""table {tq(dim1)}
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

\tpartition {tq(dim1)} = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Origen = #table(
\t\t\t\t        type table [{tipo}],
\t\t\t\t        {{
{filas}
\t\t\t\t        }}
\t\t\t\t    )
\t\t\t\tin
\t\t\t\t    Origen

\tannotation PBI_ResultType = Table
"""


def tmdl_dim2(dom):
    """Dimensión 2: 'ID <dim2>' (clave), <dim2> y la columna de agrupación."""
    dim2, col_grupo, filas_dom = dom["dim2"]
    id2 = "ID " + dim2
    lt_tabla, lt_id, lt_nombre, lt_grupo = (nuevo_guid(), nuevo_guid(),
                                            nuevo_guid(), nuevo_guid())
    filas = ",\n".join(
        '\t\t\t\t            {%d, "%s", "%s"}' % (i, n, g) for i, n, g in filas_dom)
    tipo = "{} = Int64.Type, {} = text, {} = text".format(
        mq(id2), mq(dim2), mq(col_grupo))
    return f"""table {tq(dim2)}
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

\tpartition {tq(dim2)} = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Origen = #table(
\t\t\t\t        type table [{tipo}],
\t\t\t\t        {{
{filas}
\t\t\t\t        }}
\t\t\t\t    )
\t\t\t\tin
\t\t\t\t    Origen

\tannotation PBI_ResultType = Table
"""


def _filas_hecho(dom):
    """Filas de muestra del hecho: (fecha M, id_dim1, id_dim2, Num, Den)."""
    d1_ids = [r[0] for r in dom["dim1"][1]]
    d2_ids = [r[0] for r in dom["dim2"][2]]
    fechas = ["#date(2024, 1, 15)", "#date(2024, 2, 15)", "#date(2024, 3, 15)",
              "#date(2025, 1, 15)", "#date(2025, 2, 15)", "#date(2025, 3, 15)"]
    nums = [82, 45, 70, 90, 48, 40]
    dens = [100, 60, 90, 100, 60, 50]
    filas = []
    for i, fecha in enumerate(fechas):
        d1 = d1_ids[i % len(d1_ids)]
        d2 = d2_ids[i % len(d2_ids)]
        filas.append("\t\t\t\t            {%s, %d, %d, %d, %d}"
                     % (fecha, d1, d2, nums[i], dens[i]))
    return ",\n".join(filas)


def tmdl_hecho(dom):
    """Tabla de hechos. Claves 'ID <dim1>' e 'ID <dim2>' ocultas; Num/Den ocultas."""
    dim1 = dom["dim1"][0]
    dim2 = dom["dim2"][0]
    hecho = dom["hecho"]
    id1, id2 = "ID " + dim1, "ID " + dim2
    lt_tabla, lt_fecha, lt_d1, lt_d2, lt_num, lt_den = (
        nuevo_guid(), nuevo_guid(), nuevo_guid(), nuevo_guid(),
        nuevo_guid(), nuevo_guid())
    filas = _filas_hecho(dom)
    tipo = "Fecha = date, {} = Int64.Type, {} = Int64.Type, Num = Int64.Type, Den = Int64.Type".format(
        mq(id1), mq(id2))
    return f"""table {tq(hecho)}
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

\tpartition {tq(hecho)} = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Origen = #table(
\t\t\t\t        type table [{tipo}],
\t\t\t\t        {{
{filas}
\t\t\t\t        }}
\t\t\t\t    )
\t\t\t\tin
\t\t\t\t    Origen

\tannotation PBI_ResultType = Table
"""


def tmdl_medidas(dom):
    """Tabla de medidas oculta '_ Medidas' con 3 medidas DAX de ejemplo, que
    referencian el hecho del dominio. Tabla calculada de una columna en blanco.
    """
    hecho = dom["hecho"]
    lt_tabla, lt_col = nuevo_guid(), nuevo_guid()
    lt_num, lt_den, lt_ind = nuevo_guid(), nuevo_guid(), nuevo_guid()
    return f"""table '_ Medidas'
\tisHidden
\tlineageTag: {lt_tabla}

\tmeasure Numerador = ```
\t\t\tVAR Resultado = SUM ( {tq(hecho)}[Num] )
\t\t\tRETURN
\t\t\t    Resultado
\t\t\t```
\t\tformatString: #,0
\t\tdisplayFolder: Indicadores
\t\tlineageTag: {lt_num}

\tmeasure Denominador = ```
\t\t\tVAR Resultado = SUM ( {tq(hecho)}[Den] )
\t\t\tRETURN
\t\t\t    Resultado
\t\t\t```
\t\tformatString: #,0
\t\tdisplayFolder: Indicadores
\t\tlineageTag: {lt_den}

\tmeasure 'Indicador %' = ```
\t\t\tVAR Num = [Numerador]
\t\t\tVAR Den = [Denominador]
\t\t\tRETURN
\t\t\t    DIVIDE ( Num, Den )
\t\t\t```
\t\tformatString: 0.0%;-0.0%;0.0%
\t\tdisplayFolder: Indicadores
\t\tlineageTag: {lt_ind}

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


def tmdl_model(nombre_modelo, tablas_orden):
    """model.tmdl. Desactiva Auto date/time (__PBI_TimeIntelligenceEnabled = 0)
    para NO generar LocalDateTable.
    """
    refs = "\n".join(f"ref table {tq(t)}" for t in tablas_orden)
    orden_json = json.dumps(tablas_orden, ensure_ascii=False)
    return f"""model Model
\tculture: es-ES
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: es-PE
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
def generar(nombre, salida, tema, dominio):
    dom = DOMINIOS[dominio]
    dim1 = dom["dim1"][0]
    dim2 = dom["dim2"][0]
    hecho = dom["hecho"]

    base = os.path.join(salida, nombre)
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
    tablas = ["Calendario", dim1, dim2, hecho, "_ Medidas"]
    escribir_texto(
        os.path.join(sm_dir, "definition", "model.tmdl"),
        tmdl_model(nombre, tablas),
    )

    # tablas (nombre de archivo = nombre de tabla)
    tdir = os.path.join(sm_dir, "definition", "tables")
    escribir_texto(os.path.join(tdir, "Calendario.tmdl"), tmdl_calendario())
    escribir_texto(os.path.join(tdir, f"{dim1}.tmdl"), tmdl_dim1(dom))
    escribir_texto(os.path.join(tdir, f"{dim2}.tmdl"), tmdl_dim2(dom))
    escribir_texto(os.path.join(tdir, f"{hecho}.tmdl"), tmdl_hecho(dom))
    escribir_texto(os.path.join(tdir, "_ Medidas.tmdl"), tmdl_medidas(dom))

    # relationships.tmdl — dimensión->hecho (1->*)
    rels = [
        (hecho, "Fecha", "Calendario", "Fecha"),
        (hecho, "ID " + dim1, dim1, "ID " + dim1),
        (hecho, "ID " + dim2, dim2, "ID " + dim2),
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
        tema_name = tema_obj.get("name") or "TemaCustom"
        tema_filename = "theme_custom.json"
        rr_dir = os.path.join(report_dir, "StaticResources", "RegisteredResources")
        ruta_tema = os.path.join(rr_dir, tema_filename)
        escribir_json(ruta_tema, tema_obj)
        archivos.append(ruta_tema)
        # ThemeMetadata REQUIERE name + reportVersionAtImport + type (schema oficial
        # report/3.x). Omitir reportVersionAtImport corrompe el report.json al abrir.
        report_json["themeCollection"] = {
            "customTheme": {
                "name": tema_name,
                "reportVersionAtImport": THEME_REPORT_VERSIONS,
                "type": "RegisteredResources",
            }
        }
        report_json["resourcePackages"] = [
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [
                    {"name": tema_name, "path": tema_filename, "type": "CustomTheme"}
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
        "locale": "es-PE",
    }
    r = os.path.join(report_dir, "definition", "report.json")
    escribir_json(r, report_json)
    archivos.append(r)

    # --- página + visuales ---
    page_name = nombre_hex()
    pages_dir = os.path.join(report_dir, "definition", "pages")

    r = os.path.join(pages_dir, "pages.json")
    escribir_json(r, {
        "$schema": SCHEMA_PAGES,
        "pageOrder": [page_name],
        "activePageName": page_name,
    })
    archivos.append(r)

    page = {
        "$schema": SCHEMA_PAGE,
        "name": page_name,
        "displayName": "Resumen",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }
    r = os.path.join(pages_dir, page_name, "page.json")
    escribir_json(r, page)
    archivos.append(r)

    # 3 visuales: título, card 'Indicador %', barras de 'Indicador %' por <dim2>
    visuales = [
        visual_titulo("Resumen de indicadores"),
        visual_card("_ Medidas", "Indicador %"),
        visual_barras(dim2, dim2, "_ Medidas", "Indicador %"),
    ]
    for vname, vobj in visuales:
        r = os.path.join(pages_dir, page_name, "visuals", vname, "visual.json")
        escribir_json(r, vobj)
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
    args = ap.parse_args()
    validar_nombre(args.nombre)

    base, archivos = generar(args.nombre, args.salida, args.tema, args.dominio)

    # Validación final: cada .json generado debe reparsear
    errores = 0
    for ruta in archivos:
        if ruta.endswith((".json", ".pbip", ".pbir", ".pbism", ".platform")):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
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
