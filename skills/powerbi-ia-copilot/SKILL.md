---
name: powerbi-ia-copilot
description: >
  Preparar un modelo semantico de Power BI para IA y Copilot. USAR cuando el
  usuario quiere que Copilot/Q&A respondan bien sobre su modelo, menciona "preparar
  datos para IA", "Prep data for AI", "Approved for Copilot", sinonimos,
  descripciones de medidas, AI instructions o verified answers, o cuando el modelo
  lo va a consumir un agente LLM/MCP.
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

Fundamento: Microsoft Learn ("Prepare your data for AI", "Copilot semantic models"),
SQLBI (descripciones/nombres).
