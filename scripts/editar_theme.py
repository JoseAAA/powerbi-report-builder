#!/usr/bin/env python3
"""
editar_theme.py — Modifica un theme.json EXISTENTE de Power BI sin perder
el resto de su configuración. Pensado para cambios puntuales: "cambia el
azul por nuestro verde", "ponme otra fuente", "pásalo a modo oscuro".

A diferencia de generar_theme.py (que crea desde cero), este script CARGA
el tema actual, aplica solo los cambios pedidos y conserva todo lo demás.

Uso (combinables):
  python editar_theme.py --archivo theme.json [opciones]

Opciones:
  --nombre "Nuevo nombre"
  --primario "#1E8449"        Color principal de marca. Actualiza el 1er
                              color de datos, el acento de tablas y la rampa
                              (maximum/center/minimum). El resto de colores
                              de datos NO se toca.
  --color-dato "3:#C44536"    Cambia un color de datos puntual (índice desde 1)
  --bueno "#1E8449"           Semáforo verde (KPI bueno)
  --malo "#C0392B"            Semáforo rojo (KPI malo)
  --neutral "#C99700"         Semáforo ámbar (KPI neutral)
  --texto "#252423"           Texto principal (firstLevelElements)
  --texto-secundario "#605E5C"
  --fondo "#FFFFFF"           Fondo de los visuales (background)
  --fondo-pagina "#F7F7F7"    Fondo del lienzo de la página
  --fuente "Arial"            Cambia la tipografía en todas las clases de texto
  --modo claro|oscuro         Cambia SOLO los colores de estructura (fondos y
                              textos) y CONSERVA la paleta de datos y semáforos
  --salida ruta.json          Por defecto sobrescribe el archivo de entrada
  --no-auto-contraste         Desactiva el ajuste automático de contraste WCAG

Devuelve un resumen de qué cambió (antes → después) y el chequeo de contraste.
"""
import argparse
import colorsys
import copy
import json
import sys

# Salida UTF-8 (evita crash en consolas Windows cp1252 con simbolos como ✔/→).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------- utilidades de color ----------
def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Color hex inválido: #{h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in rgb))


def rel_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(h1, h2):
    l1, l2 = rel_luminance(hex_to_rgb(h1)), rel_luminance(hex_to_rgb(h2))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def adjust_lightness(hexc, factor):
    r, g, b = (c / 255.0 for c in hex_to_rgb(hexc))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.0, min(1.0, l * factor))
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r2 * 255, g2 * 255, b2 * 255))


def ensure_contrast(text_hex, bg_hex, ratio=4.5, max_iter=20):
    if contrast(text_hex, bg_hex) >= ratio:
        return text_hex, False
    bg_lum = rel_luminance(hex_to_rgb(bg_hex))
    factor = 0.85 if bg_lum > 0.5 else 1.18
    c = text_hex
    for _ in range(max_iter):
        c = adjust_lightness(c, factor)
        if contrast(c, bg_hex) >= ratio:
            return c, True
    return ("#252423" if bg_lum > 0.5 else "#F3F2F1"), True


# ---------- presets de modo ----------
CLARO = {"background": "#FFFFFF", "secondaryBackground": "#C8C6C4",
         "firstLevelElements": "#252423", "secondLevelElements": "#605E5C",
         "thirdLevelElements": "#F3F2F1", "fourthLevelElements": "#B3B0AD",
         "null": "#B3B0AD", "_pagina": "#F7F7F7"}
OSCURO = {"background": "#1B1A19", "secondaryBackground": "#3B3A39",
          "firstLevelElements": "#F3F2F1", "secondLevelElements": "#C8C6C4",
          "thirdLevelElements": "#3B3A39", "fourthLevelElements": "#797775",
          "null": "#797775", "_pagina": "#141414"}


def set_page_background(theme, color):
    vs = theme.setdefault("visualStyles", {})
    page = vs.setdefault("page", {}).setdefault("*", {})
    page["background"] = [{"color": {"solid": {"color": color}}, "transparency": 0}]
    page["outspace"] = [{"color": {"solid": {"color": color}}}]


def set_title_color(theme, color):
    vs = theme.setdefault("visualStyles", {})
    star = vs.setdefault("*", {}).setdefault("*", {})
    star["title"] = [{"show": True, "fontColor": {"solid": {"color": color}}, "alignment": "left"}]


