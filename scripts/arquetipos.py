#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arquetipos.py — Conocimiento de diseño de reportes, como DATOS.

Por que existe
--------------
El scaffold entregaba 1 pagina con 3 visuales. La brecha hasta un reporte util no
era de codigo: **no existia el conocimiento de diseño** que el generador tenia que
materializar. Este modulo lo pone en forma de datos, para que el generador
construya paginas completas en vez de un esqueleto.

Que es citable y que no
-----------------------
El COOKBOOK (que visual responde cada pregunta) esta sustentado: cada entrada
lleva su regla y su fuente de Microsoft Learn. Los ARQUETIPOS de negocio **no**:
Microsoft no define arquetipos de pagina con nombre — se comprobo recorriendo el
indice de `guidance/`, las 11 unidades del Training y `service-dashboards-design-tips`.
Los marcados `heuristico=True` son composicion nuestra sobre principios citados
(colocacion, balance, proximidad, contraste, repeticion, espacio, alineacion).
Los tres canonicos (tooltip, drillthrough, movil) SI tienen parametros oficiales.

Accesibilidad no es opcional aqui
---------------------------------
Cada ranura de arquetipo declara su `alt` (texto alternativo). La regla
`PBI-A11Y-01` es la de mayor severidad del catalogo y el generador la incumplia
en el 100% de los visuales. El alt describe el **insight**, no el aspecto: el
lector de pantalla ya anuncia titulo y tipo de visual.
Fuente: learn.microsoft.com/power-bi/create-reports/desktop-accessibility-creating-reports

