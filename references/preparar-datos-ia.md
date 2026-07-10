# Preparar el modelo para IA / Copilot (semantic model AI-ready)

> Plantilla viva · actualizado 2026-07 · fuentes: Microsoft Learn ("Prepare your data for AI", "Copilot semantic models"); SQLBI (naming/descriptions) · ver `mantenimiento-de-plantillas.md`

Objetivo: que el modelo dé **buenas respuestas cuando lo consulta una IA** — Copilot
de Power BI, pero también los **agentes LLM/MCP** que este framework asume como
consumidores. La regla del proyecto (el modelo es la fuente de verdad, editable
por LLM/MCP) exige que el modelo esté escrito para que una IA lo entienda sin
adivinar. Un modelo bien preparado para IA **es** un modelo bien hecho: los mismos
metadatos ayudan a la persona y a la máquina.

> Importante: ninguna de estas funciones garantiza una salida exacta — la IA es no
> determinista. Preparar los datos **sube la probabilidad** de respuestas correctas
> y aterrizadas, no la asegura.

## 1. Fundamento del modelo (lo que más pesa)

Antes que cualquier función de IA, el modelo tiene que estar limpio. Microsoft lo
dice explícito en la guía de Copilot:

- **Estrella** (ver `fase4-modelado.md`): relaciones claras, sin ambigüedad, sin
  muchos-a-muchos evitables. La IA se pierde con modelos enredados.
- **Nombres únicos y de negocio** (ver `nomenclatura.md`): no repitas el mismo
  nombre de campo en varias tablas ("Nombre" en Cliente y en Producto confunde a
  Copilot). Usa el término que usa el negocio.
- **Oculta lo técnico**: claves, columnas Num/Den, tablas de medidas. Lo oculto no
  distrae a la IA ni al usuario (`isHidden`).
- **Quita lo que no se usa**: tablas, columnas y medidas muertas. Menos superficie
  = menos ambigüedad.
- **Una medida por concepto** con `formatString` (la IA respeta el formato al
  responder).

## 2. Metadatos que la IA lee (el gran diferenciador)

### Descripciones (`description`) — lo primero que hay que hacer

Cada **medida**, **tabla** y **columna** visible debería tener una descripción:
una frase de negocio que explique qué es y cuándo usarla. Es el metadato que más
usa Copilot para desambiguar, y es exactamente lo que un agente LLM lee del TMDL.

En TMDL la descripción se escribe con un comentario **`///` en la línea
inmediatamente encima del objeto** (sintaxis oficial; NO uses `description:` como
propiedad). No dejes línea en blanco entre el `///` y el `measure`:

```tmdl
	/// Cumplimiento del presupuesto de ventas del periodo. Positivo = sobre plan; negativo = bajo plan. Usar con el filtro de mes.
	measure 'Ventas vs Ppto %' = DIVIDE([Ventas] - [Presupuesto], [Presupuesto])
		formatString: 0.0%;-0.0%;0.0%
		displayFolder: 02 Comparaciones
```

- El validador `validar_modelo.py` marca **R12** las medidas sin `///` descripción.
- El `scaffold_pbip.py` ya genera las medidas base con su `///`.
- Escríbelas en lenguaje de negocio, no repitiendo el DAX ("suma de importe" no
  aporta; "ingreso facturado sin IGV del periodo" sí).
- **Límite de Copilot**: lee solo los **primeros ~200 caracteres** de la descripción
  — pon lo esencial al inicio. _(Microsoft, guía de AI-readiness.)_

### Sinónimos y modelado lingüístico (Q&A / Copilot)

Si el negocio llama a lo mismo de varias formas ("Ventas", "Facturación",
"Ingresos"), regístralo como **sinónimo** para que la IA lo reconozca. En Power BI:
**Modelado → Q&A / Sinónimos** (linguistic schema). También puedes definir verbos
para relaciones ("un cliente **compra** productos"). Es requisito para que Q&A y
Copilot respondan con el vocabulario real del usuario.

