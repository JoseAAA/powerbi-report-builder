#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tmdl.py — Parser minimo de TMDL (Tabular Model Definition Language).

Por que existe
--------------
Las reglas de Best Practice Analyzer oficiales de Microsoft se evaluan sobre
objetos del modelo (tablas, columnas, medidas, particiones, relaciones), no sobre
texto. Implementarlas con expresiones regulares sobre el .tmdl da falsos
positivos con facilidad: ya me paso una vez, con un `[\\w ]+` que capturaba un
espacio y reportaba medidas "cualificadas" que no lo estaban.

Este modulo convierte una carpeta TMDL en un arbol de objetos con sus
propiedades, para que las reglas se escriban sobre datos y no sobre cadenas.

Que implementa de la especificacion
-----------------------------------
  - Declaracion de objeto: `<tipo> <nombre>` con nombre entre comillas simples si
    contiene espacio, punto, igual, dos puntos o comilla (doble '' escapa una).
  - Propiedades `clave: valor`, y la forma corta booleana (solo el nombre, que
    implica true) — p. ej. `isHidden`.
  - Propiedad por defecto tras `=`, en la misma linea o multilinea.
  - Expresiones multilinea, incluidas las delimitadas por triple backtick, que se
    leen literales.
  - Descripciones con `///` encima del objeto (sintaxis oficial; NO existe una
    propiedad `description:` en TMDL).
  - Anidamiento por indentacion. La spec dice "default single tab", pero no
    declara invalidos los espacios y los propios ejemplos de Microsoft mezclan
    tabs con 1 y 4 espacios: el parser acepta ambos y normaliza.
  - `ref <tipo> <nombre>` para el orden de colecciones.

Lo que NO implementa (y no hace falta para auditar un modelo)
-------------------------------------------------------------
  Evaluacion de DAX o M: las expresiones se guardan como texto. Las reglas que
  necesitan el grafo de dependencias o un tokenizador de DAX quedan fuera y estan
  marcadas como tales en el catalogo.

