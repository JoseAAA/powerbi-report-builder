# Plan del reporte — Demo-Ventas

> **Esto es una propuesta, no el reporte.** Leela, dime que cambiar, y
> recien ahi lo construyo. Cambiar el plan cuesta un minuto; rehacer el
> reporte, una tarde.

**De que trata:** Comercial (Region / Producto / Ventas).

## 1. Que vamos a medir

| Indicador | Tipo |
|---|---|
| % Margen  ← **el principal** | Porcentaje |
| % Cumplimiento Meta | Porcentaje |
| Ticket Promedio | Absoluto |

**Por que importa el principal:** es el que abre el reporte y el que ven
las tarjetas. Si no es el correcto, dimelo ahora.

## 2. Como vamos a poder cortar la informacion

- **Region** — Cortar por region
- **Producto** — Cortar por producto (agrupado en Categoria Producto)
- **Indicador** — Elegir que se esta midiendo
- **Calendario** — Cortar por fecha

## 3. Las paginas y su historia

### Pagina 1: Resumen

*Para quien:* Quien decide y no explora: el estado actual y su porque.

**Como se lee:**

- Entras y lo primero que ves es **como vamos** (las tarjetas de arriba).
- Justo debajo, **si eso mejora o empeora** con el tiempo.
- Al lado, **quien lo explica**: que categorias tiran del resultado.
- Y abajo, **las cifras exactas** por si alguien las pide.

**Que va en la pagina:**

| Responde a | Se ve como |
|---|---|
| El mensaje de la pagina: la conclusion, no el tema | textbox |
| Elegir que indicador se esta mirando | slicer |
| Acotar el periodo | slicer |
| ¿Como vamos en % Margen? | cardVisual |
| ¿Y en el segundo indicador? | cardVisual |
| ¿Y en el tercero? | cardVisual |
| ¿Mejora o empeora con el tiempo? | lineChart |
| ¿Quien concentra el resultado y quien se queda atras? | clusteredBarChart |
| Las cifras exactas, para llevarselas | tableEx |

> *Nota de honestidad:* la **composicion** de esta pagina es
> propuesta nuestra — Microsoft no publica arquetipos de pagina con
> nombre. Lo que si esta respaldado es la eleccion de cada grafico
> (ver seccion 5) y los principios de composicion:
> Lo mas importante arriba-izquierda (LTR); slicers en la misma posicion en todas las paginas; un mensaje por pagina.

### Pagina 2: Detalle

*Para quien:* Quien viene a investigar: densidad alta aceptable.

**Como se lee:**

- Aqui vienes a investigar, no a mirar de reojo.
- La matriz cruza las dos dimensiones para que **encuentres la celda** que explica lo que viste en Resumen.
- Abajo, la **comparacion contra el periodo anterior**.

**Que va en la pagina:**

| Responde a | Se ve como |
|---|---|
| El mensaje de la pagina: la conclusion, no el tema | textbox |
| Elegir que indicador se esta mirando | slicer |
| Acotar por Region | slicer |
| ¿Que combinacion concreta explica el resultado? | pivotTable |
| ¿Como vamos contra el periodo anterior? | clusteredColumnChart |

> *Nota de honestidad:* la **composicion** de esta pagina es
> propuesta nuestra — Microsoft no publica arquetipos de pagina con
> nombre. Lo que si esta respaldado es la eleccion de cada grafico
> (ver seccion 5) y los principios de composicion:
> Slicers en la misma posicion que en la pagina anterior; Top N o el filtro mas restrictivo en tablas y matrices.

## 4. Lo que necesito que decidas

- [ ] ¿'% Margen' es de verdad el indicador que abre el reporte, o hay otro mas importante?
- [ ] ¿Los cortes por Region y Producto son los que usa tu negocio, o falta alguno?
- [ ] ¿Quien va a leer esto: alguien que decide (le basta Resumen) o alguien que investiga (necesita Detalle)?
- [ ] ¿Hay una meta u objetivo contra el que comparar? Sin meta, un numero solo dice 'cuanto', no 'si vamos bien'.

**El plan no se aprueba con casillas sin marcar.** Si algo no lo sabes
todavia, dimelo y lo dejamos anotado como supuesto explicito.

## 5. Por que cada grafico es ese y no otro

Ninguna eleccion es de gusto personal: cada una tiene su razon documentada.

| Grafico | Por que ese |
|---|---|
| `cardVisual` | Tarjeta cuando un solo numero es lo mas importante a seguir. Hay que darle contexto: un numero solo no dice si es bueno. |
| `clusteredBarChart` | Barras cuando los nombres de categoria son largos; comparar valores entre categorias es su punto fuerte. |
| `clusteredColumnChart` | Columnas para comparaciones temporales discretas. |
| `lineChart` | Linea enfatiza la forma de la serie en el tiempo y necesita eje X continuo. Con periodos sin dato la linea INVENTA tendencia: en ese caso, columnas. |
| `pivotTable` | Matriz para cruzar dos o mas dimensiones; soporta layout escalonado y drill por jerarquias. |
| `slicer` | Slicer para los filtros de uso frecuente, con el estado visible de un vistazo y en la MISMA posicion en todas las paginas. |
| `tableEx` | Tabla cuando hacen falta valores exactos y comparar muchas medidas de una sola categoria. Aplica Top N o el filtro mas restrictivo que permita la pregunta. |
| `textbox` | Cuadro de texto para el mensaje de la pagina. El titulo dice la conclusion, no el tema. |

Fuentes: Microsoft Learn (tipos de visual y guia de diseño), WCAG 2.2 para
accesibilidad, y el catalogo oficial de reglas de Microsoft para el modelo.

## 6. Que pasa cuando digas que si

1. Genero el proyecto con datos de ejemplo que **ya se ven** en el reporte.
2. Abres el `.pbip`, miras si la historia funciona, y corriges los datos.
3. Cuando la forma te sirva, cambiamos el origen por tus datos reales.

Los datos de ejemplo son **aleatorios**: sirven para validar la forma, no
para mostrarlos a nadie como si fueran tu negocio.
