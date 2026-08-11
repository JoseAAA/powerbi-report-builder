#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prueba_rapida.py — Comprueba que todo funciona, en cualquier maquina o sandbox.

Un solo comando que ejecuta el flujo completo y SE AUTOVERIFICA: genera el plan,
crea el proyecto, corre los cuatro validadores, mete fallos a proposito para
comprobar que se detectan, y dice si todo esta bien.

Para que sirve
--------------
- Antes de usar el framework en serio: confirmar que tu entorno esta OK.
- En ChatGPT / Claude.ai / Gemini con sandbox de Python: comprobar que el
  proyecto corre ahi (no necesita internet ni dependencias).
- Como demo: ver en 30 segundos todo lo que hace.

Uso:
  python scripts/prueba_rapida.py
  python scripts/prueba_rapida.py --dominio salud --salida /ruta/donde/dejarlo
  python scripts/prueba_rapida.py --rapida     # omite las pruebas negativas

Exit 0 = todo correcto. Exit 1 = algo fallo (dice que).
Solo libreria estandar; NO necesita internet.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OK, FALLO = "OK  ", "FALLO"
resultados = []


def paso(titulo):
    print("\n" + "─" * 66)
    print(f"  {titulo}")
    print("─" * 66)


def check(nombre, condicion, detalle=""):
    resultados.append((nombre, bool(condicion)))
    marca = OK if condicion else FALLO
    print(f"  [{marca}] {nombre}" + (f"  — {detalle}" if detalle else ""))
    return bool(condicion)


