#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_proyecto.py — Bootstrap de un proyecto de dashboard Power BI.

Arma, en UN comando, la base de un trabajo nuevo (sirve para multi-empresa: cada
proyecto/clon su propia carpeta), reutilizando los demas scripts del plugin:
genera el tema, los datos de ejemplo y el .pbip base, y deja la estructura de
fases lista para llenar.

Estructura generada (convencion del framework):
  proyecto-<nombre>/
  ├── 01-marca/          theme.json + copia de _plantilla-marca.json
  ├── 02-descubrimiento/ plantilla-descubrimiento.md
  ├── 03-kpis/           ficha-kpi.md
  ├── 04-modelo/         (vacio, listo)
  ├── 05-diseno/         (vacio, listo)
  └── 06-mvp/            <Reporte>.pbip base + datos-ejemplo/*.csv

Uso:
  python init_proyecto.py --nombre "Ventas LATAM" --dominio ventas --marca <empresa>.json
  python init_proyecto.py --nombre "Mi Reporte" --tema theme.json
  python init_proyecto.py --nombre "Mi Reporte" --sin-marca   # neutro, EXPLICITO

Argumentos:
  --nombre     (requerido) nombre del proyecto/reporte.
  --dominio    ventas | rrhh | finanzas | salud | generico (default: generico).
  --marca      ruta a un archivo de marca JSON (genera el tema desde ahi).
  --tema       ruta a un theme.json YA generado (se usa tal cual).
  --sin-marca  acepta EXPLICITAMENTE un tema neutro provisional.
  --salida     carpeta donde crear proyecto-<nombre> (default: actual).

REGLA: hay que elegir UNO de --marca / --tema / --sin-marca. Sin eleccion el
script falla con instrucciones: los colores de la empresa NUNCA se ignoran en
silencio.

Nota Windows: usa una carpeta de salida corta; rutas muy profundas pueden topar
con el limite de 260 caracteres (MAX_PATH).

Solo libreria estandar (subprocess, os, sys, shutil, argparse).
"""
import argparse
import os
import shutil
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(SCRIPTS)          # raiz del plugin/skill
ASSETS = os.path.join(RAIZ, "assets")


def _slug(nombre):
    s = nombre.strip().lower().replace(" ", "-")
    return "".join(c for c in s if c.isalnum() or c in "-_")


def _run(args):
    """Ejecuta un script hermano con el mismo interprete; devuelve True si OK."""
    r = subprocess.run([sys.executable] + args)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(description="Bootstrap de un proyecto Power BI (estructura + tema + .pbip base).")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--dominio", default="generico",
                    choices=["ventas", "rrhh", "finanzas", "salud", "generico"])
    ap.add_argument("--marca", help="ruta a un archivo de marca JSON (genera el tema)")
    ap.add_argument("--tema", help="ruta a un theme.json ya generado (se usa tal cual)")
    ap.add_argument("--sin-marca", dest="sin_marca", action="store_true",
                    help="acepta explicitamente un tema neutro provisional")
    ap.add_argument("--salida", default="./")
    args = ap.parse_args()

    if not (args.marca or args.tema or args.sin_marca):
        ap.error(
            "elige el tema del reporte: --marca <empresa>.json (recomendado), "
            "--tema theme.json, o --sin-marca para aceptar un neutro provisional. "
            "Los colores de tu empresa no se ignoran en silencio.")
    if sum(bool(x) for x in (args.marca, args.tema, args.sin_marca)) > 1:
        ap.error("usa solo UNO de --marca / --tema / --sin-marca.")

    base = os.path.abspath(os.path.join(args.salida, "proyecto-" + _slug(args.nombre)))
    fases = ["01-marca", "02-descubrimiento", "03-kpis", "04-modelo", "05-diseno", "06-mvp"]
    for fase in fases:
        os.makedirs(os.path.join(base, fase), exist_ok=True)

    # --- 01-marca: tema ---
    theme = os.path.join(base, "01-marca", "theme.json")
    if args.marca:
        ok_tema = _run([os.path.join(SCRIPTS, "generar_theme.py"),
                        "--marca", args.marca, "--salida", theme])
    elif args.tema:
        try:
            shutil.copy(args.tema, theme)
            ok_tema = True
        except OSError as e:
            print(f"ERROR copiando --tema: {e}")
            ok_tema = False
    else:  # --sin-marca (eleccion explicita del usuario)
        ok_tema = _run([os.path.join(SCRIPTS, "generar_theme.py"),
                        "--nombre", "Tema neutro provisional", "--primario", "#2C3E50",
                        "--salida", theme])
    # plantilla de marca para que el usuario la complete
    plantilla = os.path.join(ASSETS, "marca", "_plantilla-marca.json")
    if os.path.exists(plantilla):
        shutil.copy(plantilla, os.path.join(base, "01-marca", "_plantilla-marca.json"))

    # --- 02-descubrimiento / 03-kpis: plantillas ---
    for src, fase in [("plantilla-descubrimiento.md", "02-descubrimiento"),
                      ("ficha-kpi.md", "03-kpis")]:
        ruta = os.path.join(ASSETS, src)
        if os.path.exists(ruta):
            shutil.copy(ruta, os.path.join(base, fase, src))

    # --- 06-mvp: datos de ejemplo + .pbip base ---
    mvp = os.path.join(base, "06-mvp")
    ok_datos = _run([os.path.join(SCRIPTS, "generar_datos_ejemplo.py"),
                     "--dominio", args.dominio,
                     "--salida", os.path.join(mvp, "datos-ejemplo")])
    scaffold_args = [os.path.join(SCRIPTS, "scaffold_pbip.py"),
                     "--nombre", args.nombre, "--dominio", args.dominio,
                     "--salida", mvp]
    if os.path.exists(theme):
        scaffold_args += ["--tema", theme]
    ok_pbip = _run(scaffold_args)

    print("=" * 70)
    print(f"Proyecto inicializado: {base}")
    origen_tema = "marca" if args.marca else ("theme.json" if args.tema else "NEUTRO provisional (--sin-marca)")
    print(f"  dominio: {args.dominio} | tema: {origen_tema}")
    print(f"  tema 01-marca/theme.json : {'OK' if ok_tema else 'ERROR'}")
    print(f"  datos de ejemplo 06-mvp  : {'OK' if ok_datos else 'ERROR'}")
    print(f"  .pbip base 06-mvp        : {'OK' if ok_pbip else 'ERROR'}")
    print("")
    print("Siguiente: abre el .pbip de 06-mvp en Power BI Desktop, y completa las")
    print("fases 01-05 (marca real, descubrimiento, KPIs, modelo, diseño).")
    print("=" * 70)
    return 0 if (ok_tema and ok_datos and ok_pbip) else 1


if __name__ == "__main__":
    sys.exit(main())
