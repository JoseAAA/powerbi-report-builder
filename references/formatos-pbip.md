# Formatos del proyecto Power BI (PBIP / TMDL / PBIR)

> Plantilla viva · actualizado 2026-06 · fuentes: Microsoft Learn (PBIP/TMDL/PBIR); microsoft/powerbi-desktop-samples · ver `mantenimiento-de-plantillas.md`

Lee este archivo SIEMPRE antes de editar archivos de un proyecto PBIP.

## Contexto rápido

- **PBIP** (Power BI Project) es el formato de guardado basado en carpetas y
  texto plano. Reemplaza al .pbix binario para desarrollo con Git.
- **PBIR** (enhanced report format) es **default desde enero 2026** en Power BI
  Desktop y Service (los reportes nuevos se guardan en PBIR y los existentes se
  convierten al editarlos). Sigue en **preview**; la **GA está planificada para
  Q3 2026**, cuando PBIR pasará a ser el único formato soportado. _Fuente: Power BI
  blog — "PBIR will become the default report format"._
- **TMDL** (Tabular Model Definition Language): el modelo semántico como
  archivos de texto, uno por tabla/rol/perspectiva/cultura.
- **PBIR** (enhanced report format): el reporte como JSONs individuales por
  página, visual y bookmark, con JSON schema público por archivo.

## Estructura de carpetas

```
MiReporte.pbip                      ← manifiesto del proyecto
MiReporte.Report/
├── definition.pbir                 ← descriptor: versión + conexión al modelo
├── definition/
│   ├── report.json                 ← config global del reporte (tema activo aquí)
│   ├── version.json
│   ├── pages/
│   │   ├── pages.json              ← orden y página activa
│   │   └── <nombrePagina>/
│   │       ├── page.json           ← nombre visible, tamaño, displayOption
│   │       └── visuals/
│   │           └── <nombreVisual>/
│   │               └── visual.json ← tipo, posición, campos, formato
│   └── bookmarks/...
├── StaticResources/
│   └── RegisteredResources/        ← imágenes, temas custom (json), íconos
MiReporte.SemanticModel/
├── definition.pbism
├── definition/
│   ├── model.tmdl                  ← propiedades del modelo, annotations
│   ├── database.tmdl
│   ├── expressions.tmdl            ← parámetros y expresiones M compartidas
│   ├── relationships.tmdl          ← TODAS las relaciones
│   ├── cultures/...
│   └── tables/
│       ├── Ventas.tmdl             ← un archivo por tabla (columnas, medidas,
│       └── Calendario.tmdl            particiones con su query M)
└── .pbi/                           ← cache local, NO editar ni versionar
```

## Qué archivo tocar según la tarea

| Tarea | Archivo |
|---|---|
| Agregar/editar una medida | `tables/<Tabla>.tmdl` (bloque `measure`) |
| Crear relación | `relationships.tmdl` |
| Cambiar query M de una tabla | bloque `partition` dentro de `tables/<Tabla>.tmdl` |
| Mover/redimensionar un visual | `pages/<pag>/visuals/<vis>/visual.json` → `position` |
| Cambiar título de visual | `visual.json` → `visual.visualContainerObjects.title` |
| Renombrar página (nombre visible) | `page.json` → `displayName` |
| Orden de páginas | `pages/pages.json` → `pageOrder` |
| Tema del reporte | colocar el json en `StaticResources/RegisteredResources/` y referenciarlo en `report.json` → `themeCollection.customTheme` |

## Reglas de seguridad (no corromper el proyecto)

1. **Nunca cambies la propiedad `name`** (el identificador interno de ~20
   caracteres) de páginas, visuales o bookmarks: rompe bookmarks, filtros
   y referencias externas. `displayName` sí es editable.
2. **Respeta el `$schema`** declarado al inicio de cada JSON PBIR. No
   agregues propiedades que no existan en ese schema: Desktop valida los
   archivos al abrir y puede rechazar el reporte.
