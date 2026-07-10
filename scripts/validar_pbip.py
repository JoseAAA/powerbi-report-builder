#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_pbip.py — Validador del lado REPORTE (PBIR) de un proyecto Power BI.

Complementa a validar_modelo.py (que revisa el modelo/TMDL). Este revisa los
JSON del reporte para atrapar ANTES de abrir en Power BI Desktop los errores que
corrompen el informe ("El informe tiene problemas que no se pudieron resolver").

Uso:
  python validar_pbip.py <ruta al proyecto, a la carpeta .Report o a definition/>

Reglas (severidad [ALTA] bloquea, exit 1):
  P1  [ALTA]  Algún .json/.pbir no parsea (JSON inválido).
  P2  [ALTA]  themeCollection.customTheme/baseTheme sin 'name'/'type'/'reportVersionAtImport'
              (ThemeMetadata requiere los tres; omitir reportVersionAtImport corrompe).
  P3  [ALTA]  'reportVersionAtImport' sin las 3 subversiones visual/page/report.
  P4  [ALTA]  pages.json: 'activePageName' no está en 'pageOrder' (o pageOrder vacío).
  P5  [MEDIA] Un visual.json/page.json sin '$schema' o sin 'name'.
  P6  [MEDIA] definition.pbir sin 'datasetReference'.
  P7  [ALTA]  Tema custom NO cableado: hay un theme .json en RegisteredResources
              pero report.json no lo referencia (los colores NO se aplican), o al
              reves: customTheme referenciado pero el archivo del recurso no existe.

Solo librería estándar.
"""
import json
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _localizar_report(raiz: Path):
    """Devuelve la carpeta .Report (con definition/) a partir de una ruta flexible."""
    if (raiz / "definition" / "report.json").exists():
        return raiz
    # ruta = carpeta definition/
    if raiz.name == "definition" and (raiz / "report.json").exists():
        return raiz.parent
    # ruta = proyecto: busca un *.Report con definition/report.json
    for p in raiz.rglob("definition/report.json"):
        return p.parent.parent
    return None


def _cargar(ruta, hallazgos):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        hallazgos.append(("ALTA", "P1", f"JSON inválido: {ruta.name} ({e})"))
    except OSError as e:
        hallazgos.append(("ALTA", "P1", f"No se pudo leer {ruta.name} ({e})"))
    return None


def _validar_theme_meta(tipo, meta, hallazgos):
    """customTheme/baseTheme deben tener name + type + reportVersionAtImport{3}."""
    for req in ("name", "type", "reportVersionAtImport"):
        if req not in meta:
            hallazgos.append(("ALTA", "P2",
                f"themeCollection.{tipo} sin '{req}' (requerido por ThemeMetadata)"))
    rva = meta.get("reportVersionAtImport")
    if isinstance(rva, dict):
        for sub in ("visual", "page", "report"):
            if sub not in rva:
                hallazgos.append(("ALTA", "P3",
                    f"themeCollection.{tipo}.reportVersionAtImport sin '{sub}'"))


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
    entrada = Path(_ruta_io(sys.argv[1]))
    if not entrada.exists():
        print(f"No existe la ruta: {sys.argv[1]}")
        return 2
    report = _localizar_report(entrada)
    if not report:
        print("No se encontró un reporte PBIR (definition/report.json) bajo esa ruta.")
        return 2

    definition = report / "definition"
    hallazgos = []
    report_obj = None
    jsons = sorted(report.rglob("*.json")) + sorted(report.glob("*.pbir"))
    n_ok = 0

    for f in jsons:
        # ignora cache local
        if ".pbi" in f.parts:
            continue
        obj = _cargar(f, hallazgos)
        if obj is None:
            continue
        n_ok += 1
        nombre = f.name

        # $schema recomendado en archivos PBIR
        if nombre in ("report.json", "pages.json", "page.json", "visual.json") and "$schema" not in obj:
            hallazgos.append(("MEDIA", "P5", f"{nombre} sin '$schema' ({f.parent.name})"))

        if nombre == "report.json":
            report_obj = obj
            tc = obj.get("themeCollection", {})
            for tipo in ("customTheme", "baseTheme"):
                if tipo in tc:
                    _validar_theme_meta(tipo, tc[tipo], hallazgos)

        elif nombre == "pages.json":
            orden = obj.get("pageOrder", [])
            activa = obj.get("activePageName")
            if not orden:
                hallazgos.append(("ALTA", "P4", "pages.json con 'pageOrder' vacío"))
            elif activa not in orden:
                hallazgos.append(("ALTA", "P4",
                    f"pages.json: activePageName '{activa}' no está en pageOrder"))

        elif nombre in ("page.json", "visual.json"):
            if "name" not in obj:
                hallazgos.append(("MEDIA", "P5", f"{nombre} sin 'name' ({f.parent.name})"))

        elif f.suffix == ".pbir":
            if "datasetReference" not in obj:
                hallazgos.append(("MEDIA", "P6", "definition.pbir sin 'datasetReference'"))

    # P7 — cableado del tema custom (report.json <-> RegisteredResources)
    rr = report / "StaticResources" / "RegisteredResources"
    temas_en_disco = sorted(rr.glob("*.json")) if rr.exists() else []
    if report_obj is not None:
        ct = report_obj.get("themeCollection", {}).get("customTheme")
        items = [i for p in report_obj.get("resourcePackages", [])
                 for i in p.get("items", []) if i.get("type") == "CustomTheme"]
        if ct:
            rutas_ok = any((rr / i.get("path", "")).exists() for i in items)
            if not rutas_ok:
                hallazgos.append(("ALTA", "P7",
                    "customTheme referenciado en report.json pero el archivo del "
                    "recurso no existe en StaticResources/RegisteredResources"))
        elif temas_en_disco:
            hallazgos.append(("ALTA", "P7",
                f"Hay un tema en RegisteredResources ({temas_en_disco[0].name}) pero "
                "report.json NO lo referencia (themeCollection.customTheme): los "
                "colores de la marca NO se estan aplicando"))

    print(f"Reporte: {report.name}  |  Archivos JSON/PBIR: {n_ok}")
    if not hallazgos:
        print("OK  Sin hallazgos en el reporte (P1-P7).")
        return 0
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    for sev, regla, msg in sorted(hallazgos, key=lambda h: orden[h[0]]):
        print(f"[{sev}] {regla}: {msg}")
    altas = sum(1 for h in hallazgos if h[0] == "ALTA")
    print(f"\nTotal: {len(hallazgos)} hallazgos ({altas} de severidad ALTA)")
    return 1 if altas else 0


if __name__ == "__main__":
    sys.exit(main())
