---
name: powerbi-actualizar
description: >
  USAR cuando el usuario pregunta "¿hay novedades de Power BI?", "¿el catalogo
  esta al dia?", "actualiza las reglas", "¿salio algo nuevo de Microsoft?",
  "¿esto sigue siendo verdad?", o cuando detectas en un proyecto algo que el
  catalogo no contempla (una propiedad de tema desconocida, un visual nuevo, una
  funcion DAX que no reconoces). Tambien como rutina mensual. NO usar para
  auditar un proyecto concreto (eso es powerbi-auditoria) ni para actualizar el
  plugin en si.
---

# Mantener el catalogo al dia con las fuentes oficiales

Objetivo: que "todo sustentado en documentacion oficial y **actualizada**" tenga
un mecanismo, no solo una buena intencion. Las 15 fuentes que respaldan el
catalogo estan declaradas en `${CLAUDE_PLUGIN_ROOT}/scripts/fuentes.py` con su
TTL, y su estado en `references/estado-fuentes.json`.

## Procedimiento

**0. TTL — no gastes cuota en vano.** Cada fuente declara su propio TTL (7 dias
las que se mueven mucho como `create-reports`, 30 las normales, 90 las casi
inmoviles como la spec de TMDL). Una ejecucion normal solo consulta las
vencidas. Si el usuario no pidio el chequeo explicitamente y no hay nada
vencido, responde "catalogo al dia" y termina.

**1. Detectar cambios** (1 llamada HTTP publica por fuente, sin credenciales):

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/actualizar_catalogo.py"
```

- exit 0 → catalogo al dia. Informa y termina.
- exit 1 → hay cambios: sigue al paso 2.
- exit 2 → error de red o cuota agotada (GitHub da 60 llamadas/hora sin token).
  Dilo y ofrece reintentar mas tarde. **No inventes un veredicto.**

Para el modo maquina: `--json` devuelve el contrato
`pbi-builder/actualizar-catalogo@1` con los mismos exit codes.

**2. Interpretar.** Por cada fuente con cambios, abre la URL que imprime el
script (o las paginas concretas con WebFetch) y clasifica:

| Lo que ves | Que suele significar |
|---|---|
| Pagina **nueva** | posible regla nueva, o una funcion/visual que el catalogo no cubre |
| Pagina **modificada** | ¿cambio la severidad, el arreglo o la URL de una regla existente? |
| Pagina **eliminada** | una regla puede haber quedado sin fuente → hay que recitar o retirar |
| Cambio cosmetico (typos, imagenes, metadata) | ignorar |

Fuentes con tratamiento especial:
- **`bpa_rules`**: es `BPARules.json`, las 71 reglas oficiales de Microsoft. Si
  cambia, el catalogo del modelo cambia con el; compara los `ID` uno a uno.
- **`theme_schema`**: los schemas se publican **versionados** y no hay URL
  "latest". Si aparece una version nueva, hay que fijarla en `SCHEMA_VERSION` de
  `generar_theme.py` — pero antes compara las props raiz del schema viejo y el
  nuevo: si el salto no es aditivo, puede invalidar temas ya generados.
- **`pbir_schemas`**: si sube la version de un schema de PBIR, **no cambies el
  `$schema` de los archivos existentes**. La regla oficial es copiar el `$schema`
  de un archivo hermano del mismo tipo y nunca inventar ni subir versiones.

**3. Proponer en lenguaje llano, y NO tocar nada sin el OK.** Resume: que cambio,
a que regla afecta, y que propones hacer. Una pagina nueva no implica una regla
nueva.

**4. Aplicar (solo tras el OK).** Actualiza el catalogo y su cita, corre los
validadores (`validar_modelo.py`, `validar_pbip.py`, `verificar_cableado.py`,
`check_consistencia.py`), y anota el cambio en `CHANGELOG.md` **con la fecha y la
fuente**.

**5. Cerrar el ciclo:**

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/actualizar_catalogo.py" --marcar-revisado
```

Sin este paso los contadores de TTL no se reinician y el siguiente chequeo vuelve
a reportar lo mismo.

## Jerarquia de autoridad de la fuente

Al citar, respeta el orden (`NIVELES_AUTORIDAD` en `fuentes.py`):

1. Documentacion oficial de Microsoft · 2. Repos oficiales de Microsoft ·
3. Estandar de un organismo (W3C/WCAG, IBCS) · 4. Experto reconocido (SQLBI,
Chris Webb, Tabular Editor) · 5. Otro.

**Una regla de severidad ALTA no puede sustentarse solo en un nivel 5.** Si tras
buscar no hay fuente oficial, dilo explicitamente: "no esta documentado
oficialmente" es una respuesta valida y correcta. Inventar no lo es.

## Lo que este mecanismo NO cubre (dilo si viene al caso)

- **Release plans y blogs oficiales** no estan en el vigilante: las olas de
  funcionalidad se anuncian ahi antes de llegar a la doc. Revision semestral
  manual: `learn.microsoft.com/power-platform/release-plan/` y el blog de Power BI.
- **Cambios de comportamiento sin cambio de doc.** Si el usuario reporta algo que
  contradice al catalogo, gana lo que el usuario observa: verificalo y registra
  la discrepancia.
- **Fechas de vigencia dentro de las paginas.** El vigilante detecta que un
  archivo cambio, no si la afirmacion que citas sigue en el. Al recitar, relee.

## Boundaries

Alcance: vigilar las fuentes oficiales, interpretar sus cambios y mantener el
catalogo y sus citas al dia. Termina con `--marcar-revisado`.
Fuera de alcance: auditar un proyecto concreto → **powerbi-auditoria**. Publicar
→ **powerbi-entrega**. Actualizar la version del plugin en si (eso es del repo,
no del catalogo).
**No modifica el catalogo sin aprobacion explicita del usuario**, y no consulta
la red si nada vencio salvo que se le pida.

Fundamento: patron de mantenimiento con TTL + gate humano de
JoseAAA/power-automate-architect (`pa-actualizar`); fuentes confirmadas contra la
API publica de GitHub.
