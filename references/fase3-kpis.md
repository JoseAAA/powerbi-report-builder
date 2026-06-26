# Fase 3 — Definición y validación de KPIs / OKRs

> Plantilla viva · actualizado 2026-06 · fuentes: OKR (Doerr/Google); Balanced Scorecard (Kaplan & Norton); Microsoft · ver `mantenimiento-de-plantillas.md`

Objetivo: convertir cada pregunta de negocio "Must" en una ficha de
indicador completa y validada contra los datos reales.

## KPI vs OKR (cómo tratarlos distinto)

- **KPI**: mide la salud continua de un proceso (rotación de inventario,
  % ocupación, días de cobranza). Vive permanentemente en el reporte.
- **OKR**: objetivo con resultados clave y fecha (Q/semestre). En el
  reporte se muestra como progreso hacia meta con fecha límite; al cumplirse
  el periodo, se archiva o renueva.
- Un OKR suele descomponerse en 2-4 KPIs que ya existen o se crean.

## La ficha de indicador (plantilla en assets/ficha-kpi.md)

Campos obligatorios — si el usuario no tiene alguno, pregúntalo; los dos
que NUNCA pueden faltar son **meta** y **dueño** (un indicador sin meta es
un dato decorativo; sin dueño, nadie actúa):

| Campo | Ejemplo |
|---|---|
| Nombre de negocio | % Entregas a tiempo |
| Definición en una frase | Proporción de OC entregadas en o antes de la fecha pactada |
| Fórmula conceptual | OC a tiempo / OC totales del periodo |
| Grain | Una fila por línea de orden de compra |
| Dimensiones de corte | Proveedor, categoría, sede, mes |
| Meta y semáforo | ≥95% verde; 90-95% ámbar; <90% rojo |
| Dueño | Jefe de Compras |
| Fuente | AX → tabla PurchLine + Vendor |
| Frecuencia de refresco | Diaria 6 AM |
| Pregunta de negocio que responde | (referencia a fase 2) |

## Validación contra los datos (el paso que casi todos se saltan)

Para CADA ficha, ejecutar esta verificación con el usuario:

1. ¿Existe la tabla/columna fuente exacta? (nombre real, no supuesto)
2. ¿La grain de la fuente coincide con la grain del indicador? (si el KPI
   es por línea de OC y la fuente está agregada por OC, hay gap)
3. ¿La columna clave tiene calidad? (nulos, duplicados, fechas imposibles —
   si el usuario puede correr un query, dale el SQL/M de perfilado)
4. ¿La historia disponible alcanza? (un YoY necesita ≥13 meses)

Veredicto por indicador:

- ✅ **Disponible** → pasa a fase 4.
- ⚠️ **Parcial** → pasa a fase 4 CON una nota de transformación requerida
  (ej. "derivar fecha pactada desde el campo X").
- ❌ **Sin datos** → NO pasa. Se documenta en la sección "Deuda de datos"
  del entregable con qué se necesitaría capturar y a quién pedírselo.

Sé directo con el usuario cuando un KPI esté en ❌: es mejor un reporte con
6 indicadores confiables que con 10 donde 4 muestran números inventables.

## Anti-patrones a frenar

- **KPI overload**: más de ~10 indicadores en la vista principal. Propón
  jerarquía: 3-5 estratégicos arriba, el resto en páginas de detalle.
- **Indicadores espejo**: "Ventas" y "Ventas sin IGV" como KPIs separados →
  es una medida con variante, no dos indicadores.
- **Metas heredadas sin dueño**: "siempre fue 95%" → preguntar quién la
  defiende hoy.
- **Promedios de promedios** en la fórmula conceptual → definir desde la
  grain correcta.
