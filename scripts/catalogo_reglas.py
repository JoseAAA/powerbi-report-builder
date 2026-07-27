#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
catalogo_reglas.py — Catalogo de reglas del modelo, con FUENTE OBLIGATORIA.

Principio de diseño
-------------------
No escribimos nuestras propias "mejores practicas" cuando Microsoft ya publica
las suyas en formato machine-readable. Este catalogo **consume el BPARules.json
OFICIAL** (`references/bpa/BPARules.json`, copia fijada con su SHA-256 de
`microsoft/Analysis-Services`, rama `master`): 71 reglas con `ID` estable,
`Severity`, `Scope`, `Description` y `Expression`. La cita a la fuente ya viene
dentro de la propia regla en 30 de los 71 casos.

Cada regla implementada aqui declara:
  codigo  : el ID OFICIAL de Microsoft, o un `PBI-*` propio si Microsoft no cubre
            el caso (y entonces con su fuente aparte).
  fuente  : URL. **Campo obligatorio**: `verificar_catalogo()` falla si falta, y
            una regla de severidad ALTA no puede apoyarse solo en un nivel 5 de
            la jerarquia de autoridad (ver `fuentes.py`).

Tres decisiones de criterio, no de codigo
-----------------------------------------
1. **`DATECOLUMN_FORMATSTRING` se EXCLUYE.** La regla oficial exige literalmente
   `formatString == "mm/dd/yyyy"`. Es el formato de EE. UU. y seria incorrecto en
   un reporte es-ES, es-PE o en cualquier locale que no use mes/dia/año. Aplicarla
   a ciegas empeoraria el producto. Queda documentada en EXCLUIDAS con el motivo.
2. **Las reglas oficiales basadas en nombres INGLESES no disparan en español.**
   `MONTH_(AS_A_STRING)_MUST_BE_SORTED` busca "MONTH" en el nombre de la columna,
   asi que nunca ve una columna `Mes`. No es un defecto de Microsoft: su catalogo
   asume modelos en ingles. Se añade el equivalente propio `PBI-NAME-01`.
3. **`PERCENTAGE_FORMATTING` se aplica tal cual.** Exige el formato canonico
   `#,0.0%;-#,0.0%;#,0.0%`. Es una convencion, no una correccion, pero es de
   Microsoft, es severidad 2 y cumplirla es gratis: se alinearon los generadores.

Solo libreria estandar.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuentes import nivel_autoridad  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_BPA = os.path.join(RAIZ, "references", "bpa", "BPARules.json")
RUTA_SHA = os.path.join(RAIZ, "references", "bpa", "BPARules.sha256")

# Severidad oficial (1/2/3) -> nuestra etiqueta y peso a descontar de 100.
SEVERIDAD = {3: ("ALTA", 15), 2: ("MEDIA", 7), 1: ("BAJA", 3)}

# Fuente por defecto para las reglas oficiales que no traen URL en su Description.
# El propio catalogo de Microsoft es la fuente (nivel 2 de autoridad).
FUENTE_BPA = ("https://github.com/microsoft/Analysis-Services/blob/master/"
              "BestPracticeRules/BPARules.json")

# Reglas oficiales EXCLUIDAS a proposito, con el motivo. Que esten aqui y no
# simplemente ausentes es deliberado: la decision queda auditable.
EXCLUIDAS = {
    "DATECOLUMN_FORMATSTRING": (
        "Exige literalmente formatString == 'mm/dd/yyyy', el formato de EE. UU. "
        "En un reporte es-ES/es-PE eso es incorrecto: mostraria 03/07 como 7 de "
        "marzo. Aplicarla empeoraria el producto en vez de mejorarlo."),
    "MONTHCOLUMN_FORMATSTRING": (
        "Exige formatString == 'MMMM yyyy' en columnas DateTime cuyo nombre "
        "contenga 'Month'. Mismo problema de idioma que la anterior, y ademas "
        "solo aplica si el mes es DateTime (en un calendario normal es texto)."),
    "FIX_REFERENTIAL_INTEGRITY_VIOLATIONS": (
        "Requiere contar filas del modelo cargado; no se puede evaluar leyendo "
        "TMDL. `verificar_cableado.py` cubre la integridad de los CSV de ejemplo."),
    "LARGE_TABLES_SHOULD_BE_PARTITIONED": (
        "Requiere el numero de filas de la tabla; solo con el modelo cargado."),
    "REDUCE_USAGE_OF_LONG-LENGTH_COLUMNS_WITH_HIGH_CARDINALITY": (
        "Requiere cardinalidad real de la columna; solo con el modelo cargado."),
    "REMOVE_ROLES_WITH_NO_MEMBERS": (
        "Los miembros de un rol no viven en el TMDL, se asignan en el Service."),
}