def run(script, *args, silencioso=True):
    """Ejecuta un script hermano. Devuelve (exit_code, stdout)."""
    cmd = [sys.executable, os.path.join(SCRIPTS, script)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if not silencioso:
        print(r.stdout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    ap = argparse.ArgumentParser(description="Prueba de extremo a extremo, autoverificada.")
    ap.add_argument("--dominio", default="ventas",
                    choices=["ventas", "rrhh", "finanzas", "salud", "generico"])
    ap.add_argument("--salida", help="donde dejar el proyecto (default: carpeta temporal)")
    ap.add_argument("--rapida", action="store_true", help="omite las pruebas negativas")
    args = ap.parse_args()

    tmp = args.salida or tempfile.mkdtemp(prefix="pbi-prueba-")
    os.makedirs(tmp, exist_ok=True)
    print("=" * 66)
    print("  PRUEBA RAPIDA — Power BI Report Builder")
    print("=" * 66)
    print(f"  Python  : {sys.version.split()[0]}")
    print(f"  Dominio : {args.dominio}")
    print(f"  Carpeta : {tmp}")

    # ---------------------------------------------------------------- 1
    paso("1. El PLAN se genera antes que nada (lenguaje de negocio)")
    cod, out = run("plan_reporte.py", "--nombre", "Prueba", "--dominio", args.dominio)
    check("el plan se genera", cod == 0)
    check("esta en lenguaje de negocio", "TMDL" not in out and "visualType" not in out,
          "sin TMDL ni visualType en lo que lee el usuario")
    check("dice la historia de la pagina", "Como se lee" in out)
    check("pide decisiones al usuario", "- [ ]" in out,
          f"{out.count('- [ ]')} preguntas abiertas")

    # ---------------------------------------------------------------- 2
    paso("2. Se construye el proyecto")
    proy = os.path.join(tmp, "prueba")
    cod, out = run("init_proyecto.py", "--nombre", "Prueba", "--dominio", args.dominio,
                   "--sin-marca", "--salida", tmp)
    check("bootstrap sin errores", cod == 0)
    check(".pbip en la RAIZ del proyecto", glob.glob(os.path.join(proy, "*.pbip")),
          "es lo que espera Fabric Git Integration")
    check("plan escrito en docs/", os.path.exists(os.path.join(proy, "docs", "plan.md")))
    csvs = glob.glob(os.path.join(proy, "datos", "*.csv"))
    check("datos de ejemplo generados", len(csvs) == 5, f"{len(csvs)} CSV")

    sm = glob.glob(os.path.join(proy, "*.SemanticModel"))
    rp = glob.glob(os.path.join(proy, "*.Report"))
    if not (sm and rp):
        print("\n  No se pudo continuar: falta el modelo o el reporte.")
        return 1
    sm, rp = sm[0], rp[0]

    # ---------------------------------------------------------------- 3
    paso("3. El .pbip LEE los datos (no muestra datos inventados)")
    expr = os.path.join(sm, "definition", "expressions.tmdl")
    check("existe el parametro RutaBase", os.path.exists(expr))
    hecho = [p for p in glob.glob(os.path.join(sm, "definition", "tables", "*.tmdl"))
             if "Csv.Document" in open(p, encoding="utf-8").read()]
    check("las particiones leen los CSV", len(hecho) >= 4, f"{len(hecho)} tablas")
    # filas reales, no seis de relleno
    fact = [c for c in csvs if os.path.basename(c) not in
            ("Calendario.csv", "Indicador.csv")]
    filas = max(sum(1 for _ in open(c, encoding="utf-8-sig")) - 1 for c in fact)
    check("hay datos de verdad", filas > 500, f"{filas} filas en el hecho")

    # ---------------------------------------------------------------- 4
    paso("4. El reporte tiene paginas, visuales y accesibilidad")
    pages = glob.glob(os.path.join(rp, "definition", "pages", "*", "page.json"))
    vis = glob.glob(os.path.join(rp, "definition", "pages", "*", "visuals", "*", "visual.json"))
    check("varias paginas", len(pages) >= 2, f"{len(pages)} paginas")
    check("reporte con contenido", len(vis) >= 10, f"{len(vis)} visuales")
    con_alt = sum(1 for v in vis if "altText" in open(v, encoding="utf-8").read())
    check("TODOS los visuales con altText", con_alt == len(vis),
          f"{con_alt}/{len(vis)} — WCAG, regla de mayor severidad")
    tipos = set()
    for v in vis:
        tipos.add(json.load(open(v, encoding="utf-8"))["visual"]["visualType"])
    check("variedad de visuales", len(tipos) >= 6, ", ".join(sorted(tipos)))
    slicers = sum(1 for v in vis
                  if json.load(open(v, encoding="utf-8"))["visual"]["visualType"] == "slicer")
    check("hay segmentadores", slicers >= 2, f"{slicers} slicers")

    # ---------------------------------------------------------------- 5
    paso("5. Los cuatro validadores")
    for etiqueta, script, ruta in (
            ("modelo (R1-R12 + 26 reglas oficiales)", "validar_modelo.py", sm),
            ("reporte (P1-P9)", "validar_pbip.py", rp),
            ("cableado datos<->modelo (E1-E6)", "verificar_cableado.py", proy),
            ("catalogo: toda regla con fuente", "catalogo_reglas.py", None)):
        cod, out = run(script, *( [ruta] if ruta else [] ))
        check(etiqueta, cod == 0, out.strip().splitlines()[-1][:60] if out.strip() else "")

    # ---------------------------------------------------------------- 6
    if not args.rapida:
        paso("6. Pruebas NEGATIVAS: ¿detecta los fallos de verdad?")
        malo = os.path.join(tmp, "con-fallos")
        shutil.rmtree(malo, ignore_errors=True)
        shutil.copytree(proy, malo)
        sm2 = glob.glob(os.path.join(malo, "*.SemanticModel"))[0]
        rp2 = glob.glob(os.path.join(malo, "*.Report"))[0]

        # a) medida que divide con '/' en vez de DIVIDE
        med = os.path.join(sm2, "definition", "tables", "_ Medidas.tmdl")
        s = open(med, encoding="utf-8").read()
        s = s.replace("DIVIDE ( [Numerador], [Denominador] )",
                      "[Numerador] / [Denominador]", 1)
        open(med, "w", encoding="utf-8").write(s)
        cod, out = run("validar_modelo.py", sm2)
        check("detecta division sin DIVIDE()", cod != 0 or "DIVIDE" in out)

        # b) visual sin texto alternativo
        v = glob.glob(os.path.join(rp2, "definition", "pages", "*", "visuals", "*", "visual.json"))[0]
        d = json.load(open(v, encoding="utf-8"))
        d["visual"].get("visualContainerObjects", {}).pop("general", None)
        json.dump(d, open(v, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        cod, out = run("validar_pbip.py", rp2)
        check("detecta visual sin altText", cod != 0 and "P9" in out)

        # c) datos huerfanos: el .pbip deja de leer los CSV
        huerfano = os.path.join(tmp, "huerfano")
        shutil.rmtree(huerfano, ignore_errors=True)
        os.makedirs(huerfano)
        run("generar_datos_ejemplo.py", "--dominio", args.dominio,
            "--salida", os.path.join(huerfano, "datos"))
        run("scaffold_pbip.py", "--nombre", "Huerfano", "--dominio", args.dominio,
            "--salida", huerfano, "--en-raiz")   # SIN --datos: datos inline
        cod, out = run("verificar_cableado.py", huerfano)
        check("detecta datos huerfanos", cod != 0 and "E3" in out,
              "el .pbip no leeria los CSV que hay al lado")

    # ---------------------------------------------------------------- resumen
    print("\n" + "=" * 66)
    fallos = [n for n, ok in resultados if not ok]
    if not fallos:
        print(f"  TODO CORRECTO — {len(resultados)} comprobaciones pasadas")
        print("=" * 66)
        print(f"\n  Tu proyecto de prueba: {proy}")
        print("  Abre el .pbip en Power BI Desktop y pulsa Actualizar.")
        print("  (Antes: Archivo > Opciones > Caracteristicas en vista previa >")
        print("   marca «Almacenar informes con el formato de metadatos mejorado»)")
        return 0
    print(f"  {len(fallos)} COMPROBACION(ES) FALLIDA(S) de {len(resultados)}:")
    for f in fallos:
        print(f"    - {f}")
    print("=" * 66)
    return 1


if __name__ == "__main__":
    sys.exit(main())