Solo libreria estandar; datos y funciones puras.
"""

# --------------------------------------------------------------------------- #
# Lienzo y bandas
#
# 16:9 y los dos tamaños concretos SI son oficiales (report display settings).
# El reparto en bandas es NUESTRO: es una composicion razonable, no una norma.
# --------------------------------------------------------------------------- #
CANVAS = {"width": 1280, "height": 720}          # oficial: 16:9, 1280x720
GAP = 16                                          # [HEURISTICO]
MARGEN = 32                                       # [HEURISTICO]

# Pagina tooltip: 320x240 SI es oficial y obligatorio.
# learn.microsoft.com/power-bi/guidance/report-page-tooltips
TOOLTIP = {"width": 320, "height": 240}

FUENTE_A11Y = ("https://learn.microsoft.com/en-us/power-bi/create-reports/"
               "desktop-accessibility-creating-reports")
FUENTE_VISUALES = ("https://learn.microsoft.com/en-us/power-bi/visuals/"
                   "power-bi-visualization-types-for-reports-and-q-and-a")
FUENTE_OPTIM = ("https://learn.microsoft.com/en-us/power-bi/guidance/"
                "power-bi-optimization")
FUENTE_TOOLTIP = ("https://learn.microsoft.com/en-us/power-bi/guidance/"
                  "report-page-tooltips")


# --------------------------------------------------------------------------- #
# COOKBOOK — pregunta analitica -> visual, con su regla y fuente
#
# Es la parte SUSTENTADA de este modulo. `regla` es la razon por la que ese
# visual responde esa pregunta; sirve para explicarselo al usuario sin inventar.
# --------------------------------------------------------------------------- #
COOKBOOK = {
    "comparar_categorias_nombre_largo": {
        "visual": "clusteredBarChart",
        "regla": "Barras cuando los nombres de categoria son largos; comparar "
                 "valores entre categorias es su punto fuerte.",
        "fuente": FUENTE_VISUALES,
    },
    "comparar_periodos": {
        "visual": "clusteredColumnChart",
        "regla": "Columnas para comparaciones temporales discretas.",
        "fuente": FUENTE_VISUALES,
    },
    "evolucion_en_el_tiempo": {
        "visual": "lineChart",
        "regla": "Linea enfatiza la forma de la serie en el tiempo y necesita eje "
                 "X continuo. Con periodos sin dato la linea INVENTA tendencia: "
                 "en ese caso, columnas.",
        "fuente": FUENTE_VISUALES,
    },
    "un_numero_que_importa": {
        "visual": "cardVisual",
        "regla": "Tarjeta cuando un solo numero es lo mas importante a seguir. "
                 "Hay que darle contexto: un numero solo no dice si es bueno.",
        "fuente": FUENTE_VISUALES,
    },
    "cruce_de_dimensiones_con_drill": {
        "visual": "pivotTable",
        "regla": "Matriz para cruzar dos o mas dimensiones; soporta layout "
                 "escalonado y drill por jerarquias.",
        "fuente": FUENTE_VISUALES,
    },
    "valores_exactos": {
        "visual": "tableEx",
        "regla": "Tabla cuando hacen falta valores exactos y comparar muchas "
                 "medidas de una sola categoria. Aplica Top N o el filtro mas "
                 "restrictivo que permita la pregunta.",
        "fuente": FUENTE_OPTIM,
    },
    "filtrar_en_canvas": {
        "visual": "slicer",
        "regla": "Slicer para los filtros de uso frecuente, con el estado visible "
                 "de un vistazo y en la MISMA posicion en todas las paginas.",
        "fuente": FUENTE_VISUALES,
    },
    "titulo_o_mensaje": {
        "visual": "textbox",
        "regla": "Cuadro de texto para el mensaje de la pagina. El titulo dice la "
                 "conclusion, no el tema.",
        "fuente": FUENTE_VISUALES,
    },
}


def visual_para(pregunta):
    """visualType recomendado para una pregunta del cookbook."""
    return COOKBOOK[pregunta]["visual"]


# --------------------------------------------------------------------------- #
# ARQUETIPOS
#
# Cada ranura: (rol, pregunta_del_cookbook, x, y, w, h, alt)
#   rol   : para que sirve la ranura; el generador decide que campo/medida poner.
#   alt   : plantilla del texto alternativo. `{ind}` = nombre del indicador
#           principal, `{d1}`/`{d2}` = nombres de las dimensiones.
# El ORDEN de la lista es el orden de tabulacion (tabOrder), que debe seguir el
# orden de lectura — WCAG 2.4.3.
# --------------------------------------------------------------------------- #

_ANCHO_UTIL = CANVAS["width"] - 2 * MARGEN            # 1216
_COL = (_ANCHO_UTIL - 2 * GAP) // 3                   # 3 columnas de tarjetas

ARQUETIPOS = {
    "resumen": {
        "titulo": "Resumen",
        "heuristico": True,
        "para": "Quien decide y no explora: el estado actual y su porque.",
        "base_citada": "Lo mas importante arriba-izquierda (LTR); slicers en la "
                       "misma posicion en todas las paginas; un mensaje por pagina.",
        "ranuras": [
            ("titulo", "titulo_o_mensaje", MARGEN, 24, 700, 40,
             "Titulo del reporte: {ind} y su desglose."),
            ("slicer_indicador", "filtrar_en_canvas", 780, 24, 210, 56,
             "Segmentador para elegir el indicador que se analiza. "
             "Al elegir uno, el resto de la pagina se recalcula para ese indicador."),
            ("slicer_anio", "filtrar_en_canvas", 1006, 24, 210, 56,
             "Segmentador de año."),
            ("kpi_1", "un_numero_que_importa", MARGEN, 100, _COL, 130,
             "{ind} del periodo seleccionado, en total."),
            ("kpi_2", "un_numero_que_importa", MARGEN + _COL + GAP, 100, _COL, 130,
             "Segundo indicador del periodo seleccionado."),
            ("kpi_3", "un_numero_que_importa", MARGEN + 2 * (_COL + GAP), 100, _COL, 130,
             "Tercer indicador del periodo seleccionado."),
            ("tendencia", "evolucion_en_el_tiempo", MARGEN, 250, 760, 300,
             "Evolucion mensual de {ind}. Permite ver la tendencia y los meses "
             "que se desvian del resto."),
            ("ranking", "comparar_categorias_nombre_largo",
             MARGEN + 760 + GAP, 250, _ANCHO_UTIL - 760 - GAP, 300,
             "{ind} por {d2}, ordenado de mayor a menor. Identifica cual "
             "concentra el resultado y cual queda rezagado."),
            ("detalle", "valores_exactos", MARGEN, 570, _ANCHO_UTIL, 120,
             "Tabla con los valores exactos de {ind} por {d1}, para leer cifras "
             "concretas y exportarlas."),
        ],
    },
    "detalle": {
        "titulo": "Detalle",
        "heuristico": True,
        "para": "Quien viene a investigar: densidad alta aceptable.",
        "base_citada": "Slicers en la misma posicion que en la pagina anterior; "
                       "Top N o el filtro mas restrictivo en tablas y matrices.",
        "ranuras": [
            ("titulo", "titulo_o_mensaje", MARGEN, 24, 700, 40,
             "Titulo de la pagina de detalle."),
            ("slicer_indicador", "filtrar_en_canvas", 780, 24, 210, 56,
             "Segmentador de indicador, en la misma posicion que en Resumen."),
            ("slicer_dim1", "filtrar_en_canvas", 1006, 24, 210, 56,
             "Segmentador de {d1}."),
            ("matriz", "cruce_de_dimensiones_con_drill", MARGEN, 100, _ANCHO_UTIL, 380,
             "Matriz de {ind} cruzando {d2} contra los meses. Permite localizar "
             "la combinacion concreta que explica el resultado."),
            ("comparacion", "comparar_periodos", MARGEN, 500, _ANCHO_UTIL, 190,
             "{ind} por {d1} y año, para comparar un periodo contra el anterior."),
        ],
    },
}


def arquetipo(nombre):
    return ARQUETIPOS[nombre]


def alt_de(plantilla, ind, d1, d2):
    """
    Resuelve la plantilla de texto alternativo y respeta el limite duro de 250
    caracteres que documenta Microsoft para el campo alt text.
    """
    t = plantilla.format(ind=ind, d1=d1, d2=d2)
    return t if len(t) <= 250 else t[:247].rstrip() + "..."
