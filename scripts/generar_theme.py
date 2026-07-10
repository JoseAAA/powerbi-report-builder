#!/usr/bin/env python3
"""
generar_theme.py - Genera un theme.json de Power BI desde un ARCHIVO DE MARCA
(assets/marca/<empresa>.json) o desde colores sueltos.

Uso principal (recomendado): leer la marca guardada
  python generar_theme.py --marca ../assets/marca/ejemplos/ejemplo-corporativo.json [--salida theme.json]

Uso alterno: colores sueltos (sin archivo de marca)
  python generar_theme.py --nombre "Tema ACME" --primario "#0F4C81" \
      [--paleta "#0F4C81,#F2A104,..."] [--fuente "Segoe UI"] [--modo claro|oscuro]

Produce un tema completo y valido para Power BI (mid-2026):
  - $schema apuntando al schema oficial (autocompletado en VS Code)
  - dataColors, colores estructurales, semaforos (good/neutral/bad),
    rampa de formato condicional (maximum/center/minimum/null)
  - textClasses (4 clases primarias) y visualStyles globales
  - un style preset de ejemplo para card (feature 2026)
Verifica contraste WCAG (>=4.5:1 texto normal, >=3:1 callouts) y ajusta el
texto automaticamente si no cumple.

Referencias:
  - Schema oficial: github.com/microsoft/powerbi-desktop-samples
    /tree/main/Report Theme JSON Schema
  - learn.microsoft.com .../report-themes-create-custom
"""
import argparse
import colorsys
import json
import sys

SCHEMA_URL = ("https://raw.githubusercontent.com/microsoft/"
              "powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/"
              "reportThemeSchema-2.143.json")


# ---------- utilidades de color ----------
def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Color hex invalido: #{h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        *(max(0, min(255, round(c))) for c in rgb))


def rel_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(hex1, hex2):
    l1, l2 = rel_luminance(hex_to_rgb(hex1)), rel_luminance(hex_to_rgb(hex2))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def adjust_lightness(hexc, factor):
    r, g, b = (c / 255.0 for c in hex_to_rgb(hexc))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.0, min(1.0, l * factor))
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r2 * 255, g2 * 255, b2 * 255))


def ensure_contrast(text_hex, bg_hex, ratio=4.5, max_iter=20):
    """Oscurece/aclara el texto hasta cumplir el ratio contra el fondo."""
    if contrast(text_hex, bg_hex) >= ratio:
        return text_hex, False
    bg_lum = rel_luminance(hex_to_rgb(bg_hex))
    factor = 0.85 if bg_lum > 0.5 else 1.18
    cur = text_hex
    for _ in range(max_iter):
        cur = adjust_lightness(cur, factor)
        if contrast(cur, bg_hex) >= ratio:
            return cur, True
    return cur, True


# ---------- carga de marca ----------
def marca_a_config(ruta):
    with open(ruta, encoding="utf-8") as f:
        m = json.load(f)
    c = m["colores"]
    return {
        "nombre": f"Tema {m.get('marca', 'Empresa')}",
        "paleta": c["paletaDatos"],
        "good": c["semaforo"]["bueno"],
        "neutral": c["semaforo"]["neutral"],
        "bad": c["semaforo"]["malo"],
        "texto": c["texto"]["principal"],
        "texto2": c["texto"]["secundario"],
        "texto3": c["fondo"]["grid"],
        "texto4": c["texto"]["atenuado"],
        "fondoVisual": c["fondo"]["visual"],
        "fondoSecundario": c["fondo"]["secundario"],
        "fondoPagina": c["fondo"]["pagina"],
        "tableAccent": c["primario"],
        "maximum": c["rampa"]["maximo"],
        "center": c["rampa"]["centro"],
        "minimum": c["rampa"]["minimo"],
        "null": c["rampa"]["nulo"],
        "fuente": m["tipografia"]["familia"],
        "fuenteTitulo": m["tipografia"].get("familiaTitulos",
                                            m["tipografia"]["familia"]),
        "tam": m["tipografia"]["tamanos"],
        "modo": m.get("modo", "claro"),
    }


def config_basico(args):
    """Config cuando no hay archivo de marca (colores sueltos)."""
    if args.paleta:
        paleta = [c.strip() for c in args.paleta.split(",") if c.strip()]
    elif args.primario:
        p = args.primario
        paleta = [p, "#E25822", "#50C878", "#1987EC",
                  "#E1C955", "#6B7A8F", "#1076AA", "#9C5BA8"]
    else:
        raise SystemExit("Falta --marca o --primario/--paleta")
    osc = args.modo == "oscuro"
    return {
        "nombre": args.nombre or "Tema personalizado",
        "paleta": paleta,
        "good": "#2E8B57", "neutral": "#E1A30B", "bad": "#C0392B",
        "texto": "#E6E6E6" if osc else "#252423",
        "texto2": "#B3B0AD" if osc else "#605E5C",
        "texto3": "#3B3A39" if osc else "#DBE3EA",
        "texto4": "#8A8886",
        "fondoVisual": "#201F1E" if osc else "#FFFFFF",
        "fondoSecundario": "#2B2A29" if osc else "#EAEFF4",
        "fondoPagina": "#161514" if osc else "#F5F6F8",
        "tableAccent": paleta[0],
        "maximum": paleta[0], "center": "#84A9C0",
        "minimum": "#DCE6EF", "null": "#B3B0AD",
        "fuente": args.fuente or "Segoe UI",
        "fuenteTitulo": (args.fuente or "Segoe UI"),
        "tam": {"callout": 34, "title": 14, "header": 12, "label": 10},
        "modo": args.modo,
    }


