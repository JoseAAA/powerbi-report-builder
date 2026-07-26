#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
actualizar_catalogo.py — Vigilante de las fuentes oficiales del catalogo.

Consulta los repos publicos de GitHub que respaldan Microsoft Learn y reporta que
cambio desde la ultima revision: paginas AGREGADAS, ELIMINADAS y MODIFICADAS.
Sirve para que la regla "nunca inventes, todo con documentacion oficial y
actualizada" tenga un mecanismo, y no sea solo una buena intencion.

Como funciona (1 sola llamada HTTP por fuente, sin autenticacion)
-----------------------------------------------------------------
`GET /repos/{o}/{r}/contents/{ruta}` devuelve el **blob SHA de cada archivo**, no
solo su nombre. Guardando `{nombre: sha}` se detectan las tres clases de cambio
con una peticion, sin tocar `/commits`. Revision completa = 15 de las 60 llamadas
por hora que da GitHub sin token.

TTL por niveles: cada fuente declara el suyo en `fuentes.py` (7/30/90 dias) segun
su cadencia real. Sin `--forzar` solo se consultan las fuentes vencidas, asi que
una ejecucion rutinaria no gasta casi cuota.

Uso:
  python actualizar_catalogo.py                    # revisa las fuentes vencidas
  python actualizar_catalogo.py --forzar           # revisa todas
  python actualizar_catalogo.py --json             # contrato para agentes
  python actualizar_catalogo.py --marcar-revisado  # persiste el estado nuevo
  python actualizar_catalogo.py --sembrar          # crea el lockfile por 1a vez

Exit codes (estables entre modo humano y --json):
  0  sin cambios (o nada vencido)
  1  HAY cambios que revisar
  2  error de red / API

Privacidad: solo lee metadatos publicos de GitHub. No envia ningun dato del
usuario ni de su proyecto.

Solo libreria estandar (urllib, json, argparse, datetime).
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuentes import ESTADO, FUENTES, url_contents, url_humana  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_ESTADO = os.path.join(RAIZ, ESTADO)
CONTRATO = "pbi-builder/actualizar-catalogo@1"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def ahora_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cargar_estado():
    if not os.path.exists(RUTA_ESTADO):
        return {"fuentes": {}}
    with open(RUTA_ESTADO, encoding="utf-8") as f:
        return json.load(f)


def guardar_estado(estado):
    estado["_comentario"] = (
        "Lockfile de la documentacion oficial que sustenta el catalogo de reglas. "
        "Lo mantiene scripts/actualizar_catalogo.py; no lo edites a mano. "
        "'archivos' guarda el blob SHA de cada pagina para detectar modificaciones, "
        "no solo altas y bajas.")
    estado["_generado_por"] = CONTRATO
    os.makedirs(os.path.dirname(RUTA_ESTADO), exist_ok=True)
    with open(RUTA_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def dias_desde(iso):
    if not iso:
        return None
    try:
        t = dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=dt.timezone.utc)
    except ValueError:
        return None
    return (dt.datetime.now(dt.timezone.utc) - t).days