3. **JSON siempre válido**: valida con `python -m json.tool` después de
   editar.
4. **TMDL es sensible a indentación** (estilo YAML, tabs): las propiedades
   de un objeto van un nivel dentro; los bloques `measure`, `column`,
   `partition` van dentro de `table`. Deja una línea en blanco entre
   objetos hermanos. No mezcles tabs y espacios en el mismo archivo;
   respeta el estilo del archivo existente.
5. **Expresiones DAX multilinea en TMDL** van indentadas bajo el `=` con
   sangría adicional consistente (ver fase 4).
6. **No edites `.pbi/`** (cache) ni `localSettings.json`.
7. Después de editar, el usuario abre el `.pbip` en Power BI Desktop; si
   algo no carga, Desktop indica el archivo problemático. Recomienda commit
   en Git ANTES de cualquier edición masiva.

## Qué es FIJO y qué VARÍA en un PBIP (clona, no inventes)

Regla de oro para no corromper: parte de un PBIP que **ya abre bien** y cambia
SOLO los campos variables; nunca quites propiedades requeridas ni inventes nuevas.

| FIJO — clona exacto | VARÍA — esto sí editas |
|---|---|
| `$schema` y `version` de cada archivo; `compatibilityLevel` | `displayName` de páginas/reporte |
| La forma de los objetos requeridos (sus propiedades obligatorias) | datos (inline/M), nombres de tablas/columnas/medidas |
| La propiedad interna `name` (~20 chars) de página/visual/bookmark | `position` de visuales, `pageOrder` |
| Estructura del modelo (relaciones, particiones) | paleta del theme, títulos, `formatString` |

**Propiedades requeridas que NO se pueden omitir** (si faltan → "El informe tiene
problemas que no se pudieron resolver" al abrir):
- `themeCollection.customTheme` y `baseTheme` son `ThemeMetadata` → requieren
  **`name` + `reportVersionAtImport` (con `visual`/`page`/`report`) + `type`**.
  Omitir `reportVersionAtImport` corrompe el report.json. *(Schema oficial report/3.x.)*
- Cada `visual.json` / `page.json` requiere su `$schema` y su `name`.
- `pages.json`: `activePageName` debe existir dentro de `pageOrder`.

**Cómo saber qué es requerido sin adivinar:** abre el `$schema` que declara el
archivo (URL oficial de Microsoft) y revisa sus `required`. Eso ES "la documentación
oficial": edita solo lo que el schema marca como variable; el resto se clona tal cual.

## Snippets de referencia

### Medida en TMDL (dentro de tables/X.tmdl)

```tmdl
	/// Ingreso facturado del periodo (sin impuestos). Medida principal de ventas.
	measure 'Ventas Totales' = SUM(Ventas[Importe])
		formatString: #,0
		displayFolder: 01 Ventas

	measure 'Ventas YTD' = ```
			VAR _resultado =
			    TOTALYTD([Ventas Totales], 'Calendario'[Fecha])
			RETURN
			    _resultado
			```
		formatString: #,0
		displayFolder: 01 Ventas
```

(Nota: el bloque ``` dentro de TMDL delimita expresiones multilinea.)

**Descripciones en TMDL**: van con un comentario **`///` en la línea inmediatamente
encima** del objeto (tabla/medida/columna), SIN línea en blanco entre el `///` y el
objeto. Es la sintaxis oficial (no existe una propiedad `description:`). Evita los
comentarios `//` sueltos. _(Fuente: Microsoft Learn — TMDL overview.)_

### Posición de un visual (visual.json)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.0.0/schema.json",
  "name": "a1b2c3d4e5f6a7b8c9d0",
  "position": { "x": 40, "y": 100, "width": 580, "height": 320, "z": 1 }
}
```

El lienzo estándar es 1280×720 px (16:9). Usa una grilla de 8 px para
posiciones consistentes.
