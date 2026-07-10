#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_consistencia.py — Guarda de invariantes del repo (evita que la documentacion
se desalinee sola). Inspirado en el check de "rule copies" de ponytail.

Verifica, sin dependencias (solo stdlib):
  C1  Cada skills/<x>/SKILL.md tiene frontmatter con 'name:' y 'description:'.
  C2  La description de cada SKILL.md dice CUANDO activar (contiene "USAR"/"USE"),
      no solo que hace (regla de superpowers).
  C3  Todo skill (salvo el orquestador) esta referenciado en powerbi-builder
      (no hay skills huerfanos sin ruta de enrutamiento).
  C4  Ningun .tmdl de example/ usa 'description:' como propiedad (en TMDL la
      description va con '///' encima del objeto — sintaxis oficial).
  C5  No quedan rangos de reglas desactualizados ("R1-R11"/"P1-P6") en la
      documentacion de estado actual (el CHANGELOG historico se excluye).
  C6  Cada 'references/<x>.md' citada en AGENTS.md existe en disco.
  C7  Portabilidad: AGENTS.md existe y los punteros por agente (CLAUDE.md,
      GEMINI.md) existen y referencian AGENTS.md (una sola fuente de verdad).

Uso:  python scripts/check_consistencia.py
Salida: lista de fallas y exit 1 si hay alguna; exit 0 si todo consistente.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parent.parent
fallas = []


def _leer(p):
    return p.read_text(encoding="utf-8", errors="replace")


def _frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---", texto, re.DOTALL)
    return m.group(1) if m else ""


# --- Skills ---
skill_files = sorted((RAIZ / "skills").glob("*/SKILL.md"))
skills = [f.parent.name for f in skill_files]

for f in skill_files:
    nombre = f.parent.name
    fm = _frontmatter(_leer(f))
    if "name:" not in fm:
        fallas.append(f"C1 {nombre}: falta 'name:' en el frontmatter")
    if "description:" not in fm:
        fallas.append(f"C1 {nombre}: falta 'description:' en el frontmatter")
    # C2: la description debe indicar cuando activar
    if re.search(r"\b(USAR|USE)\b", fm) is None:
        fallas.append(f"C2 {nombre}: la description no dice CUANDO activar "
                      "(usa 'USAR cuando...') — regla de superpowers")

# C3: skills huerfanos (no citados por el orquestador)
orq = RAIZ / "skills" / "powerbi-builder" / "SKILL.md"
if orq.exists():
    txt_orq = _leer(orq)
    for s in skills:
        if s == "powerbi-builder":
            continue
        if s not in txt_orq:
            fallas.append(f"C3 {s}: no esta referenciado en powerbi-builder "
                          "(skill huerfano sin ruta de enrutamiento)")

# C4: description: como propiedad en TMDL de los ejemplos
for t in (RAIZ / "example").rglob("*.tmdl"):
    for i, linea in enumerate(_leer(t).splitlines(), 1):
        if re.match(r"^\s*description:\s", linea):
            rel = t.relative_to(RAIZ).as_posix()
            fallas.append(f"C4 {rel}:{i}: usa 'description:' como propiedad; "
                          "en TMDL la description va con '///' encima del objeto")

# C5: rangos de reglas desactualizados (excluye CHANGELOG historico)
PROHIBIDOS = ("R1-R11", "R1–R11", "P1-P6", "P1–P6")
docs = []
for patron in ("README.md", "AGENTS.md", "CONTRIBUTING.md", "example/README.md"):
    p = RAIZ / patron
    if p.exists():
        docs.append(p)
for d in ("docs", "references", "skills"):
    docs.extend((RAIZ / d).rglob("*.md"))
for f in docs:
    texto = _leer(f)
    for bad in PROHIBIDOS:
        if bad in texto:
            rel = f.relative_to(RAIZ).as_posix()
            fallas.append(f"C5 {rel}: contiene rango desactualizado '{bad}' "
                          "(deberia ser R1-R12 / P1-P7)")

# C6: references citadas en AGENTS.md que no existen
agents = RAIZ / "AGENTS.md"
if agents.exists():
    for ref in sorted(set(re.findall(r"references/[A-Za-z0-9_\-]+\.md", _leer(agents)))):
        if not (RAIZ / ref).exists():
            fallas.append(f"C6 AGENTS.md cita '{ref}' pero el archivo no existe")

# C7: portabilidad multi-agente (AGENTS.md + punteros por proveedor)
if not agents.exists():
    fallas.append("C7 falta AGENTS.md (guia canonica multi-agente)")
for puntero in ("CLAUDE.md", "GEMINI.md"):
    p = RAIZ / puntero
    if not p.exists():
        fallas.append(f"C7 falta el puntero {puntero} (portabilidad del agente)")
    elif "AGENTS.md" not in _leer(p):
        fallas.append(f"C7 {puntero} no referencia AGENTS.md (evita duplicar la guia)")

# --- salida ---
print(f"Skills: {len(skills)} | Chequeos: C1-C7")
if not fallas:
    print("OK  Consistencia del repo: sin fallas.")
    sys.exit(0)
for x in fallas:
    print(f"[FALLA] {x}")
print(f"\nTotal: {len(fallas)} inconsistencia(s)")
sys.exit(1)
