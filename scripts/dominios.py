#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dominios.py — Catalogo UNICO de dominios de ejemplo (fuente de verdad).

Por que existe este archivo
---------------------------
Antes, `generar_datos_ejemplo.py` y `scaffold_pbip.py` tenian cada uno su
propio diccionario DOMINIOS. Divergieron en TODOS los dominios (p. ej. ventas
tenia 6 productos en los CSV y 4 en el modelo TMDL), asi que los datos de
ejemplo y el .pbip describian modelos distintos. Un solo catalogo compartido
hace imposible esa divergencia.

Estructura por dominio
----------------------
  desc         : descripcion corta del dominio
  dim1         : (tabla, [(id, nombre)])
  dim2         : (tabla, columna_grupo, [(id, nombre, grupo)])
  hecho        : nombre de la tabla de hechos
  indicadores  : [(id, nombre, (num_lo, num_hi), (den_lo, den_hi))]
  pct          : set de ids de indicador que son porcentajes (num <= den)

El hecho es "alto" (tall): una fila por Fecha x dim1 x dim2 x indicador, con
el patron Num/Den. Ese diseno EXIGE una dimension Indicador; sin ella las
medidas suman atravesando indicadores y mezclan porcentajes con importes
absolutos (p. ej. % Margen + Ticket Promedio -> 5226%). La dimension se
deriva de `indicadores` con `filas_indicador()`.

Fundamento del modelo: esquema estrella (Kimball); nombres de negocio con
espacios, sin prefijos DIM_/FACT_ (Microsoft / SQLBI / Tabular Editor BPA).

