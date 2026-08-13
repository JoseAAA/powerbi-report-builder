#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_proyecto.py — Bootstrap de un proyecto de dashboard Power BI.

Arma, en UN comando, un proyecto que **abre con datos reales**: genera el tema,
los datos de ejemplo, y un .pbip cuyas particiones LEEN esos datos. Abres el
.pbip, refrescas y ves tus filas. Si corriges un CSV, refrescas y el reporte
cambia — ese es el bucle de mockup rapido.

Estructura generada
-------------------
  mi-reporte/
  ├── Mi Reporte.pbip                  <- el artefacto, en la RAIZ
  ├── Mi Reporte.SemanticModel/        <- modelo (TMDL)
  ├── Mi Reporte.Report/               <- reporte (PBIR)
  ├── datos/                           <- CSV que el modelo lee de verdad
  │   └── modelo-ejemplo.m             <- el mismo M, por si conectas a mano
  ├── docs/                            <- el PROCESO, no el producto
  │   ├── theme.json  marca.json
  │   ├── descubrimiento.md  kpis.md
  └── .gitignore

Por que el .pbip va en la raiz: es lo que espera **Fabric Git Integration**
(los items del workspace se mapean a carpetas del repo). Antes el proyecto
quedaba enterrado en `06-mvp/<Nombre>/` detras de seis carpetas numeradas —
dos de ellas vacias — que eran las fases del framework filtrandose al
entregable del cliente. Las fases son metodologia, no estructura de proyecto:
ahora sus documentos viven en `docs/`.

Sirve para los dos caminos de publicacion:
  - CON Git: `git init` + push a main -> Fabric Git Integration -> Service.
  - SIN Git: abrir el .pbip en Desktop y Publicar. La estructura es la misma.

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
  --salida     carpeta donde crear el proyecto (default: actual).
  --aqui       monta el proyecto EN --salida, sin crear la subcarpeta <nombre>.
               Para cuando ya estas dentro de la carpeta del proyecto.
  --cultura    culture del modelo y locale del reporte (default: es-ES).
  --sin-datos  genera el .pbip con datos inline en vez de leer los CSV.

REGLA: hay que elegir UNO de --marca / --tema / --sin-marca. Sin eleccion el
script falla con instrucciones: los colores de la empresa NUNCA se ignoran en
silencio.

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

# .gitignore del proyecto del usuario. `.pbi/` es cache local de Power BI
# Desktop (cache.abf pesa cientos de MB y localSettings.json causa conflictos).
GITIGNORE = """# Power BI Desktop — cache y settings locales (nunca se versionan)
**/.pbi/

# Sistema operativo
.DS_Store
Thumbs.db
"""

