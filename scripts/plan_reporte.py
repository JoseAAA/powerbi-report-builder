#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plan_reporte.py — El PLAN del reporte, en lenguaje de negocio, ANTES de construir.

Por que existe
--------------
Construir primero y enseñar despues obliga al usuario a revisar 14 visuales ya
hechos para descubrir que la historia no era la que queria. Revisar un plan de
media pagina cuesta un minuto; rehacer un reporte, una tarde.

El plan es el CONTRATO: nada se construye hasta que el usuario dice que si.
Patron tomado de Fission-AI/OpenSpec (propuesta -> aprobacion -> implementacion,
con el artefacto en disco) y del HARD-GATE de obra/superpowers ("no invoques
ninguna accion de implementacion hasta que el usuario apruebe el diseño").

Que lo hace distinto de un README de plantilla
----------------------------------------------
1. **Esta en lenguaje de negocio.** Cero TMDL, cero PBIR, cero `visualType`. Si
   el usuario no es tecnico, igual puede validarlo.
2. **Dice la HISTORIA de cada pagina**, no la lista de graficos: que pregunta
   responde, en que orden se lee y con que se sale el lector.
3. **Sobrevive a la compactacion de contexto**: vive en disco (`docs/plan.md`),
   no en la conversacion.
4. **Declara lo que NO sabe.** Lo que el usuario tiene que decidir va marcado
   como pregunta abierta; el plan no se aprueba con preguntas abiertas.

Uso:
  python plan_reporte.py --nombre "Ventas LATAM" --dominio ventas --salida docs/plan.md
  python plan_reporte.py --nombre "X" --dominio salud --json     # contrato agente

Solo libreria estandar.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arquetipos  # noqa: E402
from dominios import DOMINIOS, TABLA_INDICADOR, filas_indicador, nombres  # noqa: E402

CONTRATO = "pbi-builder/plan-reporte@1"

# Que responde cada rol de ranura, en lenguaje de negocio. El usuario valida
# ESTO, no un `visualType`.
QUE_RESPONDE = {
    "titulo": "El mensaje de la pagina: la conclusion, no el tema",
    "slicer_indicador": "Elegir que indicador se esta mirando",
    "slicer_anio": "Acotar el periodo",
    "slicer_dim1": "Acotar por {d1}",
    "kpi_1": "¿Como vamos en {ind}?",
    "kpi_2": "¿Y en el segundo indicador?",
    "kpi_3": "¿Y en el tercero?",
    "tendencia": "¿Mejora o empeora con el tiempo?",
    "ranking": "¿Quien concentra el resultado y quien se queda atras?",
    "detalle": "Las cifras exactas, para llevarselas",
    "matriz": "¿Que combinacion concreta explica el resultado?",
    "comparacion": "¿Como vamos contra el periodo anterior?",
}

# La historia de cada pagina: como se lee, de arriba a abajo.
HISTORIA = {
    "resumen": [
        "Entras y lo primero que ves es **como vamos** (las tarjetas de arriba).",
        "Justo debajo, **si eso mejora o empeora** con el tiempo.",
        "Al lado, **quien lo explica**: que categorias tiran del resultado.",
        "Y abajo, **las cifras exactas** por si alguien las pide.",
    ],
    "detalle": [
        "Aqui vienes a investigar, no a mirar de reojo.",
        "La matriz cruza las dos dimensiones para que **encuentres la celda** que explica lo que viste en Resumen.",
        "Abajo, la **comparacion contra el periodo anterior**.",
    ],
}


def construir(nombre, dominio):
    """Devuelve el plan como estructura de datos (para --json y para el .md)."""
    dom = DOMINIOS[dominio]
    d1, d2, col_grupo, hecho = nombres(dom)
    inds = filas_indicador(dom)
    ppal = inds[0][1]

    paginas = []
    for clave in ("resumen", "detalle"):
        arq = arquetipos.arquetipo(clave)
        bloques = []
        for rol, pregunta, _x, _y, _w, _h, _alt in arq["ranuras"]:
            texto = QUE_RESPONDE.get(rol, rol)
            bloques.append({
                "responde": texto.format(ind=ppal, d1=d1, d2=d2),
                "se_ve_como": arquetipos.COOKBOOK[pregunta]["visual"],
                "por_que": arquetipos.COOKBOOK[pregunta]["regla"],
                "fuente": arquetipos.COOKBOOK[pregunta]["fuente"],
            })
        paginas.append({
            "nombre": arq["titulo"],
            "para_quien": arq["para"],
            "historia": HISTORIA[clave],
            "heuristico": arq.get("heuristico", False),
            "base_citada": arq.get("base_citada", ""),
            "bloques": bloques,
        })

    return {
        "contrato": CONTRATO,
        "reporte": nombre,
        "dominio": dominio,
        "descripcion_dominio": dom["desc"],
        "indicador_principal": ppal,
        "indicadores": [{"nombre": n, "tipo": t} for _i, n, t, _f in inds],
        "dimensiones": [
            {"nombre": d1, "para": f"Cortar por {d1.lower()}"},
            {"nombre": d2, "para": f"Cortar por {d2.lower()} (agrupado en {col_grupo})"},
            {"nombre": TABLA_INDICADOR, "para": "Elegir que se esta midiendo"},
            {"nombre": "Calendario", "para": "Cortar por fecha"},
        ],
        "hecho": hecho,
        "paginas": paginas,
        "preguntas_abiertas": [
            f"¿'{ppal}' es de verdad el indicador que abre el reporte, o hay otro mas importante?",
            f"¿Los cortes por {d1} y {d2} son los que usa tu negocio, o falta alguno?",
            "¿Quien va a leer esto: alguien que decide (le basta Resumen) o alguien que investiga (necesita Detalle)?",
            "¿Hay una meta u objetivo contra el que comparar? Sin meta, un numero solo dice 'cuanto', no 'si vamos bien'.",
        ],
    }


def a_markdown(p):
    L = []
    A = L.append
    A(f"# Plan del reporte — {p['reporte']}")
    A("")
    A("> **Esto es una propuesta, no el reporte.** Leela, dime que cambiar, y")
    A("> recien ahi lo construyo. Cambiar el plan cuesta un minuto; rehacer el")
    A("> reporte, una tarde.")
    A("")
    A(f"**De que trata:** {p['descripcion_dominio']}")
    A("")

    A("## 1. Que vamos a medir")
    A("")
    A("| Indicador | Tipo |")
    A("|---|---|")
    for i in p["indicadores"]:
        marca = "  ← **el principal**" if i["nombre"] == p["indicador_principal"] else ""
        A(f"| {i['nombre']}{marca} | {i['tipo']} |")
    A("")
    A("**Por que importa el principal:** es el que abre el reporte y el que ven")
    A("las tarjetas. Si no es el correcto, dimelo ahora.")
    A("")

    A("## 2. Como vamos a poder cortar la informacion")
    A("")
    for d in p["dimensiones"]:
        A(f"- **{d['nombre']}** — {d['para']}")
    A("")

    A("## 3. Las paginas y su historia")
    A("")
    for n, pg in enumerate(p["paginas"], 1):
        A(f"### Pagina {n}: {pg['nombre']}")
        A("")
        A(f"*Para quien:* {pg['para_quien']}")
        A("")
        A("**Como se lee:**")
        A("")
        for paso in pg["historia"]:
            A(f"1. {paso}" if False else f"- {paso}")
        A("")
        A("**Que va en la pagina:**")
        A("")
        A("| Responde a | Se ve como |")
        A("|---|---|")
        for b in pg["bloques"]:
            A(f"| {b['responde']} | {b['se_ve_como']} |")
        A("")
        if pg["heuristico"]:
            A("> *Nota de honestidad:* la **composicion** de esta pagina es")
            A("> propuesta nuestra — Microsoft no publica arquetipos de pagina con")
            A("> nombre. Lo que si esta respaldado es la eleccion de cada grafico")
            A("> (ver seccion 5) y los principios de composicion:")
            A(f"> {pg['base_citada']}")
            A("")

    A("## 4. Lo que necesito que decidas")
    A("")
    for q in p["preguntas_abiertas"]:
        A(f"- [ ] {q}")
    A("")
    A("**El plan no se aprueba con casillas sin marcar.** Si algo no lo sabes")
    A("todavia, dimelo y lo dejamos anotado como supuesto explicito.")
    A("")

    A("## 5. Por que cada grafico es ese y no otro")
    A("")
    A("Ninguna eleccion es de gusto personal: cada una tiene su razon documentada.")
    A("")
    vistos = {}
    for pg in p["paginas"]:
        for b in pg["bloques"]:
            vistos.setdefault(b["se_ve_como"], b)
    A("| Grafico | Por que ese |")
    A("|---|---|")
    for v, b in sorted(vistos.items()):
        A(f"| `{v}` | {b['por_que']} |")
    A("")
    A("Fuentes: Microsoft Learn (tipos de visual y guia de diseño), WCAG 2.2 para")
    A("accesibilidad, y el catalogo oficial de reglas de Microsoft para el modelo.")
    A("")

    A("## 6. Que pasa cuando digas que si")
    A("")
    A("1. Genero el proyecto con datos de ejemplo que **ya se ven** en el reporte.")
    A("2. Abres el `.pbip`, miras si la historia funciona, y corriges los datos.")
    A("3. Cuando la forma te sirva, cambiamos el origen por tus datos reales.")
    A("")
    A("Los datos de ejemplo son **aleatorios**: sirven para validar la forma, no")
    A("para mostrarlos a nadie como si fueran tu negocio.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Genera el PLAN del reporte en lenguaje de negocio, para que "
                    "el usuario lo valide ANTES de construir nada.")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--dominio", default="generico", choices=sorted(DOMINIOS))
    ap.add_argument("--salida", help="ruta del .md (default: imprime por pantalla)")
    ap.add_argument("--json", action="store_true", help="contrato para agentes")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    plan = construir(args.nombre, args.dominio)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    md = a_markdown(plan)
    if args.salida:
        os.makedirs(os.path.dirname(os.path.abspath(args.salida)), exist_ok=True)
        with open(args.salida, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Plan escrito en: {args.salida}")
        print("")
        print("SIGUIENTE PASO: leelo con el usuario y espera su OK.")
        print("No construyas el proyecto hasta que apruebe y no queden preguntas")
        print("abiertas sin resolver.")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
