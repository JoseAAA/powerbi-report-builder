#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_datos_ejemplo.py — Generador de datos de ejemplo + codigo Power Query M
para arrancar un MVP de Power BI con un modelo estrella.

GENERICO Y MULTI-DOMINIO: elige el dominio con --dominio. Cada dominio define sus
dos dimensiones y sus indicadores; la estructura (modelo estrella con patron
Num/Den) es la misma. No esta atado a ninguna empresa ni sector.

Que genera (5 CSV + 1 .m):
  <Calendario>.csv   dimension fecha
  <Dim1>.csv         dimension 1 (p. ej. Region, Sede, Departamento)
  <Dim2>.csv         dimension 2 con columna de agrupacion (p. ej. Producto)
  Indicador.csv      dimension de indicadores (que mide cada fila del hecho)
  <Hecho>.csv        HECHO con patron Num / Den por indicador
  modelo-ejemplo.m   codigo Power Query M listo para pegar (una seccion por
                     tabla); incluye, comentada, una variante SharePoint.

El hecho es "alto": una fila por Fecha x Dim1 x Dim2 x indicador. Ese diseno
EXIGE la dimension Indicador — sin ella las medidas suman atravesando
indicadores y mezclan porcentajes con importes (p. ej. % Margen + Ticket
Promedio -> 5226%). El catalogo de dominios vive en `dominios.py`, compartido
con `scaffold_pbip.py` para que los CSV y el .pbip nunca describan modelos
distintos.

Convencion de nombres (mejor practica Tabular Editor / Microsoft):
  nombres de negocio legibles, con espacios, SIN prefijos dim_/fact_.

Uso:
  python generar_datos_ejemplo.py --dominio ventas
  python generar_datos_ejemplo.py --dominio salud --salida ./datos-ejemplo
  python generar_datos_ejemplo.py --dominio rrhh --desde 2024-01-01 --hasta 2024-12-31
  python generar_datos_ejemplo.py --salida /tmp/datos --ruta-base "C:\\Datos\\PowerBI"

Argumentos:
  --dominio     ventas | rrhh | finanzas | salud | generico (default: generico)
  --salida      Carpeta de salida (default: ./datos-ejemplo)
  --desde       Fecha inicial AAAA-MM-DD (default: 2024-01-01)
  --hasta       Fecha final   AAAA-MM-DD (default: fecha actual)
  --filas       Limite opcional de filas del hecho (recorta el resultado)
  --ruta-base   Ruta base que se escribe en el .m para los File.Contents
                (default: el path absoluto de la carpeta de salida)

