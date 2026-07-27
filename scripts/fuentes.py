#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fuentes.py — Registro de las FUENTES OFICIALES que sustentan el catalogo.

Cada regla del framework tiene que trazar a documentacion oficial. Este archivo
declara DE DONDE sale esa documentacion, para poder detectar cuando Microsoft la
cambia en vez de esperar a que alguien lo note.

Todos los repos, ramas y rutas de aqui estan CONFIRMADOS con una peticion real a
la API de GitHub (2026-07-26). Tres cosas que no eran lo que parecian:

  - **DAX no vive en `sql-docs` ni en `bi-shared-docs`**: es
    `MicrosoftDocs/query-docs`, ruta `query-languages/dax/`. Lo delata el campo
    `original_content_git_url` de las paginas de Learn. `MicrosoftDocs/dax-docs`
    no existe (404).
  - **`microsoft/Analysis-Services` usa la rama `master`**, no `main`.
  - Los repos `*-pr` de MicrosoftDocs son **privados** (404); los espejos
    publicos son los que estan aqui.

TTL por niveles, no global: hay ~100x de diferencia de cadencia entre
`create-reports` (decenas de commits/mes) y las BPA rules (casi inmovil). Un TTL
unico o revisa de mas o revisa de menos.

Solo datos y funciones puras; sin efectos secundarios al importar.
"""

# Ruta del lockfile con el estado de la ultima revision (relativa a la raiz).
ESTADO = "references/estado-fuentes.json"

# clave -> (repo, rama, ruta_en_el_repo, ttl_dias, para_que_sirve)
FUENTES = {
    # ---- Power BI: guidance normativa y formato del proyecto ----
    "powerbi_guidance": (
        "MicrosoftDocs/powerbi-docs", "main", "powerbi-docs/guidance", 7,
        "Esquema estrella, DAX, relaciones, RLS, optimizacion. Sustenta "
        "PBI-MOD-*, PBI-DAX-*, PBI-PERF-*."),
    "powerbi_projects": (
        "MicrosoftDocs/powerbi-docs", "main", "powerbi-docs/developer/projects", 7,
        "Formato PBIP/PBIR, limites, casilla de vista previa. Sustenta "
        "references/formatos-pbip.md y las reglas P1-P9."),
    "powerbi_create_reports": (
        "MicrosoftDocs/powerbi-docs", "main", "powerbi-docs/create-reports", 7,
        "Accesibilidad, temas, visuales, Copilot. Sustenta PBI-A11Y-*, "
        "PBI-COL-*, PBI-VIS-*, PBI-IA-*."),
    "powerbi_transform_model": (
        "MicrosoftDocs/powerbi-docs", "main", "powerbi-docs/transform-model", 30,
        "Calculation groups, field parameters, storage mode."),
    "powerbi_connect_data": (
        "MicrosoftDocs/powerbi-docs", "main", "powerbi-docs/connect-data", 30,
        "Conectores, refresco incremental, gateway. Sustenta la fase de datos."),

    # ---- Fabric ----
    "fabric_fundamentals": (
        "MicrosoftDocs/fabric-docs", "main", "docs/fundamentals", 7,
        "Direct Lake, capacidades, Git integration, deployment pipelines."),
    "fabric_enterprise": (
        "MicrosoftDocs/fabric-docs", "main", "docs/enterprise", 30,
        "Gobierno, seguridad y escalado de la capacidad."),

    # ---- TMDL / Analysis Services / DAX ----
    "tmdl": (
        "MicrosoftDocs/bi-shared-docs", "main", "docs/analysis-services/tmdl", 90,
        "Especificacion TMDL: indentacion, expresiones, descripciones ///. "
        "Casi inmovil (ms.date 2023-12-27), de ahi el TTL alto."),
    "analysis_services": (
        "MicrosoftDocs/bi-shared-docs", "main", "docs/analysis-services", 30,
        "Tabular Object Model, compatibility level, particiones."),
    "dax_reference": (
        "MicrosoftDocs/query-docs", "main", "query-languages/dax", 30,
        "Referencia de funciones DAX (517 paginas)."),
    "dax_best_practices": (
        "MicrosoftDocs/query-docs", "main", "query-languages/dax/best-practices", 30,
        "Buenas practicas DAX oficiales, incluidas las UDF. Sustenta PBI-DAX-*."),

    # ---- Esquemas y catalogos machine-readable ----
    "bpa_rules": (
        "microsoft/Analysis-Services", "master", "BestPracticeRules", 90,
        "BPARules.json: las 71 reglas de Best Practice Analyzer OFICIALES, con "
        "ID, Severity, Scope y Expression. Es la fuente del catalogo del modelo."),
    "pbir_schemas": (
        "microsoft/json-schemas", "main", "fabric/item/report/definition", 30,
        "JSON Schemas oficiales de PBIR (visualContainer, page, report...). "
        "Se publican mensualmente."),
    "theme_schema": (
        "microsoft/powerbi-desktop-samples", "main", "Report Theme JSON Schema", 30,
        "Schema oficial de temas, versionado (no hay URL 'latest'). Avisa cuando "
        "hay una version nueva que fijar en generar_theme.py."),

    # ---- Guia de agentes de Microsoft (para saber si cambian de criterio) ----
    "skills_for_fabric": (
        "microsoft/skills-for-fabric", "main", "skills", 30,
        "Los skills oficiales de Microsoft para Fabric/Power BI. No es fuente "
        "normativa, pero si Microsoft cambia su propia guia conviene saberlo."),
}

# Jerarquia de autoridad de la fuente. Una regla de severidad ALTA no puede
# sustentarse solo en un blog: el catalogo lo comprueba.
NIVELES_AUTORIDAD = {
    1: "Documentacion oficial de Microsoft (learn.microsoft.com, docs.microsoft.com)",
    2: "Repos oficiales de Microsoft (github.com/microsoft, github.com/MicrosoftDocs)",
    3: "Estandar publicado por un organismo (W3C/WCAG, IBCS)",
    4: "Experto reconocido del ecosistema (SQLBI, Chris Webb, Tabular Editor)",
    5: "Otro (blog personal, foro). NO puede sustentar severidad ALTA por si solo.",
}

DOMINIOS_POR_NIVEL = {
    "learn.microsoft.com": 1,
    "docs.microsoft.com": 1,
    "powerbi.microsoft.com": 1,
    "github.com/microsoft": 2,
    "github.com/MicrosoftDocs": 2,
    "raw.githubusercontent.com/microsoft": 2,
    "w3.org": 3,
    "ibcs.com": 3,
    "sqlbi.com": 4,
    "crossjoin.co.uk": 4,
    "daxpatterns.com": 4,
    "dax.guide": 4,
    "tabulareditor.com": 4,
}


def nivel_autoridad(url):
    """Nivel 1-5 de una URL segun la jerarquia de autoridad (5 = el mas debil)."""
    if not url:
        return 5
    for patron, nivel in DOMINIOS_POR_NIVEL.items():
        if patron in url:
            return nivel
    return 5


def url_contents(clave):
    """URL de la API de GitHub que lista el contenido de una fuente."""
    import urllib.parse
    repo, rama, ruta, _ttl, _para = FUENTES[clave]
    return ("https://api.github.com/repos/{}/contents/{}?ref={}".format(
        repo, urllib.parse.quote(ruta), rama))


def url_humana(clave):
    """URL navegable de la fuente, para que el usuario pueda ir a mirar."""
    import urllib.parse
    repo, rama, ruta, _ttl, _para = FUENTES[clave]
    return "https://github.com/{}/tree/{}/{}".format(
        repo, rama, urllib.parse.quote(ruta))
