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
  P8  [ALTA]  Nombre del tema inconsistente: el `name` interno del theme.json,
              `customTheme.name` y el `name`/`path` del item de resourcePackages
              deben ser IDENTICOS y terminar en ".json". Sin la extension, Desktop
              abre bien pero el reporte PUBLICADO EN EL SERVICE aplica mal el tema.
              Equivale a PBIR_THEME_NAME_MISSING_JSON_EXT y
              PBIR_THEME_FILE_NAME_MISMATCH del validador oficial de Microsoft.
  P9  [ALTA]  Visual sin altText (accesibilidad). Es la regla de MAYOR severidad
              del catalogo de visualizacion: sin alt, un lector de pantalla solo
              anuncia el tipo de visual y el insight se pierde. Limite 250 chars.
              Exentos los decorativos (shape, image, actionButton).

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

        if nombre == "visual.json":
            # P9 — accesibilidad: alt text en todo visual que transmita informacion.
            # Es la regla de MAYOR severidad del catalogo de visualizacion
            # (PBI-A11Y-01): sin alt, un lector de pantalla solo anuncia el tipo de
            # visual y el insight se pierde. Limite duro de 250 caracteres.
            # learn.microsoft.com/power-bi/create-reports/desktop-accessibility-creating-reports
            v = obj.get("visual", {})
            tipo = v.get("visualType", "?")
            general = v.get("visualContainerObjects", {}).get("general", [])
            alt = None
            for bloque in general:
                cand = bloque.get("properties", {}).get("altText")
                if isinstance(cand, dict):
                    alt = (cand.get("expr", {}).get("Literal", {}).get("Value") or "")
                    alt = alt.strip("'")
                    break
            # Los puramente decorativos (formas e imagenes sin dato) estan exentos.
            decorativos = {"shape", "image", "actionButton", "basicShape"}
            if tipo in decorativos:
                pass
            elif not alt:
                hallazgos.append(("ALTA", "P9",
                    f"visual '{tipo}' sin altText ({f.parent.name}): un lector de "
                    "pantalla solo anunciara el tipo de visual y el insight se "
                    "pierde. Describe el hallazgo, no el aspecto"))
            elif len(alt) > 250:
                hallazgos.append(("MEDIA", "P9",
                    f"visual '{tipo}': altText de {len(alt)} caracteres; el limite "
                    "duro del campo son 250"))

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

        # P8 — identidad del nombre del tema (4 valores que deben coincidir).
        # Microsoft exige que el `name` interno del theme.json, customTheme.name y
        # el name/path del item de resourcePackages sean IDENTICOS y terminen en
        # ".json". Si falta la extension, Power BI Desktop abre bien pero el reporte
        # PUBLICADO EN EL SERVICE aplica el tema incorrectamente: los colores del
        # usuario se pierden en silencio justo al llegar a produccion. Si el `name`
        # interno no coincide con la referencia, el tema no carga.
        # Equivale a los diagnosticos PBIR_THEME_NAME_MISSING_JSON_EXT y
        # PBIR_THEME_FILE_NAME_MISMATCH del validador oficial de Microsoft
        # (@microsoft/powerbi-report-authoring-cli), comprobados empiricamente.
        if ct:
            ref = ct.get("name", "")
            if not ref.lower().endswith(".json"):
                hallazgos.append(("ALTA", "P8",
                    f'themeCollection.customTheme.name es "{ref}" y le falta la '
                    'extension ".json". Power BI Desktop abre bien, pero el reporte '
                    "publicado en el Service aplica el tema incorrectamente: los "
                    "colores de la marca se pierden al llegar a produccion"))
            for i in items:
                for clave in ("name", "path"):
                    if i.get(clave) != ref:
                        hallazgos.append(("ALTA", "P8",
                            f'resourcePackages item {clave}="{i.get(clave)}" no coincide '
                            f'con customTheme.name="{ref}"; los cuatro valores '
                            "(name interno del tema, customTheme.name, item.name e "
                            "item.path) deben ser identicos"))
            for t in temas_en_disco:
                if t.name != ref:
                    continue
                try:
                    with open(t, encoding="utf-8") as fh:
                        interno = json.load(fh).get("name", "")
                except (OSError, ValueError):
                    continue
                if interno != ref:
                    hallazgos.append(("ALTA", "P8",
                        f'el "name" dentro de {t.name} es "{interno}" pero report.json '
                        f'referencia "{ref}"; si no son identicos el tema no carga'))

    print(f"Reporte: {report.name}  |  Archivos JSON/PBIR: {n_ok}")
    if not hallazgos:
        print("OK  Sin hallazgos en el reporte (P1-P9).")
        return 0
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    for sev, regla, msg in sorted(hallazgos, key=lambda h: orden[h[0]]):
        print(f"[{sev}] {regla}: {msg}")
    altas = sum(1 for h in hallazgos if h[0] == "ALTA")
    print(f"\nTotal: {len(hallazgos)} hallazgos ({altas} de severidad ALTA)")
    return 1 if altas else 0


if __name__ == "__main__":
    sys.exit(main())