Requisitos: solo libreria estandar (csv, datetime, random, argparse, os).
Los CSV se escriben en UTF-8 (con BOM) para que Excel/Power BI lean las tildes.
"""
import argparse
import csv
import datetime as dt
import os
import random
import sys

# El catalogo de dominios es compartido con scaffold_pbip.py (fuente unica).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dominios import (  # noqa: E402
    DOMINIOS, MESES_ES, TABLA_INDICADOR,
    esquema_csv, filas_indicador, nombres,
)


# --------------------------------------------------------------------------- #
# Catalogo de dominios: vive en `dominios.py` (importado arriba).
#
# Estuvo duplicado aqui y en scaffold_pbip.py, y los dos diccionarios
# divergieron en TODOS los dominios (ventas: 6 productos en los CSV vs 4 en el
# TMDL). Un solo catalogo compartido hace imposible esa divergencia.
# --------------------------------------------------------------------------- #



# --------------------------------------------------------------------------- #
# Utilidades de fechas
# --------------------------------------------------------------------------- #

def parse_fecha(texto):
    """Convierte 'AAAA-MM-DD' en date. Lanza ValueError si el formato es invalido."""
    return dt.datetime.strptime(texto, "%Y-%m-%d").date()


def rango_dias(desde, hasta):
    """Genera cada date entre desde y hasta (ambos inclusive)."""
    actual = desde
    un_dia = dt.timedelta(days=1)
    while actual <= hasta:
        yield actual
        actual += un_dia


def primer_dia_de_cada_mes(desde, hasta):
    """Lista de dates correspondientes al dia 1 de cada mes del rango."""
    meses = []
    anio, mes = desde.year, desde.month
    while (anio, mes) <= (hasta.year, hasta.month):
        meses.append(dt.date(anio, mes, 1))
        if mes == 12:
            anio, mes = anio + 1, 1
        else:
            mes += 1
    return meses


# --------------------------------------------------------------------------- #
# Escritura de CSV (UTF-8 con BOM)
# --------------------------------------------------------------------------- #

def escribir_csv(ruta, cabeceras, filas):
    """Escribe un CSV en UTF-8-SIG (BOM) con saltos de linea estandar."""
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabeceras)
        escritor.writerows(filas)
    return len(filas)


# --------------------------------------------------------------------------- #
# Generadores de cada tabla (dirigidos por la config del dominio)
# --------------------------------------------------------------------------- #

def generar_calendario(desde, hasta):
    """Una fila por dia: Fecha, Año, Mes, NumMes, Trimestre, EsDiaHabil.

    Las cabeceras se toman del esquema compartido para que coincidan con las
    columnas que declara el TMDL del scaffold (antes el CSV decia 'Anio' y el
    modelo 'Año', asi que la particion no habria encontrado la columna).
    """
    cabeceras = [c for c, _t in esquema_csv(DOMINIOS["generico"])["Calendario"]]
    filas = []
    for d in rango_dias(desde, hasta):
        trimestre = (d.month - 1) // 3 + 1
        es_habil = "Si" if d.weekday() < 5 else "No"  # lunes=0 ... viernes=4
        filas.append([
            d.isoformat(), d.year, MESES_ES[d.month], d.month,
            "T{}".format(trimestre), es_habil,
        ])
    return cabeceras, filas


def generar_dim1(dom):
    tabla, filas_dom = dom["dim1"]
    cabeceras = ["ID " + tabla, tabla]
    filas = [[i, nombre] for i, nombre in filas_dom]
    return cabeceras, filas


def generar_dim2(dom):
    tabla, col_grupo, filas_dom = dom["dim2"]
    cabeceras = ["ID " + tabla, tabla, col_grupo]
    filas = [[i, nombre, grupo] for i, nombre, grupo in filas_dom]
    return cabeceras, filas


def generar_indicador(dom):
    """
    Dimension Indicador: ID Indicador, Indicador, Tipo, Formato.

    NO es opcional. El hecho es alto (una fila por indicador), asi que sin esta
    tabla la clave `ID Indicador` no apunta a nada y cualquier medida suma
    porcentajes junto con importes absolutos. Las filas se derivan del catalogo
    del dominio, de modo que jamas se desincronicen del hecho.
    """
    cabeceras = ["ID " + TABLA_INDICADOR, TABLA_INDICADOR, "Tipo", "Formato"]
    return cabeceras, filas_indicador(dom)


def generar_hecho(dom, desde, hasta, limite, rnd):
    """
    Hecho con patron Num/Den. Grain: una fila por indicador / dim1 / dim2 / mes.
    Columnas: Fecha, ID <dim1>, ID <dim2>, ID Indicador, Num, Den.
    Integridad referencial garantizada: solo usa IDs de las dimensiones.
    """
    dim1_tabla = dom["dim1"][0]
    dim2_tabla = dom["dim2"][0]
    cabeceras = ["Fecha", "ID " + dim1_tabla, "ID " + dim2_tabla,
                 "ID Indicador", "Num", "Den"]
    filas = []
    meses = primer_dia_de_cada_mes(desde, hasta)
    ids_dim1 = [i for i, _ in dom["dim1"][1]]
    ids_dim2 = [i for i, _, _ in dom["dim2"][2]]
    pct = dom["pct"]

    for mes in meses:
        for d1 in ids_dim1:
            for d2 in ids_dim2:
                for ind_id, _, (num_lo, num_hi), (den_lo, den_hi) in dom["indicadores"]:
                    den = rnd.randint(den_lo, den_hi)
                    num = rnd.randint(num_lo, num_hi)
                    # Indicadores tipo porcentaje: el num no debe pasar al den.
                    if ind_id in pct and num > den:
                        num = den
                    filas.append([mes.isoformat(), d1, d2, ind_id, num, den])

    if limite is not None and limite >= 0:
        filas = filas[:limite]
    return cabeceras, filas


# --------------------------------------------------------------------------- #
# Generador del codigo Power Query M (generico, por tabla)
# --------------------------------------------------------------------------- #

def _bloque_m(tabla, columnas, ruta_m, filtro=None, nota_fecha=False):
    """
    Construye un bloque `let ... in` para una tabla:
      - variante SharePoint comentada
      - lectura CSV con Csv.Document/File.Contents
      - promocion de encabezados y tipado
      - filtro opcional (p. ej. quitar Den nulo/0 en el hecho)
    'columnas' es una lista de (nombre, tipo_m).
    """
    tipos = ",\n".join(
        '        {{"{}", {}}}'.format(col, tipo) for col, tipo in columnas)
    nota = ""
    if nota_fecha:
        nota = (
            "// IMPORTANTE (modelo de datos):\n"
            "//   - Marca esta tabla como \"Tabla de fecha\" usando [Fecha].\n"
            "//   - Apaga Auto date/time: Archivo > Opciones > Carga de datos.\n")
    paso_final = '#"Tipo cambiado"'
    paso_filtro = ""
    if filtro:
        paso_filtro = (
            ',\n    // Filas filtradas: ' + filtro["nota"] + '\n'
            '    #"Filas filtradas" = Table.SelectRows(#"Tipo cambiado", '
            + filtro["expr"] + ')')
        paso_final = '#"Filas filtradas"'
    return '''// ---------------------------------------------------------------------------
// TABLA: {tabla}
// ---------------------------------------------------------------------------
{nota}let
    // --- Variante SharePoint (comentada): descomenta al conectar la fuente real ---
    // url_archivo = "https://<tu-sitio>.sharepoint.com/.../{tabla}.xlsx",
    // Origen = Excel.Workbook(Web.Contents(url_archivo), null, true),
    // Hoja = Origen{{[Item="{tabla}",Kind="Sheet"]}}[Data],
    // EncabezadosPromovidos = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),

    // --- Fuente CSV de ejemplo ---
    Origen = Csv.Document(
        File.Contents(RutaBase & "\\{tabla}.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    EncabezadosPromovidos = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(EncabezadosPromovidos, {{
{tipos}
    }}){paso_filtro}
in
    {paso_final}
'''.format(tabla=tabla, nota=nota, tipos=tipos,
           paso_filtro=paso_filtro, paso_final=paso_final)


def generar_codigo_m(dom, ruta_base):
    """Texto .m con una seccion por tabla, derivado de la config del dominio."""
    ruta_m = ruta_base.replace("\\", "\\\\")
    dim1_tabla = dom["dim1"][0]
    dim2_tabla, col_grupo = dom["dim2"][0], dom["dim2"][1]
    hecho = dom["hecho"]

    cabecera = '''// ===========================================================================
// modelo-ejemplo.m  —  Power Query M para un MVP de modelo estrella
//
// COMO USARLO:
//   1) En Power BI Desktop: Inicio > Transformar datos > Editor avanzado.
//   2) Crea una consulta en blanco POR CADA tabla y pega su bloque.
//      (Cada bloque empieza en "let" y termina en "in <Paso>".)
//   3) Ajusta RutaBase si moviste los CSV.
//
// Convencion: nombres de negocio con espacios, sin prefijos dim_/fact_.
// Tablas: Calendario, {dim1}, {dim2}, Indicador, {hecho} (el hecho).
//
// La tabla Indicador NO es opcional: el hecho guarda una fila por indicador,
// asi que sin ella las medidas suman % junto con importes absolutos.
//
// La variante SharePoint (Excel.Workbook(Web.Contents(...))) esta INCLUIDA
// COMENTADA al inicio de cada bloque para que la actives cuando migres.
//
// ANTES DE PEGAR: crea una consulta/parametro llamado RutaBase con el valor de
// abajo (Inicio > Administrar parametros, o una consulta en blanco
//   RutaBase = "..."  ). Todos los bloques la referencian.
//   RutaBase = "{ruta}"
// ===========================================================================


'''.format(dim1=dim1_tabla, dim2=dim2_tabla, hecho=hecho, ruta=ruta_m)

    # Las columnas y tipos salen del esquema compartido (dominios.esquema_csv),
    # asi el .m, los CSV y el TMDL declaran exactamente lo mismo.
    esq = esquema_csv(dom)
    bloques = [
        _bloque_m("Calendario", esq["Calendario"], ruta_m, nota_fecha=True),
        _bloque_m(dim1_tabla, esq[dim1_tabla], ruta_m),
        _bloque_m(dim2_tabla, esq[dim2_tabla], ruta_m),
        _bloque_m(TABLA_INDICADOR, esq[TABLA_INDICADOR], ruta_m),
        _bloque_m(hecho, esq[hecho], ruta_m, filtro={
            "nota": "descarta registros sin denominador (evita dividir por 0).",
            "expr": "each [Den] <> null and [Den] > 0",
        }),
    ]
    return cabecera + "\n\n".join(bloques)


# --------------------------------------------------------------------------- #
# Validacion de integridad referencial (post-generacion)
# --------------------------------------------------------------------------- #

def validar_integridad(dom, filas_hecho):
    """Verifica que toda clave del hecho exista en las dimensiones."""
    dim1_ok = {i for i, _ in dom["dim1"][1]}
    dim2_ok = {i for i, _, _ in dom["dim2"][2]}
    ind_ok = {i for i, _, _, _ in dom["indicadores"]}
    dim1_tabla, dim2_tabla = dom["dim1"][0], dom["dim2"][0]
    errores = []
    # filas_hecho[i] = [Fecha, ID dim1, ID dim2, ID Indicador, Num, Den]
    for i, fila in enumerate(filas_hecho):
        if fila[1] not in dim1_ok:
            errores.append("Fila {}: ID {} {} no existe".format(i, dim1_tabla, fila[1]))
        if fila[2] not in dim2_ok:
            errores.append("Fila {}: ID {} {} no existe".format(i, dim2_tabla, fila[2]))
        if fila[3] not in ind_ok:
            errores.append("Fila {}: ID Indicador {} no existe".format(i, fila[3]))
    return errores


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Genera CSV de ejemplo + codigo Power Query M (modelo estrella, multi-dominio)."
    )
    parser.add_argument("--dominio", default="generico", choices=sorted(DOMINIOS),
                        help="Dominio de los datos de ejemplo (default: generico)")
    parser.add_argument("--salida", default="./datos-ejemplo",
                        help="Carpeta de salida (default: ./datos-ejemplo)")
    parser.add_argument("--desde", default="2024-01-01",
                        help="Fecha inicial AAAA-MM-DD (default: 2024-01-01)")
    parser.add_argument("--hasta", default=None,
                        help="Fecha final AAAA-MM-DD (default: hoy)")
    parser.add_argument("--filas", type=int, default=None,
                        help="Limite opcional de filas del hecho")
    parser.add_argument("--ruta-base", dest="ruta_base", default=None,
                        help="Ruta base para los File.Contents del .m (default: ruta de --salida)")
    args = parser.parse_args()

    dom = DOMINIOS[args.dominio]

    # Fechas
    try:
        desde = parse_fecha(args.desde)
        hasta = parse_fecha(args.hasta) if args.hasta else dt.date.today()
    except ValueError:
        parser.error("Fechas invalidas. Usa el formato AAAA-MM-DD.")
    if hasta < desde:
        parser.error("--hasta no puede ser anterior a --desde.")

    # Carpeta de salida
    salida = os.path.abspath(args.salida)
    os.makedirs(salida, exist_ok=True)

    # Semilla fija -> reproducible
    rnd = random.Random(42)

    # Nombres de tabla del dominio
    dim1_tabla = dom["dim1"][0]
    dim2_tabla = dom["dim2"][0]
    hecho_tabla = dom["hecho"]

    # Generar tablas
    cal_cab, cal_filas = generar_calendario(desde, hasta)
    dim1_cab, dim1_filas = generar_dim1(dom)
    dim2_cab, dim2_filas = generar_dim2(dom)
    ind_cab, ind_filas = generar_indicador(dom)
    hecho_cab, hecho_filas = generar_hecho(dom, desde, hasta, args.filas, rnd)

    # Validar integridad referencial ANTES de escribir
    errores = validar_integridad(dom, hecho_filas)
    if errores:
        print("ERROR de integridad referencial:")
        for e in errores[:10]:
            print("  - " + e)
        raise SystemExit(1)

    # Escribir CSV (nombre de archivo = nombre de tabla)
    conteos = {}
    conteos["Calendario"] = escribir_csv(
        os.path.join(salida, "Calendario.csv"), cal_cab, cal_filas)
    conteos[dim1_tabla] = escribir_csv(
        os.path.join(salida, dim1_tabla + ".csv"), dim1_cab, dim1_filas)
    conteos[dim2_tabla] = escribir_csv(
        os.path.join(salida, dim2_tabla + ".csv"), dim2_cab, dim2_filas)
    conteos[TABLA_INDICADOR] = escribir_csv(
        os.path.join(salida, TABLA_INDICADOR + ".csv"), ind_cab, ind_filas)
    conteos[hecho_tabla] = escribir_csv(
        os.path.join(salida, hecho_tabla + ".csv"), hecho_cab, hecho_filas)

    # Escribir el .m — sin --ruta-base se usa un PLACEHOLDER, no la ruta local:
    # una ruta absoluta con tu usuario dentro de un archivo versionable es fuga de datos.
    ruta_base_m = args.ruta_base if args.ruta_base else "C:\\CAMBIA-ESTA-RUTA\\datos-ejemplo"
    ruta_m = os.path.join(salida, "modelo-ejemplo.m")
    with open(ruta_m, "w", encoding="utf-8", newline="") as f:
        f.write(generar_codigo_m(dom, ruta_base_m))
    if not args.ruta_base:
        print("NOTA: en modelo-ejemplo.m la RutaBase es un placeholder; en tu maquina")
        print("      apunta a: {}".format(salida))

    # Resumen
    print("=" * 70)
    print("Datos de ejemplo generados  |  dominio: {}".format(args.dominio))
    print(dom["desc"])
    print("=" * 70)
    print("Carpeta de salida : {}".format(salida))
    print("Rango de fechas   : {} a {}".format(desde.isoformat(), hasta.isoformat()))
    print("")
    print("Archivos creados (filas por tabla):")
    print("  {:<26}: {:>7} filas  (dimension fecha)".format("Calendario.csv", conteos["Calendario"]))
    print("  {:<26}: {:>7} filas  (dimension)".format(dim1_tabla + ".csv", conteos[dim1_tabla]))
    print("  {:<26}: {:>7} filas  (dimension)".format(dim2_tabla + ".csv", conteos[dim2_tabla]))
    print("  {:<26}: {:>7} filas  (dimension de indicadores)".format(
        TABLA_INDICADOR + ".csv", conteos[TABLA_INDICADOR]))
    print("  {:<26}: {:>7} filas  (HECHO Num/Den)".format(hecho_tabla + ".csv", conteos[hecho_tabla]))
    print("  {:<26}: codigo Power Query M (5 tablas)".format("modelo-ejemplo.m"))
    print("")
    print("Integridad referencial: OK (todas las claves del hecho existen,")
    print("incluida ID {} contra su dimension).".format(TABLA_INDICADOR))
    print("")
    print("Siguiente: si generaste este proyecto con init_proyecto.py, el .pbip ya")
    print("lee estos CSV. Si vas a conectarlos a mano, pega los bloques de")
    print("'modelo-ejemplo.m' en el Editor avanzado y ajusta RutaBase.")
    print("=" * 70)


if __name__ == "__main__":
    main()