# Lo primero que necesita saber quien abra el proyecto. El formato PBIR es el
# que permite versionar pagina por pagina, y en Power BI Desktop sigue detras
# de una casilla de vista previa: sin activarla, Desktop guarda en el formato
# antiguo (report.json monolitico) y se pierde el diff por visual.
LEEME = """# {nombre}

Proyecto Power BI en formato PBIP (modelo TMDL + reporte PBIR), versionable.

## Antes de abrirlo: activa PBIR en Power BI Desktop

Una vez por equipo:

1. **Archivo > Opciones y configuracion > Opciones > Caracteristicas en vista previa**
2. Marca **«Almacenar informes con el formato de metadatos mejorado (PBIR)»**
   (en ingles: *Store reports using enhanced metadata format (PBIR)*)
3. Reinicia Power BI Desktop.

Sin esa casilla, al guardar se pierde la carpeta `definition/` (una carpeta por
pagina y por visual) y el reporte vuelve a un unico `report.json`, que no se
puede revisar en un diff. Fuente: Microsoft Learn — *Power BI Desktop project
report folder* (https://learn.microsoft.com/power-bi/developer/projects/projects-report).

## Como abrirlo

1. Abre `{nombre}.pbip` con Power BI Desktop.
2. **Inicio > Actualizar.** El modelo lee los CSV de `datos/`.
3. Si moviste el proyecto, corrige la ruta en
   **Inicio > Transformar datos > Administrar parametros > RutaBase**.

## El bucle de mockup rapido

Los datos de `datos/` son de ejemplo y estan para que los corrijas:
edita un CSV, vuelve a Power BI y pulsa **Actualizar**. El reporte refleja el
cambio sin tocar el modelo. Cuando la forma de los datos ya te sirva, cambia la
consulta de cada tabla por la fuente real (SQL, SharePoint, Fabric) — las
medidas y los visuales siguen funcionando.

## Publicar

- **Con Git:** `git init`, commit y push a `main`. Conecta el workspace con
  **Fabric Git Integration**; el `.pbip` esta en la raiz, que es donde lo busca.
- **Sin Git:** abre el `.pbip` en Desktop y usa **Publicar**. No necesitas
  ningun sistema de versiones para empezar.

## Estructura

| Carpeta | Que es |
|---|---|
| `{nombre}.pbip` | punto de entrada del proyecto |
| `{nombre}.SemanticModel/` | modelo: tablas, relaciones, medidas DAX (TMDL) |
| `{nombre}.Report/` | reporte: paginas y visuales (PBIR) |
| `datos/` | CSV de ejemplo que el modelo lee, y el codigo M equivalente |
| `docs/` | tema, marca y documentos del proceso (descubrimiento, KPIs) |
"""


def _slug(nombre):
    s = nombre.strip().lower().replace(" ", "-")
    return "".join(c for c in s if c.isalnum() or c in "-_")