# ---------- validacion ----------
_COLOR_KEYS = ("good", "neutral", "bad", "texto", "texto2", "texto3", "texto4",
               "fondoVisual", "fondoSecundario", "fondoPagina", "tableAccent",
               "maximum", "center", "minimum", "null")


def validar_colores_cfg(cfg):
    """Falla ANTES de escribir si algun color no es un hex valido.
    Evita que un valor como 'azul' se cuele al theme.json (Power BI lo rechaza)."""
    malos = []
    for i, c in enumerate(cfg.get("paleta", [])):
        try:
            hex_to_rgb(c)
        except ValueError:
            malos.append(f"paleta[{i}]='{c}'")
    for k in _COLOR_KEYS:
        v = cfg.get(k)
        if v is None:
            continue
        try:
            hex_to_rgb(v)
        except ValueError:
            malos.append(f"{k}='{v}'")
    if malos:
        raise ValueError(
            "color(es) no valido(s) (usa hex tipo #1B4D77): " + ", ".join(malos))


# ---------- construccion del tema ----------
def construir_tema(cfg, no_auto_contraste=False):
    validar_colores_cfg(cfg)
    reporte = []
    texto = cfg["texto"]
    if not no_auto_contraste:
        texto, ajustado = ensure_contrast(texto, cfg["fondoVisual"], 4.5)
        if ajustado:
            reporte.append(
                f"Texto principal ajustado a {texto} para contraste >=4.5:1 "
                f"sobre {cfg['fondoVisual']}.")
    cf = contrast(texto, cfg["fondoVisual"])

    if len(cfg["paleta"]) < 8:
        reporte.append(
            f"AVISO: solo {len(cfg['paleta'])} colores de datos; se "
            f"recomiendan >=8 (Power BI cicla colores si hay mas series).")

    tema = {
        "$schema": SCHEMA_URL,
        "name": cfg["nombre"],
        "dataColors": cfg["paleta"],
        "good": cfg["good"],
        "neutral": cfg["neutral"],
        "bad": cfg["bad"],
        "maximum": cfg["maximum"],
        "center": cfg["center"],
        "minimum": cfg["minimum"],
        "null": cfg["null"],
        "firstLevelElements": texto,
        "secondLevelElements": cfg["texto2"],
        "thirdLevelElements": cfg["texto3"],
        "fourthLevelElements": cfg["texto4"],
        "background": cfg["fondoVisual"],
        "secondaryBackground": cfg["fondoSecundario"],
        "tableAccent": cfg["tableAccent"],
        "textClasses": {
            "callout": {"fontFace": cfg["fuenteTitulo"],
                        "fontSize": cfg["tam"]["callout"], "color": texto},
            "title": {"fontFace": cfg["fuenteTitulo"],
                      "fontSize": cfg["tam"]["title"], "color": texto},
            "header": {"fontFace": cfg["fuenteTitulo"],
                       "fontSize": cfg["tam"]["header"], "color": texto},
            "label": {"fontFace": cfg["fuente"],
                      "fontSize": cfg["tam"]["label"], "color": texto},
        },
        "visualStyles": {
            "*": {
                "*": {
                    "background": [{"show": True, "transparency": 0,
                                    "color": {"solid": {"color": cfg["fondoVisual"]}}}],
                    "border": [{"show": False}],
                    "dropShadow": [{"show": False}],
                    "title": [{"show": True, "alignment": "left",
                               "fontColor": {"solid": {"color": texto}}}],
                    "visualHeaderTooltip": [{"show": True}],
                }
            },
            "page": {
                "*": {
                    "background": [{"transparency": 0,
                                    "color": {"solid": {"color": cfg["fondoPagina"]}}}],
                    "outspace": [{"color": {"solid": {"color": cfg["fondoPagina"]}}}],
                }
            },
            "card": {
                "*": {
                    "labels": [{"fontSize": cfg["tam"]["callout"],
                                "color": {"solid": {"color": cfg["tableAccent"]}}}],
                    "categoryLabels": [{"color": {"solid": {"color": cfg["texto2"]}}}],
                },
                "Callout Destacado": {
                    "labels": [{"fontSize": cfg["tam"]["callout"] + 6,
                                "bold": True}]
                }
            }
        },
    }
    return tema, reporte, cf


def main():
    ap = argparse.ArgumentParser(description="Genera theme.json de Power BI.")
    ap.add_argument("--marca", help="ruta a un archivo de marca JSON")
    ap.add_argument("--nombre")
    ap.add_argument("--primario")
    ap.add_argument("--paleta", help="hex separados por coma (8+)")
    ap.add_argument("--fuente")
    ap.add_argument("--modo", choices=["claro", "oscuro"], default="claro")
    ap.add_argument("--salida", default="theme.json")
    ap.add_argument("--no-auto-contraste", action="store_true")
    args = ap.parse_args()

    try:
        cfg = marca_a_config(args.marca) if args.marca else config_basico(args)
        tema, reporte, cf = construir_tema(cfg, args.no_auto_contraste)
    except (ValueError, KeyError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    with open(args.salida, "w", encoding="utf-8") as f:
        json.dump(tema, f, ensure_ascii=False, indent=2)

    print(f"OK  theme.json -> {args.salida}")
    print(f"    nombre: {tema['name']}")
    print(f"    dataColors: {len(tema['dataColors'])} colores")
    print(f"    contraste texto/fondo: {cf:.2f}:1 "
          f"({'AA OK' if cf >= 4.5 else 'REVISAR'})")
    for r in reporte:
        print(f"    - {r}")
    print("\nImportar en Power BI: Vista -> Temas -> Buscar temas -> "
          f"elegir {args.salida}")


if __name__ == "__main__":
    main()