## 3. "Prep data for AI" — las 3 funciones oficiales (Power BI, preview)

Microsoft agrupa la preparación en un botón **Prep data for AI** (Power BI Desktop
y Service), con tres funciones. Se guardan **en el semantic model**, no en el
reporte, y requieren **Q&A habilitado** en el modelo:

| Función | Qué es | Cuándo usarla |
|---|---|---|
| **AI instructions** | Instrucciones en lenguaje natural a nivel de modelo: contexto de negocio, terminología, prioridades analíticas, qué evitar. Tope ~**10.000 caracteres**. | Siempre que haya reglas de negocio o jerga que la IA deba respetar. |
| **AI data schemas** | Subconjuntos curados del modelo (qué tablas/campos exponer para una intención) para reducir ambigüedad. | Modelos grandes: acota lo que la IA "ve" por tema. |
| **Verified answers** | Fijas un visual como respuesta aprobada para ciertas frases-gatillo. | Preguntas frecuentes con una respuesta canónica (evita que la IA improvise). |

Ambos, AI instructions y AI data schemas, se guardan en el **LSDL** del modelo y se
pueden editar. Tras publicar por Git/pipelines, **refresca el modelo** en el
Service para sincronizar los cambios de LSDL/tooling.

En un proyecto **PBIP en disco**, estos artefactos viven en una carpeta `Copilot/`
dentro de `<Reporte>.SemanticModel/definition/` (o del modelo): típicamente
`instructions.md` (AI instructions), `schema.json` (AI data schema), `settings.json`,
`examplePrompts.json` y `VerifiedAnswers/`. Son texto/JSON, versionables en Git como
el resto del PBIP. _(Estructura observada en el repo oficial microsoft/skills-for-fabric.)_

## 4. Marcar el modelo "Approved for Copilot"

Cuando el modelo está preparado y probado, márcalo en el Service:
**Semantic model → Settings → Approved for Copilot** (antes "prepped for AI"). Así
Copilot deja de aplicar "friction treatment" a sus respuestas y los reportes sobre
ese modelo quedan aprobados. Los cambios tardan hasta ~1 h (o 24 h con muchos
reportes) en reflejarse.

> Prerrequisitos: workspace habilitado para Copilot y **Q&A activado** en el modelo.
> Desktop soporta estas funciones para Import, DirectQuery y Composite (local); en
> el Service, para todos los tipos de modelo.

## 5. Probar antes de publicar

En Power BI Desktop, usa el **panel de Copilot** y el **skill picker** (Answer
questions / Analyze report visuals / Create report pages) para simular lo que verá
el usuario. Revisa **"How Copilot arrived at this" (HCAAT)** y descarga diagnósticos
desde el menú `...` del panel. Itera: cada cambio en "Prep data for AI" se ve al
cerrar y reabrir el panel.

## Checklist AI-ready (revísalo antes de entregar)

- [ ] Estrella limpia, sin relaciones ambiguas ni m-a-m evitables.
- [ ] Nombres de negocio, únicos entre tablas; técnico oculto; muerto eliminado.
- [ ] **Descripción `///` en cada medida** (R12) y en tablas/columnas clave (lo
      esencial en los primeros ~200 caracteres).
- [ ] `formatString` en toda medida.
- [ ] Sinónimos para los términos con varios nombres; verbos en relaciones clave.
- [ ] (Si hay Copilot) AI instructions + al menos las verified answers frecuentes.
- [ ] Q&A habilitado y modelo **Approved for Copilot**.

## Fuentes

- Microsoft Learn — *Prepare your data for AI to improve Copilot results*:
  https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai
- Microsoft Learn — *AI instructions*:
  https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-instructions
- Microsoft Learn — *Use Copilot with semantic models (prepare your model)*:
  https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models
- Microsoft Learn — *Tutorial: prepare a semantic model for Copilot*:
  https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model
- Descripciones/nombres: `references/nomenclatura.md` (SQLBI, Tabular Editor, Chris Webb).