Solo libreria estandar. Este modulo no tiene efectos secundarios: solo datos
y funciones puras, para que cualquier script lo importe sin coste.
"""

# --------------------------------------------------------------------------- #
# Catalogo de dominios
# --------------------------------------------------------------------------- #

DOMINIOS = {
    "generico": {
        "desc": "Modelo neutro (Categoria / Segmento / Hechos) para cualquier area.",
        "dim1": ("Categoria", [
            (1, "Categoria A"), (2, "Categoria B"), (3, "Categoria C"),
        ]),
        "dim2": ("Segmento", "Grupo", [
            (1, "Segmento 1", "Grupo X"), (2, "Segmento 2", "Grupo X"),
            (3, "Segmento 3", "Grupo Y"), (4, "Segmento 4", "Grupo Y"),
        ]),
        "hecho": "Hechos",
        "indicadores": [
            (1, "% Cumplimiento", (60, 100), (90, 110)),
            (2, "Volumen",        (500, 2000), (10, 40)),
            (3, "% Eficiencia",   (30, 90), (95, 105)),
        ],
        "pct": {1, 3},
    },
    "ventas": {
        "desc": "Comercial (Region / Producto / Ventas).",
        "dim1": ("Region", [
            (1, "Norte"), (2, "Centro"), (3, "Sur"), (4, "Oriente"),
        ]),
        "dim2": ("Producto", "Categoria Producto", [
            (1, "Laptop", "Computo"), (2, "Monitor", "Computo"),
            (3, "Audifonos", "Accesorios"), (4, "Teclado", "Accesorios"),
            (5, "Impresora", "Oficina"), (6, "Tablet", "Computo"),
        ]),
        "hecho": "Ventas",
        "indicadores": [
            (1, "% Margen",            (20, 45), (95, 105)),
            (2, "% Cumplimiento Meta", (70, 110), (95, 105)),
            (3, "Ticket Promedio",     (8000, 30000), (80, 260)),
        ],
        "pct": {1, 2},
    },
    "rrhh": {
        "desc": "Recursos Humanos (Departamento / Categoria / Personal).",
        "dim1": ("Departamento", [
            (1, "Tecnologia"), (2, "Comercial"), (3, "Operaciones"),
            (4, "Finanzas"), (5, "Recursos Humanos"),
        ]),
        "dim2": ("Categoria", "Nivel", [
            (1, "Analista", "Profesional"), (2, "Especialista", "Profesional"),
            (3, "Jefe", "Mando"), (4, "Gerente", "Mando"),
            (5, "Asistente", "Soporte"),
        ]),
        "hecho": "Personal",
        "indicadores": [
            (1, "% Rotacion",           (2, 15), (95, 115)),
            (2, "% Ausentismo",         (1, 8), (95, 110)),
            (3, "% Cobertura Vacantes", (60, 100), (80, 105)),
        ],
        "pct": {1, 2, 3},
    },
    "finanzas": {
        "desc": "Finanzas (Centro de Costo / Cuenta / Movimientos).",
        "dim1": ("Centro de Costo", [
            (1, "CC Comercial"), (2, "CC Operaciones"),
            (3, "CC Administracion"), (4, "CC Tecnologia"),
        ]),
        "dim2": ("Cuenta", "Tipo Cuenta", [
            (1, "Ingresos", "Resultado"), (2, "Gastos Operativos", "Resultado"),
            (3, "CAPEX", "Inversion"), (4, "Provisiones", "Resultado"),
        ]),
        "hecho": "Movimientos",
        "indicadores": [
            (1, "% Ejecucion Presupuesto", (70, 110), (95, 105)),
            (2, "% Margen Operativo",      (5, 35), (95, 105)),
            (3, "Costo por Unidad",        (1000, 9000), (50, 300)),
        ],
        "pct": {1, 2},
    },
    "salud": {
        "desc": "Salud / operaciones clinicas (Sede / Servicio / Indicadores).",
        "dim1": ("Sede", [
            (1, "Sede Norte"), (2, "Sede Centro"), (3, "Sede Sur"), (4, "Sede Este"),
        ]),
        "dim2": ("Servicio", "Servicio Agrupado", [
            (1, "Emergencia", "Atencion Critica"),
            (2, "Hospitalizacion", "Atencion Critica"),
            (3, "Consulta Externa", "Ambulatorio"),
            (4, "Quirofano", "Atencion Critica"),
            (5, "Hemodialisis", "Ambulatorio"),
            (6, "Farmacia", "Soporte"),
            (7, "Laboratorio", "Soporte"),
            (8, "Imagenes", "Soporte"),
        ]),
        "hecho": "Indicadores",
        "indicadores": [
            (1, "% Ocupacion",          (18, 30), (25, 32)),
            (2, "% Entregas a tiempo",  (80, 100), (90, 110)),
            (3, "Tiempo de Estancia",   (120, 360), (40, 90)),
            (4, "% Cumplimiento Citas", (60, 95), (75, 100)),
            (5, "Reingresos 30 dias",   (1, 12), (40, 120)),
        ],
        "pct": {1, 2, 4},
    },
}

# Meses en espanol (indice 1..12). Se usa tanto al generar el CSV de calendario
# como al construir el calendario inline en TMDL, para que coincidan.
MESES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

# Nombre de la dimension de indicadores. El hecho es alto, asi que esta tabla
# no es opcional: es la que evita sumar indicadores incompatibles.
TABLA_INDICADOR = "Indicador"


# --------------------------------------------------------------------------- #
# Derivaciones del catalogo (puras)
# --------------------------------------------------------------------------- #

def nombres(dom):
    """Devuelve (dim1, dim2, col_grupo, hecho) del dominio."""
    return dom["dim1"][0], dom["dim2"][0], dom["dim2"][1], dom["hecho"]


def filas_indicador(dom):
    """
    Filas de la dimension Indicador, derivadas de `indicadores` + `pct`.

    Columnas: ID Indicador, Indicador, Tipo, Formato
      - Tipo    : 'Porcentaje' | 'Absoluto'  (corta y explica la mezcla)
      - Formato : formatString DAX sugerido para ese indicador

    Existir esta tabla es lo que permite que una medida se evalue para UN
    indicador a la vez en vez de sumar todo el hecho.
    """
    filas = []
    for ind_id, nombre, _num, _den in dom["indicadores"]:
        es_pct = ind_id in dom["pct"]
        filas.append([
            ind_id,
            nombre,
            "Porcentaje" if es_pct else "Absoluto",
            "0.0%;-0.0%;0.0%" if es_pct else "#,0",
        ])
    return filas


def esquema_csv(dom):
    """
    Esquema de cada CSV del dominio: {tabla: [(columna, tipo_M), ...]}.

    Fuente unica para el codigo M y para las columnas del TMDL, de modo que
    los tipos declarados en el modelo coincidan con lo que lee Power Query.
    """
    dim1, dim2, col_grupo, hecho = nombres(dom)
    return {
        # "Año" con tilde: es la convencion de nombres de negocio del framework
        # y el TMDL del scaffold declara esa misma columna. Los CSV se escriben
        # en UTF-8 con BOM, asi que Excel y Power BI la leen sin problema.
        "Calendario": [
            ("Fecha", "type date"), ("Año", "Int64.Type"), ("Mes", "type text"),
            ("NumMes", "Int64.Type"), ("Trimestre", "type text"),
            ("EsDiaHabil", "type text"),
        ],
        dim1: [("ID " + dim1, "Int64.Type"), (dim1, "type text")],
        dim2: [("ID " + dim2, "Int64.Type"), (dim2, "type text"),
               (col_grupo, "type text")],
        TABLA_INDICADOR: [
            ("ID " + TABLA_INDICADOR, "Int64.Type"),
            (TABLA_INDICADOR, "type text"),
            ("Tipo", "type text"), ("Formato", "type text"),
        ],
        hecho: [
            ("Fecha", "type date"), ("ID " + dim1, "Int64.Type"),
            ("ID " + dim2, "Int64.Type"), ("ID " + TABLA_INDICADOR, "Int64.Type"),
            ("Num", "Int64.Type"), ("Den", "Int64.Type"),
        ],
    }


def orden_tablas(dom):
    """
    Orden de carga/declaracion de las tablas: dimensiones antes del hecho,
    medidas al final. Se usa para PBI_QueryOrder y para los `ref table`.
    """
    dim1, dim2, _col, hecho = nombres(dom)
    return ["Calendario", dim1, dim2, TABLA_INDICADOR, hecho, "_ Medidas"]