Solo libreria estandar.
"""
import os
import re

# Tipos de objeto que declaran un bloque en TMDL.
TIPOS = (
    "database", "model", "table", "column", "measure", "partition", "hierarchy",
    "level", "relationship", "role", "tablePermission", "columnPermission",
    "perspective", "perspectiveTable", "perspectiveColumn", "perspectiveMeasure",
    "culture", "expression", "annotation", "extendedProperty", "calculationGroup",
    "calculationItem", "function", "dataSource", "queryGroup", "variation",
    "changedProperty", "detailRowsDefinition", "formatStringDefinition",
    "calculationExpression", "linguisticMetadata", "refreshPolicy",
)
_TIPOS_RE = "|".join(sorted(TIPOS, key=len, reverse=True))

# `tipo nombre` / `tipo 'nombre con espacio'` / `tipo nombre = expresion`
_DECL = re.compile(
    r"^(?P<tipo>" + _TIPOS_RE + r")"
    r"(?:\s+(?P<nombre>'(?:[^']|'')*'|[^\s=]+))?"
    r"(?:\s*=\s*(?P<valor>.*))?$"
)
_PROP = re.compile(r"^(?P<clave>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<valor>.*)$")
_REF = re.compile(r"^ref\s+(?P<tipo>\w+)\s+(?P<nombre>'(?:[^']|'')*'|\S+)\s*$")


def desescapar(nombre):
    """Quita las comillas simples de un nombre TMDL y desescapa las internas."""
    if nombre and len(nombre) >= 2 and nombre[0] == "'" and nombre[-1] == "'":
        return nombre[1:-1].replace("''", "'")
    return nombre or ""


def _sangria(linea):
    """Nivel de indentacion. Un tab = 1 nivel; 4 espacios = 1 nivel."""
    n = 0
    i = 0
    while i < len(linea):
        if linea[i] == "\t":
            n += 1
            i += 1
        elif linea[i] == " ":
            j = i
            while j < len(linea) and linea[j] == " ":
                j += 1
            n += (j - i) // 4 or (1 if (j - i) else 0)
            i = j
        else:
            break
    return n


class Nodo:
    """Un objeto TMDL: tipo, nombre, propiedades, expresion, hijos y descripcion."""

    __slots__ = ("tipo", "nombre", "props", "expresion", "hijos", "descripcion",
                 "archivo", "linea", "padre")

    def __init__(self, tipo, nombre, archivo=None, linea=0, padre=None):
        self.tipo = tipo
        self.nombre = nombre
        self.props = {}
        self.expresion = None
        self.hijos = []
        self.descripcion = None
        self.archivo = archivo
        self.linea = linea
        self.padre = padre

    # --- consultas comodas -------------------------------------------------
    def de_tipo(self, *tipos):
        return [h for h in self.hijos if h.tipo in tipos]

    def prop(self, clave, default=None):
        return self.props.get(clave, default)

    def bool_prop(self, clave):
        """isHidden / isKey: presentes sin valor implican true."""
        v = self.props.get(clave)
        if v is None:
            return False
        if v == "":
            return True
        return str(v).strip().lower() == "true"

    @property
    def oculto(self):
        return self.bool_prop("isHidden")

    def __repr__(self):
        return f"<{self.tipo} {self.nombre!r} props={len(self.props)} hijos={len(self.hijos)}>"


def parsear_texto(texto, archivo=None):
    """Parsea un documento TMDL y devuelve la lista de nodos de nivel superior."""
    raices = []
    pila = []          # [(nivel, nodo)]
    refs = []
    descripcion = []   # lineas /// acumuladas
    lineas = texto.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lineas):
        cruda = lineas[i]
        desnuda = cruda.strip()
        if not desnuda:
            i += 1
            continue

        nivel = _sangria(cruda)

        # descripcion /// (se adjunta al SIGUIENTE objeto declarado)
        if desnuda.startswith("///"):
            descripcion.append(desnuda[3:].strip())
            i += 1
            continue

        if desnuda.startswith("//"):     # no es sintaxis TMDL valida, pero se ignora
            i += 1
            continue

        m = _REF.match(desnuda)
        if m:
            refs.append((m.group("tipo"), desescapar(m.group("nombre"))))
            i += 1
            continue

        # cerrar bloques mas profundos
        while pila and pila[-1][0] >= nivel:
            pila.pop()
        actual = pila[-1][1] if pila else None

        decl = _DECL.match(desnuda)
        prop = _PROP.match(desnuda)

        # Una declaracion gana sobre una propiedad solo si el token es un tipo
        # conocido; asi `mode: import` no se confunde con nada.
        if decl and (not prop or decl.group("tipo") != prop.group("clave")):
            nodo = Nodo(decl.group("tipo"), desescapar(decl.group("nombre")),
                        archivo, i + 1, actual)
            if descripcion:
                nodo.descripcion = "\n".join(descripcion)
                descripcion = []
            valor = decl.group("valor")
            if valor is not None:
                valor = valor.strip()
                if valor.startswith("```"):
                    expr, i = _leer_backticks(lineas, i, valor)
                    nodo.expresion = expr
                elif valor:
                    nodo.expresion = valor
                else:
                    expr, i = _leer_multilinea(lineas, i, nivel)
                    nodo.expresion = expr
            if actual is None:
                raices.append(nodo)
            else:
                actual.hijos.append(nodo)
            pila.append((nivel, nodo))
            i += 1
            continue

        if prop and actual is not None:
            clave, valor = prop.group("clave"), prop.group("valor").strip()
            if valor.startswith("```"):
                expr, i = _leer_backticks(lineas, i, valor)
                actual.props[clave] = expr
            elif valor == "":
                # `source =` en la linea previa ya se trato; aqui es propiedad
                # con valor multilinea (p. ej. `source =` sin nada detras).
                expr, i = _leer_multilinea(lineas, i, nivel)
                actual.props[clave] = expr
            else:
                actual.props[clave] = _limpiar_valor(valor)
            i += 1
            continue

        # propiedad booleana en forma corta (solo el nombre)
        if actual is not None and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", desnuda):
            actual.props[desnuda] = ""
            i += 1
            continue

        # `source =` (propiedad con `=` en vez de `:`)
        m2 = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", desnuda)
        if m2 and actual is not None:
            clave, valor = m2.group(1), m2.group(2).strip()
            if valor.startswith("```"):
                expr, i = _leer_backticks(lineas, i, valor)
            elif valor:
                expr = valor
            else:
                expr, i = _leer_multilinea(lineas, i, nivel)
            actual.props[clave] = expr
            i += 1
            continue

        i += 1

    for r in raices:
        r.props.setdefault("_refs", refs)
    return raices


def _limpiar_valor(valor):
    """Las comillas dobles envolventes son opcionales en TMDL y se descartan."""
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        return valor[1:-1].replace('""', '"')
    return valor


def _leer_backticks(lineas, i, primera):
    """Lee una expresion delimitada por ``` (literal, indentacion incluida)."""
    cuerpo = []
    resto = primera[3:]
    if resto.strip():
        cuerpo.append(resto)
    j = i + 1
    while j < len(lineas):
        if lineas[j].strip() == "```":
            break
        cuerpo.append(lineas[j])
        j += 1
    # se recorta la indentacion comun
    return _desindentar(cuerpo), j