def _run(args):
    """Ejecuta un script hermano con el mismo interprete; devuelve True si OK."""
    r = subprocess.run([sys.executable] + args)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(
        description="Bootstrap de un proyecto Power BI (.pbip en la raiz, con datos cableados).")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--dominio", default="generico",
                    choices=["ventas", "rrhh", "finanzas", "salud", "generico"])
    ap.add_argument("--marca", help="ruta a un archivo de marca JSON (genera el tema)")
    ap.add_argument("--tema", help="ruta a un theme.json ya generado (se usa tal cual)")
    ap.add_argument("--sin-marca", dest="sin_marca", action="store_true",
                    help="acepta explicitamente un tema neutro provisional")
    ap.add_argument("--salida", default="./")
    ap.add_argument("--aqui", action="store_true", help=(
        "crea el proyecto EN --salida directamente, sin la subcarpeta <nombre>. "
        "Usalo cuando ya estas parado en la carpeta del proyecto."))
    ap.add_argument("--cultura", default="es-ES",
                    help="culture del modelo y locale del reporte (default: es-ES)")
    ap.add_argument("--sin-datos", dest="sin_datos", action="store_true",
                    help="genera el .pbip con datos inline en vez de leer los CSV")
    args = ap.parse_args()

    if not (args.marca or args.tema or args.sin_marca):
        ap.error(
            "elige el tema del reporte: --marca <empresa>.json (recomendado), "
            "--tema theme.json, o --sin-marca para aceptar un neutro provisional. "
            "Los colores de tu empresa no se ignoran en silencio.")
    if sum(bool(x) for x in (args.marca, args.tema, args.sin_marca)) > 1:
        ap.error("usa solo UNO de --marca / --tema / --sin-marca.")

    # Por defecto se crea una subcarpeta con el slug del nombre. Con --aqui el
    # proyecto se monta DIRECTAMENTE en --salida: es lo que se espera cuando el
    # usuario ya creo la carpeta del proyecto y esta parado dentro de ella.
    base = (os.path.abspath(args.salida) if args.aqui
            else os.path.abspath(os.path.join(args.salida, _slug(args.nombre))))
    docs = os.path.join(base, "docs")
    datos = os.path.join(base, "datos")
    for d in (base, docs, datos):
        os.makedirs(d, exist_ok=True)

    # --- tema (en docs/: es insumo del proceso, no del artefacto) ---
    theme = os.path.join(docs, "theme.json")
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

    # --- PLAN del reporte, en lenguaje de negocio ---
    # Se escribe SIEMPRE, y antes que nada, para que el usuario pueda validar la
    # historia antes de mirar un solo visual. Patron propuesta -> aprobacion de
    # OpenSpec: revisar media pagina cuesta un minuto, rehacer el reporte una tarde.
    ok_plan = _run([os.path.join(SCRIPTS, "plan_reporte.py"),
                    "--nombre", args.nombre, "--dominio", args.dominio,
                    "--salida", os.path.join(docs, "plan.md")])

    # plantillas del proceso, para que el usuario las complete
    for src, destino in [
        (os.path.join("marca", "_plantilla-marca.json"), "marca.json"),
        ("plantilla-descubrimiento.md", "descubrimiento.md"),
        ("ficha-kpi.md", "kpis.md"),
    ]:
        ruta = os.path.join(ASSETS, src)
        if os.path.exists(ruta):
            shutil.copy(ruta, os.path.join(docs, destino))

    # --- datos de ejemplo ---
    # --ruta-base apunta a la carpeta real: el .m que se entrega junto a los CSV
    # debe poder pegarse sin editar nada.
    ok_datos = _run([os.path.join(SCRIPTS, "generar_datos_ejemplo.py"),
                     "--dominio", args.dominio, "--salida", datos,
                     "--ruta-base", datos])

    # --- .pbip en la RAIZ, con las particiones leyendo los CSV ---
    scaffold = [os.path.join(SCRIPTS, "scaffold_pbip.py"),
                "--nombre", args.nombre, "--dominio", args.dominio,
                "--salida", base, "--en-raiz", "--cultura", args.cultura]
    if os.path.exists(theme):
        scaffold += ["--tema", theme]
    if not args.sin_datos and ok_datos:
        scaffold += ["--datos", datos]
    ok_pbip = _run(scaffold)

    # --- archivos de proyecto ---
    with open(os.path.join(base, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(GITIGNORE)
    with open(os.path.join(base, "LEEME.md"), "w", encoding="utf-8") as f:
        f.write(LEEME.format(nombre=args.nombre))

    origen_tema = ("marca" if args.marca else
                   "theme.json" if args.tema else "NEUTRO provisional (--sin-marca)")
    modo = "inline (--sin-datos)" if args.sin_datos else "lee los CSV de datos/"

    print("=" * 70)
    print(f"Proyecto listo: {base}")
    print(f"  dominio: {args.dominio} | tema: {origen_tema} | cultura: {args.cultura}")
    print(f"  plan docs/plan.md    : {'OK' if ok_plan else 'ERROR'}  <- LEELO PRIMERO")
    print(f"  tema docs/theme.json : {'OK' if ok_tema else 'ERROR'}")
    print(f"  datos de ejemplo     : {'OK' if ok_datos else 'ERROR'}")
    print(f"  .pbip (en la raiz)   : {'OK' if ok_pbip else 'ERROR'}  [{modo}]")
    print("")
    print("ANTES DE ABRIRLO — una vez por equipo, en Power BI Desktop:")
    print("  Archivo > Opciones > Caracteristicas en vista previa >")
    print("  marca «Almacenar informes con el formato de metadatos mejorado (PBIR)»")
    print("  y reinicia. Sin eso, al guardar se pierde el detalle por visual.")
    print("")
    print(f'Luego: abre "{args.nombre}.pbip" y pulsa Actualizar. Veras los datos')
    print("de datos/. Corrige un CSV y vuelve a Actualizar: ese es el bucle de")
    print("mockup rapido. Detalles y como publicar: LEEME.md")
    print("=" * 70)
    return 0 if (ok_plan and ok_tema and ok_datos and ok_pbip) else 1


if __name__ == "__main__":
    sys.exit(main())
