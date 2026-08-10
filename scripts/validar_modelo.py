#!/usr/bin/env python3
"""
validar_modelo.py — Validador BPA-lite para modelos semánticos en TMDL.

Uso:
  python validar_modelo.py <ruta a .SemanticModel/definition o carpeta tables/>

Aplica un subconjunto de reglas inspiradas en el Best Practice Analyzer
(Power BI CAT) sobre los archivos .tmdl:

  R1  Toda medida tiene formatString
  R2  Medidas largas (>80 chars de expresión) usan VAR/RETURN
  R3  División con '/' en vez de DIVIDE() cuando hay denominador variable
  R4  Medidas con nombre duplicado entre tablas
  R5  displayFolder ausente en modelos con >10 medidas
  R6  Evidencia de Auto date/time (tablas LocalDateTable_)
  R7  Columnas numéricas sumarizables visibles junto a medidas que las usan
  R8  Columnas sumarizables visibles (no referidas por medida): ocultar/volver medida
  R9  Columnas dateTime fuera del calendario (separar fecha/hora baja cardinalidad)
  R10 Relaciones bidireccionales (crossFilteringBehavior bothDirections)
  R11 Columnas calculadas (preferir Power Query M o medidas)
  R12 Medidas sin description (comentario /// encima del measure, sintaxis TMDL
      oficial; Copilot/IA y agentes LLM la leen — "Prepare data for AI" de Microsoft)

Salida: reporte por consola con severidad [ALTA]/[MEDIA]/[BAJA] y código de
salida 1 si hay hallazgos de severidad ALTA.
"""
import os
import re
import sys
from pathlib import Path


MEASURE_RE = re.compile(
    r"^\tmeasure\s+(?P<nombre>'[^']+'|[\w ]+?)\s*=\s*(?P<resto>.*)$"
)


def extraer_medidas(texto, archivo):
    """Devuelve lista de dicts: nombre, expresion, props (texto del bloque)."""
    lineas = texto.splitlines()
    medidas = []
    i = 0
    while i < len(lineas):
        m = MEASURE_RE.match(lineas[i])
        if not m:
            i += 1
            continue
        nombre = m.group("nombre").strip().strip("'")
        # description en TMDL = comentario /// en la(s) linea(s) inmediatamente
        # encima del measure (sin linea en blanco entre medio). Sintaxis oficial.
        tiene_desc = i > 0 and lineas[i - 1].strip().startswith("///")
        resto = m.group("resto").strip()
        expr_lineas = []
        if resto.startswith("```"):
            i += 1
            while i < len(lineas) and "```" not in lineas[i]:
                expr_lineas.append(lineas[i])
                i += 1
        else:
            expr_lineas.append(resto)
        # capturar propiedades (líneas con doble tab hasta el próximo objeto)
        props = []
        j = i + 1
        while j < len(lineas) and (lineas[j].startswith("\t\t") or lineas[j].strip() == ""):
            if lineas[j].strip():
                props.append(lineas[j].strip())
            j += 1
        medidas.append({
            "nombre": nombre,
            "expresion": "\n".join(expr_lineas).strip(),
            "props": props,
            "tiene_desc": tiene_desc,
            "archivo": archivo,
        })
        i = j
    return medidas


def extraer_columnas(texto):
    cols = []
    bloques = re.finditer(
        r"^\tcolumn\s+(?P<nombre>'[^']+'|[\w ]+)\s*$(?P<cuerpo>(?:\n\t\t.*)*)",
        texto, re.MULTILINE)
    for b in bloques:
        cuerpo = b.group("cuerpo")
        tipo_m = re.search(r"dataType:\s*(\w+)", cuerpo)
        cols.append({
            "nombre": b.group("nombre").strip().strip("'"),
            "oculta": "isHidden" in cuerpo,
            "suma": "summarizeBy: sum" in cuerpo,
            "tipo": tipo_m.group(1) if tipo_m else "",
        })
    return cols