def _leer_multilinea(lineas, i, nivel_padre):
    """Lee una expresion multilinea: todo lo indentado por debajo del padre."""
    cuerpo = []
    j = i + 1
    while j < len(lineas):
        if not lineas[j].strip():
            cuerpo.append("")
            j += 1
            continue
        if _sangria(lineas[j]) <= nivel_padre:
            break
        cuerpo.append(lineas[j])
        j += 1
    while cuerpo and not cuerpo[-1].strip():
        cuerpo.pop()
    return _desindentar(cuerpo), j - 1


def _desindentar(cuerpo):
    utiles = [l for l in cuerpo if l.strip()]
    if not utiles:
        return ""
    comun = min(len(l) - len(l.lstrip("\t ")) for l in utiles)
    return "\n".join(l[comun:] if l.strip() else "" for l in cuerpo)


class Modelo:
    """Un modelo semantico completo, leido de una carpeta `definition/`."""

    def __init__(self, ruta):
        self.ruta = ruta
        self.raices = []
        self.archivos = []
        base = ruta
        if os.path.isdir(os.path.join(ruta, "definition")):
            base = os.path.join(ruta, "definition")
        for dirpath, _dirs, files in os.walk(base):
            for f in sorted(files):
                if not f.endswith(".tmdl"):
                    continue
                p = os.path.join(dirpath, f)
                self.archivos.append(p)
                with open(p, encoding="utf-8-sig") as fh:
                    self.raices.extend(parsear_texto(fh.read(), p))

    # --- colecciones -------------------------------------------------------
    def _raices_de(self, tipo):
        return [r for r in self.raices if r.tipo == tipo]

    @property
    def tablas(self):
        return self._raices_de("table") + self._raices_de("calculationGroup")

    @property
    def relaciones(self):
        return self._raices_de("relationship")

    @property
    def roles(self):
        return self._raices_de("role")

    @property
    def expresiones(self):
        return self._raices_de("expression")

    @property
    def modelo(self):
        r = self._raices_de("model")
        return r[0] if r else None

    def columnas(self):
        for t in self.tablas:
            for c in t.de_tipo("column"):
                yield t, c

    def medidas(self):
        for t in self.tablas:
            for m in t.de_tipo("measure"):
                yield t, m

    def particiones(self):
        for t in self.tablas:
            for p in t.de_tipo("partition"):
                yield t, p

    def tabla(self, nombre):
        for t in self.tablas:
            if t.nombre == nombre:
                return t
        return None

    def columna(self, tabla, columna):
        t = self.tabla(tabla)
        if not t:
            return None
        for c in t.de_tipo("column"):
            if c.nombre == columna:
                return c
        return None

    def tabla_oculta(self, tabla):
        return tabla.oculto


def cargar(ruta):
    """Carga un modelo desde la carpeta .SemanticModel o su `definition/`."""
    return Modelo(ruta)