def listar(clave):
    """
    {nombre: sha} de una fuente. Lanza RuntimeError si falla.

    Incluye tambien las SUBCARPETAS, y no por completitud: para un directorio,
    GitHub devuelve su **tree SHA**, que cambia si cambia cualquier cosa dentro.
    Eso da deteccion recursiva de cambios con una sola llamada, y es lo unico que
    funciona en fuentes cuyo contenido son carpetas y no archivos
    (`pbir_schemas`, donde cada schema vive en `<tipo>/<version>/schema.json`, y
    `skills_for_fabric`, con una carpeta por skill).
    """
    req = urllib.request.Request(
        url_contents(clave),
        headers={"User-Agent": "powerbi-report-builder",
                 "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            items = json.load(r)
            restante = r.headers.get("X-RateLimit-Remaining")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise RuntimeError(
                "GitHub devolvio 403: probablemente agotaste las 60 llamadas por "
                "hora que permite sin token. Espera o usa --forzar mas tarde.")
        raise RuntimeError(f"HTTP {e.code} en {clave}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"sin red o host inalcanzable ({e.reason})")
    inventario = {}
    for i in items:
        if i.get("type") == "file":
            inventario[i["name"]] = i["sha"]
        elif i.get("type") == "dir":
            # sufijo "/" para distinguir carpeta de archivo en el diff
            inventario[i["name"] + "/"] = i["sha"]
    return inventario, restante


def revisar(forzar):
    estado = cargar_estado()
    fu = estado.setdefault("fuentes", {})
    resultados = []
    restante = None

    for clave, (repo, rama, ruta, ttl, para) in sorted(FUENTES.items()):
        previo = fu.get(clave, {})
        dias = dias_desde(previo.get("ultima_revision"))
        if not forzar and dias is not None and dias < ttl:
            resultados.append({
                "fuente": clave, "estado": "al-dia-por-ttl",
                "dias_desde_revision": dias, "ttl_dias": ttl,
                "cambios": {}})
            continue

        try:
            actual, restante = listar(clave)
        except RuntimeError as e:
            resultados.append({"fuente": clave, "estado": "error",
                               "mensaje": str(e), "cambios": {}})
            continue

        anterior = previo.get("archivos", {})
        agregados = sorted(set(actual) - set(anterior))
        eliminados = sorted(set(anterior) - set(actual))
        modificados = sorted(n for n in set(actual) & set(anterior)
                             if actual[n] != anterior[n])
        primera_vez = not anterior
        cambios = {}
        if not primera_vez:
            if agregados:
                cambios["agregados"] = agregados
            if eliminados:
                cambios["eliminados"] = eliminados
            if modificados:
                cambios["modificados"] = modificados

        resultados.append({
            "fuente": clave, "repo": repo, "rama": rama, "ruta": ruta,
            "ttl_dias": ttl, "para_que": para, "url": url_humana(clave),
            "estado": "sembrada" if primera_vez else (
                "con-cambios" if cambios else "sin-cambios"),
            "n_archivos": len(actual), "cambios": cambios,
        })
        # estado nuevo (se persiste solo con --marcar-revisado / --sembrar)
        fu[clave] = {"repo": repo, "rama": rama, "ruta": ruta,
                     "ttl_dias": ttl, "para_que": para,
                     "ultima_revision": ahora_iso(), "archivos": actual}

    return estado, resultados, restante


def main():
    ap = argparse.ArgumentParser(
        description="Detecta cambios en la documentacion oficial que sustenta el catalogo.")
    ap.add_argument("--forzar", action="store_true",
                    help="revisa todas las fuentes, ignorando el TTL")
    ap.add_argument("--json", action="store_true",
                    help="salida JSON (contrato para agentes)")
    ap.add_argument("--marcar-revisado", dest="marcar", action="store_true",
                    help="persiste el estado nuevo tras revisar los cambios")
    ap.add_argument("--sembrar", action="store_true",
                    help="crea el lockfile por primera vez (implica --forzar y --marcar-revisado)")
    args = ap.parse_args()
    if args.sembrar:
        args.forzar = args.marcar = True

    estado, resultados, restante = revisar(args.forzar)

    con_cambios = [r for r in resultados if r["estado"] == "con-cambios"]
    errores = [r for r in resultados if r["estado"] == "error"]
    if args.marcar and not errores:
        guardar_estado(estado)

    if args.json:
        print(json.dumps({
            "contrato": CONTRATO, "revisado": ahora_iso(),
            "llamadas_restantes_github": restante,
            "totales": {"fuentes": len(resultados),
                        "con_cambios": len(con_cambios),
                        "errores": len(errores)},
            "fuentes": resultados,
        }, ensure_ascii=False, indent=2))
        return 2 if errores else (1 if con_cambios else 0)

    print("=" * 72)
    print(f"Fuentes oficiales revisadas: {len(resultados)}"
          + (f"  |  llamadas restantes a GitHub: {restante}" if restante else ""))
    print("=" * 72)
    for r in resultados:
        if r["estado"] == "al-dia-por-ttl":
            print(f"  ·  {r['fuente']:<24} al dia (revisada hace "
                  f"{r['dias_desde_revision']}d, TTL {r['ttl_dias']}d)")
        elif r["estado"] == "error":
            print(f"  !  {r['fuente']:<24} ERROR: {r['mensaje']}")
        elif r["estado"] == "sembrada":
            print(f"  +  {r['fuente']:<24} sembrada ({r['n_archivos']} archivos)")
        elif r["estado"] == "sin-cambios":
            print(f"  =  {r['fuente']:<24} sin cambios ({r['n_archivos']} archivos)")
        else:
            print(f"  *  {r['fuente']:<24} CAMBIOS:")
            for tipo, lista in r["cambios"].items():
                muestra = ", ".join(lista[:6]) + (" ..." if len(lista) > 6 else "")
                print(f"        {tipo}: {len(lista)} -> {muestra}")
            print(f"        sustenta: {r['para_que']}")
            print(f"        revisar : {r['url']}")

    print("")
    if errores:
        print("Hubo errores de red/API: el estado NO se guardo.")
        return 2
    if not con_cambios:
        print("Catalogo al dia: ninguna fuente oficial cambio.")
        if not args.marcar:
            print("(usa --marcar-revisado para reiniciar los contadores de TTL)")
        return 0
    print(f"{len(con_cambios)} fuente(s) con cambios. Siguiente paso: abre las URLs de")
    print("arriba, decide si algun cambio afecta a una regla del catalogo, aplicalo, y")
    print("cierra el ciclo con --marcar-revisado. NO toques el catalogo sin leer el")
    print("cambio: una pagina nueva no siempre implica una regla nueva.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