def main():
    p = argparse.ArgumentParser(description="Editor de themes Power BI")
    p.add_argument("--archivo", required=True)
    p.add_argument("--nombre")
    p.add_argument("--primario")
    p.add_argument("--color-dato", action="append", default=[],
                   help='formato "N:#hex" (N desde 1)')
    p.add_argument("--bueno")
    p.add_argument("--malo")
    p.add_argument("--neutral")
    p.add_argument("--texto")
    p.add_argument("--texto-secundario", dest="texto_secundario")
    p.add_argument("--fondo")
    p.add_argument("--fondo-pagina", dest="fondo_pagina")
    p.add_argument("--fuente")
    p.add_argument("--modo", choices=["claro", "oscuro"])
    p.add_argument("--salida")
    p.add_argument("--no-auto-contraste", dest="auto_contraste",
                   action="store_false", default=True)
    args = p.parse_args()

    # cargar
    try:
        with open(args.archivo, encoding="utf-8") as f:
            theme = json.load(f)
    except FileNotFoundError:
        print(f"✖ No se encontró el archivo: {args.archivo}")
        return 2
    except json.JSONDecodeError as e:
        print(f"✖ El archivo no es un JSON válido: {e}")
        return 2

    antes = copy.deepcopy(theme)
    cambios = []

    def reg(campo, viejo, nuevo):
        cambios.append(f"{campo}: {viejo} → {nuevo}")

    try:
        return _aplicar(theme, antes, cambios, args, reg)
    except ValueError as e:
        print(f"✖ {e}")
        print("  Los colores deben ir en formato hexadecimal, por ejemplo #1E8449.")
        return 2


