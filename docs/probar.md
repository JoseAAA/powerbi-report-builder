# Cómo probarlo (en tu asistente favorito)

Una sola prueba que lo verifica todo, y la ruta concreta para cada plataforma.

## La prueba, en un comando

```bash
python scripts/prueba_rapida.py
```

Ejecuta el flujo completo **y se autoverifica**: genera el plan, construye el
proyecto, corre los cuatro validadores, y después **mete fallos a propósito** para
comprobar que los detecta. Termina con `TODO CORRECTO — 23 comprobaciones` o te
dice exactamente qué falló.

```
[OK  ] el plan se genera
[OK  ] esta en lenguaje de negocio — sin TMDL ni visualType
[OK  ] .pbip en la RAIZ del proyecto
[OK  ] hay datos de verdad — 2304 filas en el hecho
[OK  ] TODOS los visuales con altText — 14/14
[OK  ] detecta division sin DIVIDE()
[OK  ] detecta visual sin altText
[OK  ] detecta datos huerfanos
```

Opciones: `--dominio salud` (o `rrhh`, `finanzas`, `generico`), `--salida <ruta>`
para quedarte el proyecto, `--rapida` para omitir las pruebas negativas.

**No necesita internet ni instalar nada.** Solo Python 3.8 o superior.

---

## Qué funciona en cada plataforma

El proyecto es **stdlib-only**: cero dependencias externas. Eso decide qué puede
hacer cada asistente.

| Plataforma | Ejecuta los scripts | Skills automáticos | Nota |
|---|---|---|---|
| **Claude Code** | ✅ | ✅ plugin | Experiencia completa |
| **Codex** (OpenAI CLI) | ✅ | ✅ vía `AGENTS.md` | Completa |
| **Gemini CLI** / Antigravity | ✅ | ✅ vía `GEMINI.md` | Completa |
| **OpenCode** | ✅ | ✅ vía `AGENTS.md` | Completa |
| **Cursor** | ✅ | ✅ vía `AGENTS.md` | Completa |
| **ChatGPT** (web/desktop) | ✅ en su sandbox | ⚠️ manual | Ver abajo |
| **Claude.ai** (web) | ✅ en su sandbox | ⚠️ manual | Ver abajo |
| **Gemini** (web) | ✅ en su sandbox | ⚠️ manual | Ver abajo |
| **Sin IA** | ✅ | — | `python scripts/…` |

---

## Agentes de terminal (Claude Code, Codex, Gemini CLI, OpenCode, Cursor)

La ruta natural. Clona, abre la carpeta con tu agente y háblale:

```bash
git clone https://github.com/JoseAAA/powerbi-report-builder.git
cd powerbi-report-builder
python scripts/prueba_rapida.py     # confirma que tu entorno está OK
```

Luego, en el chat del agente:

> *"quiero un dashboard de ventas para mi empresa"*

El agente lee `AGENTS.md` (o los skills, en Claude Code), te muestra **el plan
primero**, espera tu OK y recién ahí construye.

---

## ChatGPT, Claude.ai y Gemini (versión web)

Estos **no acceden a tu disco**, pero **sí tienen un sandbox de Python**. Como el
proyecto no usa dependencias externas, los scripts corren ahí sin problema.

**Cómo:**

1. Descarga el repo como ZIP (botón *Code → Download ZIP* en GitHub).
2. En ChatGPT: crea un **Proyecto** y sube el ZIP. En Claude.ai: súbelo al chat o
   a un Proyecto. En Gemini: adjúntalo.
3. Pega esta instrucción:

> Descomprime el ZIP. Lee `AGENTS.md`: es la guía canónica de este framework y
> define las reglas duras que debes seguir. Después ejecuta
> `python scripts/prueba_rapida.py` para verificar que todo funciona.
> A partir de ahí, ayúdame a crear un reporte de Power BI siguiendo el proceso:
> **primero el plan** (`scripts/plan_reporte.py`), esperas mi aprobación, y
> recién después construyes.

4. Cuando termine, pídele el proyecto generado como ZIP para descargarlo y abrirlo
   en Power BI Desktop.

**Qué NO funciona en web** (y por qué):

- **`actualizar_catalogo.py`** — es el único script que necesita internet
  (consulta la API de GitHub). En un sandbox sin red, falla. No pasa nada: el
  catálogo de reglas viene incluido en el repo.
- **Los skills no se activan solos.** En la web no hay autodescubrimiento: por eso
  la instrucción de arriba le dice explícitamente que lea `AGENTS.md`.
- **El resultado hay que descargarlo.** El sandbox es efímero; pide el ZIP antes
  de cerrar la conversación.

---

## Prueba manual de 5 minutos (la que más información da)

Los validadores comprueban el formato. Esto comprueba que **funciona de verdad**:

1. **Activa PBIR una vez** en Power BI Desktop:
   *Archivo → Opciones y configuración → Opciones → Características en vista
   previa →* marca **«Almacenar informes con el formato de metadatos mejorado
   (PBIR)»** y reinicia.
2. Genera un proyecto:
   ```bash
   python scripts/init_proyecto.py --nombre "Prueba" --dominio ventas --sin-marca
   ```
3. **Lee `docs/plan.md`** — ¿la historia tiene sentido para tu negocio?
4. Abre `Prueba.pbip` y pulsa **Inicio → Actualizar**.
   Deberías ver 2 páginas con datos reales, no celdas vacías.
5. Edita `datos/Producto.csv` (cambia un nombre), vuelve a Power BI y **Actualiza**.
   El reporte debe reflejar el cambio sin tocar nada más.

Si algo falla en el paso 4 o 5, **ese error es la información más valiosa** —
ningún validador lo sustituye. Repórtalo con el mensaje exacto de Power BI.

---

## Escenarios para explorar lo que hace

```bash
# Auditar un proyecto existente (el tuyo, o uno de example/)
python scripts/validar_modelo.py     "<ruta>.SemanticModel"
python scripts/validar_pbip.py       "<ruta>.Report"
python scripts/verificar_cableado.py "<carpeta del proyecto>"

# Ver el plan de otro sector, sin construir nada
python scripts/plan_reporte.py --nombre "Operaciones" --dominio salud

# Tu marca, con verificación de contraste WCAG
python scripts/generar_theme.py --marca mi-empresa.json --salida theme.json
python scripts/editar_theme.py --archivo theme.json --modo oscuro

# ¿Microsoft cambió su documentación? (necesita internet)
python scripts/actualizar_catalogo.py

# Cuántas reglas hay y de dónde salen
python scripts/catalogo_reglas.py
```

---

## Si algo falla

| Síntoma | Qué mirar |
|---|---|
| `python: command not found` | Instala [Python 3.8+](https://www.python.org/downloads/) y marca *Add to PATH* |
| La prueba falla en «detecta datos huerfanos» | Corre `python scripts/check_consistencia.py`; suele ser un archivo modificado a mano |
| Al abrir el `.pbip` no carga datos | Moviste el proyecto: corrige *Inicio → Transformar datos → Administrar parámetros → **RutaBase*** |
| Al guardar desaparece `definition/` | Falta activar PBIR (paso 1 de arriba) |
| `actualizar_catalogo.py` da error de red | Normal en un sandbox sin internet; el resto funciona igual |
