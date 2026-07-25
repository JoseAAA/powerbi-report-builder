---
name: powerbi-mvp
description: >
  Fase 6 — MVP rapido: datos de ejemplo + .pbip base. USAR cuando el usuario
  quiere "datos de ejemplo", "un .pbip base", "arrancar ya sin la fuente real",
  un proyecto Power BI minimo para abrir y modificar, un MVP o una demo.
---

# Fase 6 — MVP rapido (datos de ejemplo + .pbip que los lee)

Objetivo: que el usuario abra algo real en minutos y pueda **iterar sobre los
datos** sin esperar la fuente definitiva.

## Un solo comando (la via recomendada)

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/init_proyecto.py" --nombre "<X>" --dominio <ventas|rrhh|finanzas|salud|generico> --marca <m>|--tema <t>|--sin-marca
```

Genera el proyecto con el `.pbip` **en la raiz**, `datos/` con los CSV y `docs/`
con el tema y las plantillas del proceso. Las particiones del modelo **leen esos
CSV**, asi que abre → Actualizar → datos en pantalla. Exige elegir el tema: los
colores del usuario nunca se ignoran en silencio.

## El bucle de mockup rapido (dile esto al usuario)

1. Abre el `.pbip`, pulsa **Actualizar**.
2. ¿Falta un campo, sobra una categoria, los rangos no se parecen al negocio?
   **Edita el CSV** en `datos/` y vuelve a Actualizar.
3. Cuando la forma de los datos ya sirva, cambia el origen de cada tabla por la
   fuente real (→ **powerbi-datos-m**). Medidas y visuales siguen funcionando.

## Si llamas a los scripts por separado

`--datos` NO es opcional: es lo que conecta ambas mitades.

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/generar_datos_ejemplo.py" --salida datos --dominio <d>
python "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_pbip.py" --nombre "<R>" --dominio <d> --tema theme.json --datos datos --en-raiz
```

**Sin `--datos` el reporte muestra datos inline de muestra y los CSV quedan
huerfanos al lado** — el usuario corrige un CSV, refresca y no cambia nada.
`--tema` va SIEMPRE (generalo con **powerbi-marca**); omitelo solo si el usuario
acepta explicitamente los colores por defecto de Power BI.

## Antes de entregar

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_modelo.py"     <ruta .SemanticModel>   # R1-R12
python "${CLAUDE_PLUGIN_ROOT}/scripts/validar_pbip.py"       <ruta .Report>          # P1-P7
python "${CLAUDE_PLUGIN_ROOT}/scripts/verificar_cableado.py" <carpeta del proyecto>  # E1-E6
```

Los dos primeros validan las reglas del framework; **el tercero valida que el
proyecto describa algo coherente** (que el reporte lea los datos que hay al
lado). Un modelo puede pasar R1–R12 y P1–P7 y aun asi mostrar cifras falsas.

Avisa al usuario de que active **PBIR** una vez: *Archivo > Opciones >
Caracteristicas en vista previa > «Almacenar informes con el formato de metadatos
mejorado (PBIR)»* y reinicie. Sin eso, al guardar se pierde el detalle por
visual. Va tambien en el `LEEME.md` del proyecto.

## Cuando NO usar datos de ejemplo

- El usuario **ya tiene** la fuente accesible (Excel, SQL, SharePoint): ve
  directo a **powerbi-datos-m**. Un MVP sintetico seria un desvio.
- El usuario necesita cifras que pueda mostrar a un directivo: los datos de
  ejemplo son aleatorios. Dilo explicitamente, no dejes que se confundan con
  datos reales.

Detalle y como adaptar a un negocio: `${CLAUDE_PLUGIN_ROOT}/references/datos-ejemplo-y-m.md`.

Fundamento: Kimball (estrella), Power Query y PBIP/PBIR (Microsoft Learn).
