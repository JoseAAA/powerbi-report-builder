#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificar_cableado.py — Guarda de regresion del bug del MVP huerfano.

El bug que evita
----------------
`init_proyecto.py` generaba tres artefactos que no se hablaban entre si:
miles de filas en CSV, un `modelo-ejemplo.m` para pegar a mano, y un `.pbip`
con seis filas inventadas inline. El usuario abria el reporte esperando su
mockup y veia datos falsos, mientras los datos reales quedaban huerfanos en la
carpeta de al lado. Peor: la clave `ID Indicador` del hecho no apuntaba a
ninguna dimension, asi que al cablear los CSV sin arreglar el modelo el KPI
principal daba 5226% (mezclaba porcentajes con importes).

Los tres validadores del repo daban VERDE mientras eso pasaba, porque validan
las reglas del propio framework y no si el proyecto describe algo coherente.
Este script cierra ese hueco.

Que comprueba (E1-E6)
---------------------
  E1  El .pbip esta en la RAIZ del proyecto (Fabric Git Integration).
  E2  Existe `expressions.tmdl` con el parametro RutaBase.
  E3  TODA tabla con CSV en datos/ tiene una particion que LEE ese CSV
      (nadie quedo con datos inline mientras hay un CSV disponible).
  E4  Las columnas que declara cada particion existen en la cabecera del CSV.
  E5  Cada clave `ID X` del hecho tiene su dimension y su relacion.
  E6  Ninguna medida hace DIVIDE sobre el hecho sin defensa por indicador.

Uso:
  python verificar_cableado.py <carpeta del proyecto>