# --------------------------------------------------------------------------- #
# Carga del catalogo oficial
# --------------------------------------------------------------------------- #

def cargar_bpa():
    """Lee la copia fijada de BPARules.json indexada por ID."""
    with open(RUTA_BPA, "rb") as f:
        raw = f.read()
    reglas = json.loads(raw.decode("utf-8-sig"))
    return {r["ID"]: r for r in reglas}


def sha256_bpa():
    with open(RUTA_BPA, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha256_fijado():
    if not os.path.exists(RUTA_SHA):
        return None
    return open(RUTA_SHA, encoding="utf-8").read().split()[0]


def fuente_de(regla_oficial):
    """URL de la Description de la regla oficial, o el propio BPARules.json."""
    urls = re.findall(r"https?://[^\s\)\"]+", regla_oficial.get("Description", ""))
    return urls[0] if urls else FUENTE_BPA


def texto_de(regla_oficial):
    """Description de Microsoft, en una linea y sin la parte 'Reference:'."""
    d = regla_oficial.get("Description", "")
    d = re.split(r"\bReference:", d)[0]
    return " ".join(d.split())


# --------------------------------------------------------------------------- #
# Predicados: cada uno devuelve la lista de objetos que INCUMPLEN
#
# Firma: f(modelo) -> [(donde, detalle), ...]
# `donde` identifica el objeto; `detalle` explica el valor concreto que falla.
# --------------------------------------------------------------------------- #

NUMERICOS = {"int64", "decimal", "double"}


def _visible(tabla, obj=None):
    if tabla.oculto:
        return False
    return not (obj.oculto if obj is not None else False)


def r_source_column(m):
    out = []
    for t, c in m.columnas():
        # solo columnas de datos: las calculadas llevan expresion
        if c.expresion:
            continue
        if not c.prop("sourceColumn"):
            out.append((f"{t.nombre}[{c.nombre}]", "sin sourceColumn"))
    return out


def r_expresion_obligatoria(m):
    out = []
    for t, me in m.medidas():
        if not (me.expresion or "").strip():
            out.append((f"{t.nombre}[{me.nombre}]", "medida sin expresion DAX"))
    return out


def r_relacion_tipos(m):
    out = []
    for r in m.relaciones:
        f, tt = r.prop("fromColumn", ""), r.prop("toColumn", "")
        cf, ct = _resolver(m, f), _resolver(m, tt)
        if cf is None or ct is None:
            continue
        df, dt = cf.prop("dataType"), ct.prop("dataType")
        if df and dt and df != dt:
            out.append((f"{f} -> {tt}", f"{df} vs {dt}"))
    return out


def _resolver(m, ref):
    """'Tabla'.'Columna' o Tabla.Columna -> nodo columna."""
    partes = re.findall(r"'((?:[^']|'')*)'|([^.\s]+)", ref or "")
    partes = [(a or b).replace("''", "'") for a, b in partes]
    if len(partes) != 2:
        return None
    return m.columna(partes[0], partes[1])


def r_espacios_en_nombres(m):
    out = []
    for nombre, obj in _todos_los_nombres(m):
        if nombre != nombre.strip():
            out.append((f"{obj}", f"'{nombre}'"))
    return out


def r_caracteres_invalidos(m):
    out = []
    for nombre, obj in _todos_los_nombres(m):
        malos = [c for c in nombre if ord(c) < 32 or ord(c) == 127]
        if malos:
            out.append((f"{obj}", "contiene caracteres de control"))
    return out


def r_caracteres_especiales(m):
    out = []
    for nombre, obj in _todos_los_nombres(m):
        if any(c in nombre for c in ("\t", "\n", "\r")):
            out.append((f"{obj}", "tabulador o salto de linea en el nombre"))
    return out


def _todos_los_nombres(m):
    for t in m.tablas:
        yield t.nombre, f"tabla {t.nombre}"
        for c in t.de_tipo("column"):
            yield c.nombre, f"{t.nombre}[{c.nombre}]"
        for me in t.de_tipo("measure"):
            yield me.nombre, f"medida {me.nombre}"
        for p in t.de_tipo("partition"):
            yield p.nombre, f"particion {t.nombre}/{p.nombre}"


def r_formatstring_medidas(m):
    out = []
    for t, me in m.medidas():
        if not _visible(t, me):
            continue
        if not (me.prop("formatString") or "").strip():
            out.append((f"{t.nombre}[{me.nombre}]", "medida visible sin formatString"))
    return out


def r_summarizeby_numerico(m):
    out = []
    for t, c in m.columnas():
        if not _visible(t, c):
            continue
        if (c.prop("dataType") or "").lower() in NUMERICOS:
            sb = (c.prop("summarizeBy") or "").lower()
            if sb and sb != "none":
                out.append((f"{t.nombre}[{c.nombre}]",
                            f"summarizeBy={c.prop('summarizeBy')} (deberia ser none)"))
    return out


def r_divide(m):
    """Regex OFICIAL de Microsoft, tal cual."""
    out = []
    for t, me in m.medidas():
        e = me.expresion or ""
        if re.search(r"\]\s*/(?!/)(?!\*)", e) or re.search(r"\)\s*/(?!/)(?!\*)", e):
            out.append((f"{t.nombre}[{me.nombre}]", "usa '/' en vez de DIVIDE()"))
    return out


def r_iferror(m):
    out = []
    for t, me in m.medidas():
        if re.search(r"(?i)IFERROR\s*\(", me.expresion or ""):
            out.append((f"{t.nombre}[{me.nombre}]", "usa IFERROR"))
    return out


def r_intersect(m):
    out = []
    for t, me in m.medidas():
        if re.search(r"(?i)\bINTERSECT\s*\(", me.expresion or ""):
            out.append((f"{t.nombre}[{me.nombre}]", "usa INTERSECT en vez de TREATAS"))
    return out


def r_evaluateandlog(m):
    out = []
    for t, me in m.medidas():
        if re.search(r"(?i)EVALUATEANDLOG\s*\(", me.expresion or ""):
            out.append((f"{t.nombre}[{me.nombre}]", "EVALUATEANDLOG en produccion"))
    return out


def r_uno_menos_xy(m):
    out = []
    for t, me in m.medidas():
        e = me.expresion or ""
        if (re.search(r"[0-9]+\s*[-+]\s*[\(]*\s*(?i:SUM)\s*\(\s*'*[A-Za-z0-9 _]+'*\s*\[[A-Za-z0-9 _]+\]\s*\)\s*/", e)
                or re.search(r"[0-9]+\s*[-+]\s*(?i:DIVIDE)\s*\(", e)):
            out.append((f"{t.nombre}[{me.nombre}]", "sintaxis 1-(x/y)"))
    return out


FMT_PCT = "#,0.0%;-#,0.0%;#,0.0%"


def r_formato_porcentaje(m):
    out = []
    for t, me in m.medidas():
        f = me.prop("formatString") or ""
        if "%" in f and f != FMT_PCT:
            out.append((f"{t.nombre}[{me.nombre}]", f"'{f}' (canonico: '{FMT_PCT}')"))
    return out


def r_formato_entero(m):
    out = []
    for t, me in m.medidas():
        f = me.prop("formatString") or ""
        if not f:
            continue
        if "$" not in f and "%" not in f and f not in ("#,0", "#,0.0"):
            out.append((f"{t.nombre}[{me.nombre}]", f"'{f}' (canonico: '#,0' o '#,0.0')"))
    return out


def r_double(m):
    out = []
    for t, c in m.columnas():
        if (c.prop("dataType") or "").lower() == "double":
            out.append((f"{t.nombre}[{c.nombre}]", "dataType double"))
    return out


def r_modelo_con_calendario(m):
    for t in m.tablas:
        if (t.prop("dataCategory") == "Time"
                and any(c.bool_prop("isKey") and (c.prop("dataType") or "").lower() == "datetime"
                        for c in t.de_tipo("column"))):
            return []
    return [("modelo", "no hay tabla marcada como tabla de fecha")]


def r_calendario_marcado(m):
    out = []
    for t in m.tablas:
        n = t.nombre.upper()
        if "DATE" not in n and "CALENDAR" not in n and "FECHA" not in n:
            continue
        ok = (t.prop("dataCategory") == "Time"
              and any(c.bool_prop("isKey") and (c.prop("dataType") or "").lower() == "datetime"
                      for c in t.de_tipo("column")))
        if not ok:
            out.append((f"tabla {t.nombre}",
                        "parece calendario pero no esta marcada como tabla de fecha "
                        "(dataCategory: Time + una columna isKey dateTime)"))
    return out


def r_auto_date(m):
    out = []
    for t in m.tablas:
        if t.nombre.startswith(("DateTableTemplate_", "LocalDateTable_")):
            out.append((f"tabla {t.nombre}",
                        "tabla de Auto date/time: apaga la opcion en Power BI Desktop"))
    return out


def r_m2m_bidireccional(m):
    out = []
    for r in m.relaciones:
        if (r.prop("fromCardinality") == "many" and r.prop("toCardinality") == "many"
                and r.prop("crossFilteringBehavior") == "bothDirections"):
            out.append((f"{r.prop('fromColumn')} -> {r.prop('toColumn')}",
                        "muchos-a-muchos en ambas direcciones"))
    return out


def r_exceso_bidireccional(m):
    bidi = [r for r in m.relaciones
            if r.prop("crossFilteringBehavior") == "bothDirections"]
    m2m = [r for r in m.relaciones
           if r.prop("fromCardinality") == "many" and r.prop("toCardinality") == "many"]
    total = len(m.relaciones) or 1
    if (len(bidi) + len(m2m)) / total > 0.3:
        return [("modelo", f"{len(bidi)} bidireccionales + {len(m2m)} m2m "
                           f"de {total} relaciones (>30%)")]
    return []


def r_particion_nombre(m):
    out = []
    for t in m.tablas:
        ps = t.de_tipo("partition")
        if len(ps) == 1 and ps[0].nombre != t.nombre:
            out.append((f"tabla {t.nombre}",
                        f"su unica particion se llama '{ps[0].nombre}'"))
    return out


def r_sin_descripcion(m):
    out = []
    for t in m.tablas:
        if not t.oculto and not (t.descripcion or "").strip():
            out.append((f"tabla {t.nombre}", "sin descripcion ///"))
    for t, me in m.medidas():
        if _visible(t, me) and not (me.descripcion or "").strip():
            out.append((f"{t.nombre}[{me.nombre}]", "medida visible sin descripcion ///"))
    return out


def r_primera_mayuscula(m):
    out = []
    for t in m.tablas:
        n = t.nombre
        if n and n[0].isalpha() and n[0] != n[0].upper():
            out.append((f"tabla {n}", "empieza en minuscula"))
    for t, me in m.medidas():
        n = me.nombre
        if n and n[0].isalpha() and n[0] != n[0].upper():
            out.append((f"medida {n}", "empieza en minuscula"))
    return out


# --- reglas PROPIAS: donde el catalogo oficial no llega ---------------------

# Palabra COMPLETA, no subcadena. La regla oficial usa `Name.Contains("MONTH")`,
# que en ingles casi no falla, pero en español "MES" es subcadena de "TRIMESTRE",
# "SEMESTRE", "MESTIZO"... El primer intento reportaba `Calendario[Trimestre]`
# como columna de mes sin ordenar. Se exige limite de palabra.
_MES_RE = re.compile(r"(?<![A-ZÁÉÍÓÚÑ])(MES|MONTH)(?![A-ZÁÉÍÓÚÑ])")
_MESES_RE = re.compile(r"(?<![A-ZÁÉÍÓÚÑ])(MESES|MONTHS)(?![A-ZÁÉÍÓÚÑ])")


def r_mes_ordenado(m):
    """
    Equivalente en español de MONTH_(AS_A_STRING)_MUST_BE_SORTED.

    La regla oficial busca "MONTH" en el nombre, asi que nunca ve una columna
    `Mes`. Sin `sortByColumn`, un slicer de meses sale en orden alfabetico
    (Abril, Agosto, Diciembre...) y el reporte parece roto.
    """
    out = []
    for t, c in m.columnas():
        n = c.nombre.upper()
        if not _MES_RE.search(n) or _MESES_RE.search(n):
            continue
        if (c.prop("dataType") or "").lower() != "string":
            continue
        if not c.prop("sortByColumn"):
            out.append((f"{t.nombre}[{c.nombre}]",
                        "columna de mes en texto sin sortByColumn: se ordenara "
                        "alfabeticamente (Abril, Agosto, Diciembre...)"))
    return out


# --------------------------------------------------------------------------- #
# Registro: ID oficial -> predicado
# --------------------------------------------------------------------------- #

OFICIALES = {
    "DATA_COLUMNS_MUST_HAVE_A_SOURCE_COLUMN": r_source_column,
    "EXPRESSION_RELIANT_OBJECTS_MUST_HAVE_AN_EXPRESSION": r_expresion_obligatoria,
    "RELATIONSHIP_COLUMNS_SAME_DATA_TYPE": r_relacion_tipos,
    "OBJECTS_SHOULD_NOT_START_OR_END_WITH_A_SPACE": r_espacios_en_nombres,
    "TRIM_OBJECT_NAMES": r_espacios_en_nombres,
    "AVOID_INVALID_NAME_CHARACTERS": r_caracteres_invalidos,
    "SPECIAL_CHARS_IN_OBJECT_NAMES": r_caracteres_especiales,
    "PROVIDE_FORMAT_STRING_FOR_MEASURES": r_formatstring_medidas,
    "NUMERIC_COLUMN_SUMMARIZE_BY": r_summarizeby_numerico,
    "USE_THE_DIVIDE_FUNCTION_FOR_DIVISION": r_divide,
    "AVOID_USING_THE_IFERROR_FUNCTION": r_iferror,
    "USE_THE_TREATAS_FUNCTION_INSTEAD_OF_INTERSECT": r_intersect,
    "EVALUATEANDLOG_SHOULD_NOT_BE_USED_IN_PRODUCTION_MODELS": r_evaluateandlog,
    "AVOID_USING_'1-(X/Y)'_SYNTAX": r_uno_menos_xy,
    "PERCENTAGE_FORMATTING": r_formato_porcentaje,
    "INTEGER_FORMATTING": r_formato_entero,
    "AVOID_FLOATING_POINT_DATA_TYPES": r_double,
    "MODEL_SHOULD_HAVE_A_DATE_TABLE": r_modelo_con_calendario,
    "DATE/CALENDAR_TABLES_SHOULD_BE_MARKED_AS_A_DATE_TABLE": r_calendario_marcado,
    "REMOVE_AUTO-DATE_TABLE": r_auto_date,
    "MANY-TO-MANY_RELATIONSHIPS_SHOULD_BE_SINGLE-DIRECTION": r_m2m_bidireccional,
    "AVOID_EXCESSIVE_BI-DIRECTIONAL_OR_MANY-TO-MANY_RELATIONSHIPS": r_exceso_bidireccional,
    "PARTITION_NAME_SHOULD_MATCH_TABLE_NAME_FOR_SINGLE_PARTITION_TABLES": r_particion_nombre,
    "OBJECTS_WITH_NO_DESCRIPTION": r_sin_descripcion,
    "FIRST_LETTER_OF_OBJECTS_MUST_BE_CAPITALIZED": r_primera_mayuscula,
}

# Reglas propias: (codigo, severidad_oficial_equivalente, titulo, arreglo, fuente, predicado)
PROPIAS = [
    ("PBI-NAME-01", 2,
     "Columna de mes en texto sin sortByColumn (equivalente en español)",
     "Pon sortByColumn apuntando al numero de mes (p. ej. NumMes). La regla "
     "oficial MONTH_(AS_A_STRING)_MUST_BE_SORTED solo busca nombres en ingles.",
     "https://learn.microsoft.com/power-bi/create-reports/desktop-sort-by-column",
     r_mes_ordenado),
]


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #

class Regla:
    __slots__ = ("codigo", "severidad", "peso", "categoria", "titulo", "texto",
                 "fuente", "nivel_fuente", "predicado", "origen")

    def __init__(self, codigo, sev_num, categoria, titulo, texto, fuente, predicado,
                 origen):
        self.codigo = codigo
        self.severidad, self.peso = SEVERIDAD.get(sev_num, ("BAJA", 3))
        self.categoria = categoria
        self.titulo = titulo
        self.texto = texto
        self.fuente = fuente
        self.nivel_fuente = nivel_autoridad(fuente)
        self.predicado = predicado
        self.origen = origen  # "microsoft" | "propia"


def construir():
    """Lista de Regla lista para evaluar. Falla si alguna no tiene fuente."""
    bpa = cargar_bpa()
    reglas = []
    for rid, pred in OFICIALES.items():
        of = bpa.get(rid)
        if of is None:
            raise SystemExit(
                f"ERROR: la regla oficial '{rid}' no esta en BPARules.json. "
                "Microsoft pudo renombrarla o retirarla: corre "
                "`python scripts/actualizar_catalogo.py --forzar` y revisa "
                "la fuente `bpa_rules`.")
        reglas.append(Regla(
            rid, of["Severity"], of.get("Category", "?"),
            of.get("Name", rid), texto_de(of), fuente_de(of), pred, "microsoft"))
    for codigo, sev, titulo, arreglo, fuente, pred in PROPIAS:
        reglas.append(Regla(codigo, sev, "Propia", titulo, arreglo, fuente, pred,
                            "propia"))
    return reglas


def verificar_catalogo():
    """
    Guarda del catalogo. Devuelve la lista de problemas (vacia = todo bien).

    Comprueba lo que la regla dura #7 exige: que ninguna regla quede sin fuente y
    que ninguna de severidad ALTA se apoye solo en un nivel 5 de autoridad.
    Ademas, que la copia local de BPARules.json coincida con su SHA fijado.
    """
    problemas = []
    esperado, actual = sha256_fijado(), sha256_bpa()
    if esperado and esperado != actual:
        problemas.append(
            f"BPARules.json no coincide con su SHA-256 fijado "
            f"({actual[:12]} != {esperado[:12]}). Si lo actualizaste a proposito, "
            "regenera references/bpa/BPARules.sha256 y anotalo en el CHANGELOG.")
    for r in construir():
        if not r.fuente:
            problemas.append(f"{r.codigo}: sin fuente (campo obligatorio)")
        elif r.severidad == "ALTA" and r.nivel_fuente >= 5:
            problemas.append(
                f"{r.codigo}: severidad ALTA sustentada solo en una fuente de "
                f"nivel 5 ({r.fuente}). Busca respaldo oficial o baja la severidad.")
    return problemas


def evaluar(modelo):
    """Evalua el catalogo sobre un Modelo ya parseado. Devuelve hallazgos."""
    hallazgos = []
    for r in construir():
        for donde, detalle in r.predicado(modelo):
            hallazgos.append({
                "codigo": r.codigo, "severidad": r.severidad, "peso": r.peso,
                "categoria": r.categoria, "titulo": r.titulo, "donde": donde,
                "detalle": detalle, "fuente": r.fuente, "origen": r.origen,
            })
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    hallazgos.sort(key=lambda h: (orden[h["severidad"]], h["codigo"], h["donde"]))
    return hallazgos


def resumen():
    """Recuento del catalogo, para documentacion y para el --help."""
    reglas = construir()
    return {
        "total": len(reglas),
        "microsoft": sum(1 for r in reglas if r.origen == "microsoft"),
        "propias": sum(1 for r in reglas if r.origen == "propia"),
        "por_severidad": {s: sum(1 for r in reglas if r.severidad == s)
                          for s in ("ALTA", "MEDIA", "BAJA")},
        "oficiales_disponibles": len(cargar_bpa()),
        "excluidas": len(EXCLUIDAS),
    }


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    problemas = verificar_catalogo()
    r = resumen()
    print(f"Catalogo de reglas del modelo")
    print(f"  implementadas      : {r['total']}  "
          f"({r['microsoft']} oficiales de Microsoft + {r['propias']} propias)")
    print(f"  por severidad      : {r['por_severidad']}")
    print(f"  disponibles en BPA : {r['oficiales_disponibles']} "
          f"(excluidas a proposito: {r['excluidas']})")
    print(f"  BPARules.json sha  : {sha256_bpa()[:16]}...")
    if problemas:
        print("")
        for p in problemas:
            print(f"[FALLA] {p}")
        sys.exit(1)
    print("  OK  toda regla tiene fuente y ninguna ALTA se apoya en nivel 5.")