def _ruta_io(ruta):
    """En Windows, prefijo \\\\?\\ para leer árboles PBIP más allá de MAX_PATH."""
    if os.name != "nt":
        return ruta
    ruta = os.path.abspath(ruta)
    if ruta.startswith("\\\\?\\"):
        return ruta
    if ruta.startswith("\\\\"):  # UNC: \\server\share -> \\?\UNC\server\share
        return "\\\\?\\UNC" + ruta[1:]
    return "\\\\?\\" + ruta


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    mostrar = sys.argv[1]  # ruta tal como la pasó el usuario, para mensajes
    raiz = Path(_ruta_io(sys.argv[1]))
    if not raiz.exists():
        print(f"No existe la ruta: {mostrar}")
        return 2

    archivos = sorted(raiz.rglob("*.tmdl"))
    if not archivos:
        print("No se encontraron archivos .tmdl")
        return 2

    todas, columnas_por_tabla, hallazgos = [], {}, []
    meta_por_tabla = {}
    auto_datetime = False
    bidireccionales = 0

    for f in archivos:
        texto = f.read_text(encoding="utf-8", errors="replace")
        if "LocalDateTable_" in texto or "LocalDateTable_" in f.name:
            auto_datetime = True
        bidireccionales += len(re.findall(r"crossFilteringBehavior:\s*bothDirections", texto))
        if f.parent.name == "tables" or "\tmeasure" in texto or "measure " in texto:
            ms = extraer_medidas(texto, f.name)
            todas.extend(ms)
            columnas_por_tabla[f.stem] = extraer_columnas(texto)
            calc = re.findall(r"^\tcolumn\s+('[^']+'|[\w ]+?)\s*=", texto, re.MULTILINE)
            meta_por_tabla[f.stem] = {
                "calendario": "dataCategory: Time" in texto,
                "calculadas": [c.strip().strip("'") for c in calc],
            }

    # R1 formatString
    for m in todas:
        if not any(p.startswith("formatString") for p in m["props"]):
            hallazgos.append(("MEDIA", "R1", f"Medida '{m['nombre']}' sin formatString ({m['archivo']})"))

    # R2 VAR/RETURN
    for m in todas:
        e = m["expresion"]
        if len(e) > 80 and ("VAR" not in e.upper() or "RETURN" not in e.upper()):
            hallazgos.append(("MEDIA", "R2", f"Medida '{m['nombre']}' es larga y no usa VAR/RETURN"))

    # R3 división directa (heurística: '/' fuera de comentarios y no en fecha)
    for m in todas:
        e = re.sub(r"//.*", "", m["expresion"])
        e = re.sub(r"\".*?\"", "", e)
        if re.search(r"[\]\)\w]\s*/\s*[\[\(\w]", e) and "DIVIDE" not in e.upper():
            hallazgos.append(("ALTA", "R3", f"Medida '{m['nombre']}' divide con '/'; usar DIVIDE() para manejar cero/blank"))

    # R4 duplicados
    vistos = {}
    for m in todas:
        if m["nombre"] in vistos and vistos[m["nombre"]] != m["archivo"]:
            hallazgos.append(("ALTA", "R4", f"Medida '{m['nombre']}' duplicada en {vistos[m['nombre']]} y {m['archivo']}"))
        vistos[m["nombre"]] = m["archivo"]

    # R5 displayFolder
    if len(todas) > 10:
        sin_folder = [m for m in todas if not any(p.startswith("displayFolder") for p in m["props"])]
        if sin_folder:
            hallazgos.append(("BAJA", "R5", f"{len(sin_folder)} medidas sin displayFolder en un modelo con {len(todas)} medidas"))

    # R6 auto date/time
    if auto_datetime:
        hallazgos.append(("ALTA", "R6", "Evidencia de Auto date/time (LocalDateTable). Desactivarlo y usar calendario propio"))

    # R7 columnas sumarizables visibles referenciadas por medidas
    for tabla, cols in columnas_por_tabla.items():
        exprs = " ".join(m["expresion"] for m in todas)
        for c in cols:
            if c["suma"] and not c["oculta"] and re.search(
                    rf"\b{re.escape(tabla)}\s*\[\s*{re.escape(c['nombre'])}\s*\]", exprs):
                hallazgos.append(("BAJA", "R7", f"Columna {tabla}[{c['nombre']}] es sumarizable, visible y ya tiene medida: ocultarla"))

    # R8 columnas sumarizables visibles no señaladas por R7: ocultar o volver medida
    exprs_all = " ".join(m["expresion"] for m in todas)
    r7_set = {(t, c["nombre"]) for t, cols in columnas_por_tabla.items()
              for c in cols if c["suma"] and not c["oculta"]
              and re.search(rf"\b{re.escape(t)}\s*\[\s*{re.escape(c['nombre'])}\s*\]", exprs_all)}
    for tabla, cols in columnas_por_tabla.items():
        for c in cols:
            if c["suma"] and not c["oculta"] and (tabla, c["nombre"]) not in r7_set:
                hallazgos.append(("BAJA", "R8", f"Columna {tabla}[{c['nombre']}] es sumarizable y visible: ocultala o conviertela en medida"))

    # R9 columnas dateTime fuera de la tabla de calendario (separar fecha/hora baja cardinalidad)
    for tabla, cols in columnas_por_tabla.items():
        if meta_por_tabla.get(tabla, {}).get("calendario"):
            continue
        for c in cols:
            if c["tipo"] == "dateTime" and c["nombre"].lower() not in ("fecha", "date", "dia", "día"):
                hallazgos.append(("BAJA", "R9", f"Columna {tabla}[{c['nombre']}] es dateTime fuera del calendario: separa fecha y hora para bajar cardinalidad"))

    # R10 relaciones bidireccionales
    if bidireccionales:
        hallazgos.append(("MEDIA", "R10", f"{bidireccionales} relacion(es) bidireccional(es): usa filtro simple y CROSSFILTER/TREATAS puntual"))

    # R11 columnas calculadas (preferir Power Query M o medidas)
    for tabla, meta in meta_por_tabla.items():
        for c in meta["calculadas"]:
            hallazgos.append(("MEDIA", "R11", f"Columna calculada {tabla}[{c}]: evalua moverla a Power Query (M) o a una medida"))

    # R12 medidas sin description (clave para Copilot/IA y agentes LLM que leen el modelo).
    # En TMDL la description es un comentario /// encima del measure (sintaxis oficial).
    for m in todas:
        if not m.get("tiene_desc"):
            hallazgos.append(("BAJA", "R12", f"Medida '{m['nombre']}' sin description (/// encima del measure): agrega una frase de negocio (Copilot/IA la usa; ver preparar-datos-ia.md)"))

    # --- Catalogo OFICIAL de Microsoft (BPARules.json) ---------------------
    # Nuestras reglas R1-R12 cubren las convenciones del framework. Estas son las
    # de Microsoft, evaluadas sobre el modelo parseado con scripts/tmdl.py y
    # citando el ID oficial y su fuente. Si el catalogo no se puede cargar (copia
    # ausente o corrupta) se avisa y se sigue: R1-R12 no dependen de el.
    # Reglas propias que una regla OFICIAL cubre igual o mejor. Cuando el catalogo
    # de Microsoft esta disponible se suprimen: reportar el mismo problema dos
    # veces con codigos distintos es ruido, y la version oficial ademas trae cita.
    # Si el catalogo no carga, se evaluan como respaldo.
    # R1 NO cede: la regla oficial exime a las medidas de una tabla oculta
    # (`not Table.IsHidden`), y ocultar la tabla `_ Medidas` es el patron
    # ESTANDAR — las medidas siguen siendo las que usa el lector. Al cederla,
    # ninguna medida de un modelo bien construido quedaba cubierta. Detectado
    # metiendo el fallo a proposito y viendo que no se reportaba.
    SUPERSEDIDAS = {
        "R3": "USE_THE_DIVIDE_FUNCTION_FOR_DIVISION",
        "R6": "REMOVE_AUTO-DATE_TABLE",
        "R12": "OBJECTS_WITH_NO_DESCRIPTION",
    }
    n_oficiales = 0
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import catalogo_reglas
        import tmdl as _tmdl
        n_oficiales = len(catalogo_reglas.construir())
        modelo_obj = _tmdl.cargar(str(raiz))
        for h in catalogo_reglas.evaluar(modelo_obj):
            hallazgos.append((h["severidad"], h["codigo"],
                              f"{h['donde']}: {h['detalle']}  [fuente: {h['fuente']}]"))
        hallazgos = [h for h in hallazgos if h[1] not in SUPERSEDIDAS]
    except Exception as e:  # noqa: BLE001 — el validador propio no debe caerse
        print(f"AVISO: no se pudo evaluar el catalogo oficial de Microsoft ({e}).")
        print("       Las reglas R1-R12 del framework si se evaluaron, incluidas las")
        print("       que normalmente cede a su equivalente oficial.")

    etiqueta = f"R1-R12 + {n_oficiales} reglas oficiales" if n_oficiales else "R1-R12"
    print(f"Modelo: {mostrar}  |  Archivos .tmdl: {len(archivos)}  |  "
          f"Medidas: {len(todas)}  |  Reglas: {etiqueta}")
    if not hallazgos:
        print(f"OK  Sin hallazgos ({etiqueta}).")
        return 0
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    for sev, regla, msg in sorted(hallazgos, key=lambda h: (orden[h[0]], h[1])):
        print(f"[{sev}] {regla}: {msg}")
    altas = sum(1 for h in hallazgos if h[0] == "ALTA")
    print(f"\nTotal: {len(hallazgos)} hallazgos ({altas} de severidad ALTA)")
    return 1 if altas else 0


if __name__ == "__main__":
    sys.exit(main())