def _aplicar(theme, antes, cambios, args, reg):

    # --modo primero (define la base estructural), conservando datos/semáforos
    if args.modo:
        preset = CLARO if args.modo == "claro" else OSCURO
        for k in ("background", "secondaryBackground", "firstLevelElements",
                  "secondLevelElements", "thirdLevelElements",
                  "fourthLevelElements", "null"):
            if theme.get(k) != preset[k]:
                reg(k, theme.get(k, "—"), preset[k])
            theme[k] = preset[k]
        set_page_background(theme, preset["_pagina"])
        set_title_color(theme, preset["firstLevelElements"])
        cambios.append(f"modo → {args.modo} (paleta de datos y semáforos conservados)")

    # nombre
    if args.nombre:
        reg("name", theme.get("name", "—"), args.nombre)
        theme["name"] = args.nombre

    # primario: 1er color de datos + acento de tabla + rampa
    if args.primario:
        hex_to_rgb(args.primario)
        prim = args.primario.upper()
        dc = theme.setdefault("dataColors", [])
        if dc:
            reg("dataColors[1]", dc[0], prim)
            dc[0] = prim
        else:
            dc.append(prim)
            cambios.append(f"dataColors[1] (nuevo) → {prim}")
        for k in ("tableAccent", "maximum"):
            reg(k, theme.get(k, "—"), prim)
            theme[k] = prim
        center, minimum = adjust_lightness(prim, 1.5), adjust_lightness(prim, 1.9)
        reg("center", theme.get("center", "—"), center)
        reg("minimum", theme.get("minimum", "—"), minimum)
        theme["center"], theme["minimum"] = center, minimum

    # colores de datos puntuales
    for spec in args.color_dato:
        if ":" not in spec:
            print(f"✖ --color-dato mal formado (usa N:#hex): {spec}")
            return 2
        idx_s, val = spec.split(":", 1)
        idx = int(idx_s)
        hex_to_rgb(val)
        dc = theme.setdefault("dataColors", [])
        while len(dc) < idx:
            dc.append("#000000")
        reg(f"dataColors[{idx}]", dc[idx - 1], val.upper())
        dc[idx - 1] = val.upper()

    # semáforos
    for arg_val, clave in ((args.bueno, "good"), (args.malo, "bad"),
                           (args.neutral, "neutral")):
        if arg_val:
            hex_to_rgb(arg_val)
            reg(clave, theme.get(clave, "—"), arg_val.upper())
            theme[clave] = arg_val.upper()

    # textos y fondos
    for arg_val, clave in ((args.texto, "firstLevelElements"),
                           (args.texto_secundario, "secondLevelElements"),
                           (args.fondo, "background")):
        if arg_val:
            hex_to_rgb(arg_val)
            reg(clave, theme.get(clave, "—"), arg_val.upper())
            theme[clave] = arg_val.upper()

    if args.fondo_pagina:
        hex_to_rgb(args.fondo_pagina)
        set_page_background(theme, args.fondo_pagina.upper())
        cambios.append(f"fondo de página → {args.fondo_pagina.upper()}")

    # fuente en todas las clases de texto
    if args.fuente:
        tc = theme.setdefault("textClasses", {})
        if not tc:
            cambios.append("aviso: el tema no tenía textClasses; se crean básicas")
            tc.update({
                "title": {"fontFace": args.fuente, "fontSize": 14},
                "header": {"fontFace": args.fuente, "fontSize": 12},
                "label": {"fontFace": args.fuente, "fontSize": 10},
                "callout": {"fontFace": args.fuente, "fontSize": 32},
            })
        else:
            for clase, cfg in tc.items():
                if isinstance(cfg, dict):
                    cfg["fontFace"] = args.fuente
        cambios.append(f"fuente → {args.fuente} (todas las clases de texto)")

    # auto-contraste de textos sobre el fondo
    avisos = []
    if args.auto_contraste and "background" in theme:
        bg = theme["background"]
        for k in ("firstLevelElements", "secondLevelElements"):
            if k in theme:
                nuevo, ajustado = ensure_contrast(theme[k], bg)
                if ajustado:
                    avisos.append(f"{k} ajustado de {theme[k]} a {nuevo} para legibilidad sobre {bg}")
                    theme[k] = nuevo

    if not cambios and not avisos:
        print("No se indicó ningún cambio. Usa --help para ver las opciones.")
        return 0

    salida = args.salida or args.archivo
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)

    print(f"✔ Tema actualizado: {salida}")
    if cambios:
        print("Cambios aplicados:")
        for c in cambios:
            print(f"  • {c}")
    for a in avisos:
        print(f"  ⚠ {a}")

    # chequeo de contraste final
    if "background" in theme:
        bg = theme["background"]
        print("Contraste WCAG (texto sobre fondo):")
        for etiqueta in ("firstLevelElements", "secondLevelElements"):
            if etiqueta in theme:
                r = contrast(theme[etiqueta], bg)
                estado = "OK" if r >= 4.5 else ("OK texto grande" if r >= 3 else "FALLA")
                print(f"  {etiqueta} {theme[etiqueta]} / {bg}: {r:.2f}:1 [{estado}]")

        # Los COLORES DE DATOS tambien tienen minimo de contraste, y es el que se
        # olvida: WCAG 1.4.11 pide >= 3:1 para las partes del grafico necesarias
        # para entenderlo. Al cambiar a modo oscuro la paleta de marca se conserva
        # a proposito (son los colores del usuario), pero un color pensado para
        # fondo claro puede quedar casi invisible sobre fondo oscuro. Reportar solo
        # el contraste del TEXTO daba un "[OK]" enganoso mientras la serie
        # principal quedaba en 1.97:1.
        datos = theme.get("dataColors") or []
        if datos:
            bajos = []
            for i, c in enumerate(datos):
                try:
                    r = contrast(c, bg)
                except Exception:  # noqa: BLE001 — color no parseable: no romper
                    continue
                if r < 3.0:
                    bajos.append((i, c, r))
            print("Contraste de los colores de datos sobre el fondo "
                  "(WCAG 1.4.11 pide >= 3:1):")
            if not bajos:
                print(f"  los {len(datos)} colores de la paleta cumplen [OK]")
            else:
                for i, c, r in bajos:
                    print(f"  dataColors[{i}] {c} / {bg}: {r:.2f}:1 [FALLA]")
                print("")
                print("  QUE HACER: son los colores de TU marca, asi que el script no")
                print("  los cambia solo. Opciones, de mejor a peor:")
                print("   1. Aclara esos hex para el tema oscuro (mantienen el tono,")
                print("      ganan luminosidad) y vuelve a generar el tema.")
                print("   2. Reordena `dataColors` para que los que fallan no sean")
                print("      los primeros: Power BI asigna por orden, asi que el")
                print("      primero es el que mas se ve.")
                print("   3. Usa el tema claro para este reporte.")
                print("  Un color de serie por debajo de 3:1 sobre el fondo deja")
                print("  fuera a quien tiene baja vision: no es un detalle estetico.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