Salida: exit 0 si todo cuadra, 1 si hay fallas (imprime cada una con su arreglo).
Solo libreria estandar.
"""
import csv
import glob
import os
import re
import sys


def _leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def _cabecera_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        for fila in csv.reader(f):
            return fila
    return []


def verificar(proyecto):
    fallas = []
    proyecto = os.path.abspath(proyecto)

    # --- E1: .pbip en la raiz ---
    pbips = glob.glob(os.path.join(proyecto, "*.pbip"))
    if not pbips:
        hondo = glob.glob(os.path.join(proyecto, "**", "*.pbip"), recursive=True)
        if hondo:
            rel = os.path.relpath(hondo[0], proyecto)
            fallas.append(
                f"E1: el .pbip esta enterrado en '{rel}', no en la raiz del proyecto.\n"
                "    Arreglo: genera con `scaffold_pbip.py --en-raiz` (o init_proyecto.py). "
                "Fabric Git Integration busca los items en la raiz.")
        else:
            fallas.append(f"E1: no hay ningun .pbip en {proyecto}.")
        return fallas

    sm_dirs = glob.glob(os.path.join(proyecto, "*.SemanticModel"))
    if not sm_dirs:
        fallas.append("E1: no hay carpeta *.SemanticModel junto al .pbip.")
        return fallas
    sm = sm_dirs[0]
    tdir = os.path.join(sm, "definition", "tables")
    datos = os.path.join(proyecto, "datos")

    # --- E2: parametro RutaBase ---
    expr = os.path.join(sm, "definition", "expressions.tmdl")
    hay_csv = os.path.isdir(datos) and glob.glob(os.path.join(datos, "*.csv"))
    if hay_csv:
        if not os.path.exists(expr):
            fallas.append(
                "E2: hay CSV en datos/ pero falta expressions.tmdl con el parametro "
                "RutaBase.\n    Sin ese archivo las particiones no pueden apuntar a los "
                "CSV salvo con una ruta absoluta incrustada.")
        elif "IsParameterQuery=true" not in _leer(expr):
            fallas.append(
                "E2: expressions.tmdl existe pero RutaBase no es un parametro real "
                "(falta IsParameterQuery=true), asi que no aparece en "
                "'Administrar parametros'.")

    # --- E3/E4: cada CSV tiene su particion, con las columnas correctas ---
    tmdls = {os.path.splitext(os.path.basename(p))[0]: p
             for p in glob.glob(os.path.join(tdir, "*.tmdl"))}
    for csv_path in sorted(glob.glob(os.path.join(datos, "*.csv"))):
        tabla = os.path.splitext(os.path.basename(csv_path))[0]
        tmdl = tmdls.get(tabla)
        if not tmdl:
            fallas.append(
                f"E3: existe datos/{tabla}.csv pero el modelo no tiene la tabla "
                f"'{tabla}'.\n    Los datos y el modelo describen cosas distintas.")
            continue
        texto = _leer(tmdl)
        if f'File.Contents(RutaBase & "\\{tabla}.csv")' not in texto:
            inline = "#table(" in texto
            fallas.append(
                f"E3: la tabla '{tabla}' NO lee datos/{tabla}.csv"
                + (" (tiene datos inline #table con el CSV disponible al lado)."
                   if inline else ".")
                + "\n    Arreglo: genera con `--datos <carpeta>` para que la particion "
                  "lea el CSV via RutaBase.")
            continue
        # E4: columnas declaradas vs cabecera real del CSV
        declaradas = set(re.findall(r'\{"([^"]+)",\s*(?:type\s+\w+|Int64\.Type)\}', texto))
        reales = set(_cabecera_csv(csv_path))
        faltan = declaradas - reales
        if faltan:
            fallas.append(
                f"E4: la particion de '{tabla}' declara columnas que el CSV no tiene: "
                f"{sorted(faltan)}.\n    Cabecera real: {sorted(reales)}. "
                "Power Query fallara al refrescar.")

    # --- E5: toda clave 'ID X' del hecho tiene dimension y relacion ---
    rel_path = os.path.join(sm, "definition", "relationships.tmdl")
    rels = _leer(rel_path) if os.path.exists(rel_path) else ""
    for tabla, tmdl in sorted(tmdls.items()):
        texto = _leer(tmdl)
        # el hecho es la tabla que tiene columnas Num y Den
        if "sourceColumn: Num" not in texto or "sourceColumn: Den" not in texto:
            continue
        for clave in sorted(set(re.findall(r"sourceColumn: (ID .+)", texto))):
            dim = clave[3:]  # "ID Indicador" -> "Indicador"
            if dim not in tmdls:
                fallas.append(
                    f"E5: el hecho '{tabla}' tiene la clave '{clave}' pero no existe la "
                    f"tabla '{dim}'.\n    Es una clave huerfana: nada explica que "
                    "significa cada fila, y las medidas suman filas incomparables.")
            elif f".'{clave}'" not in rels and f".{clave}" not in rels:
                fallas.append(
                    f"E5: existe la tabla '{dim}' pero no hay relacion desde "
                    f"'{tabla}'.'{clave}'.\n    Sin la relacion el filtro no se propaga.")

    # --- E6: medidas con DIVIDE sin defensa por indicador ---
    med = tmdls.get("_ Medidas")
    if med and "Indicador" in tmdls:
        texto = _leer(med)
        # Se parte por objeto TMDL (measure/column/partition) y se inspecciona
        # cada bloque de medida por separado.
        bloques = re.split(r"\n\t(?=measure |column |partition )", texto)
        for b in bloques:
            m = re.match(r"measure\s+(?:'([^']+)'|([^\s=]+))", b.strip())
            if not m:
                continue
            nombre = m.group(1) or m.group(2)
            if "DIVIDE" not in b:
                continue
            defendida = ("HASONEVALUE" in b or "CALCULATE" in b
                         or "SELECTEDVALUE" in b or "VALUES" in b)
            if not defendida:
                fallas.append(
                    f"E6: la medida '{nombre}' hace DIVIDE sobre un hecho con varios "
                    "indicadores y no se defiende.\n    Sumaria indicadores "
                    "incomparables (un % junto con un importe). Arreglo: exige un solo "
                    "indicador con HASONEVALUE, o filtra con CALCULATE.")
    return fallas


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    proyecto = sys.argv[1]
    if not os.path.isdir(proyecto):
        print(f"ERROR: no es una carpeta: {proyecto}")
        raise SystemExit(2)

    fallas = verificar(proyecto)
    nombre = os.path.basename(os.path.abspath(proyecto))
    print(f"Cableado datos <-> modelo: {nombre}  |  Chequeos: E1-E6")
    if not fallas:
        print("OK  El .pbip lee los CSV, las claves tienen dimension y las medidas "
              "no mezclan indicadores.")
        return 0
    for f in fallas:
        print("[FALLA] " + f)
    print(f"\nTotal: {len(fallas)} fallas de cableado.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
