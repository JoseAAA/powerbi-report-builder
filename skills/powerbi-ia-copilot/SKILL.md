---
name: powerbi-ia-copilot
description: >
  USAR cuando el modelo lo va a consumir una IA: "quiero que Copilot responda bien
  sobre esto", "preparar datos para IA", "Prep data for AI", "Approved for
  Copilot", faltan sinonimos, descripciones de medidas, AI instructions o verified
  answers, o el modelo lo va a leer un agente LLM/MCP. NO usar para escribir las
  medidas en si (eso es powerbi-modelado-dax).
---

# Preparar el modelo para IA / Copilot

Objetivo: que el modelo dé **buenas respuestas cuando lo consulta una IA** — el
Copilot de Power BI y también los agentes LLM/MCP que este framework asume como
consumidores del modelo. Un modelo AI-ready es un modelo bien hecho: los mismos
metadatos sirven a la persona y a la máquina.

Reglas de oro (impacto de mayor a menor):
1. **Fundamento limpio primero**: estrella sin ambigüedad, nombres de negocio
   únicos entre tablas, oculta lo técnico, quita lo muerto (`fase4-modelado.md`,
   `nomenclatura.md`).
2. **`description` en cada medida** (y en tablas/columnas clave): frase de negocio,
   no repetir el DAX. Es lo que más lee Copilot y lo que lee un agente del TMDL.
   `validar_modelo.py` marca **R12** las medidas sin description.
3. **Sinónimos y verbos** (linguistic schema / Q&A) para los términos con varios
   nombres.
4. **Prep data for AI** (Power BI, preview): **AI instructions**, **AI data
   schemas** y **verified answers** — se guardan en el modelo, requieren Q&A.
5. **Approved for Copilot** + Q&A habilitado antes de entregar.

Detalle, tabla de las 3 funciones, cómo probar (skill picker/HCAAT) y checklist:
`${CLAUDE_PLUGIN_ROOT}/references/preparar-datos-ia.md`.
Antes de tocar un PBIP: `${CLAUDE_PLUGIN_ROOT}/references/formatos-pbip.md`.


## Boundaries

Alcance: hacer el modelo legible para una IA — descripciones `///`, sinonimos,
nombres de negocio, AI instructions, verified answers, que se expone y que se
oculta.
Fuera de alcance: escribir o corregir las medidas → **powerbi-modelado-dax**.
Rendimiento de las consultas que genera la IA → **powerbi-rendimiento**.
Preparar para IA no arregla un modelo mal construido: si la estrella esta mal,
Copilot respondera mal con sinonimos perfectos.

Fundamento: Microsoft Learn ("Prepare your data for AI", "Copilot semantic models"),
SQLBI (descripciones/nombres).
