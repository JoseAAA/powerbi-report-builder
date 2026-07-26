# Contribuir

Gracias por mejorar este framework. Reglas cortas y no negociables:

1. **No inventar.** Toda "mejor práctica" nueva debe trazar a documentación de
   Microsoft o a un experto reconocido del área (Kimball, SQLBI/Tabular Editor
   BPA, Chris Webb, IBCS, WCAG). Sin fuente, no entra.
2. **Plantillas vivas.** Si cambias un criterio en `references/`, actualiza el
   encabezado `actualizado:`/`fuentes:` de ese archivo y anota el cambio en
   `CHANGELOG.md` (fecha · qué cambió · fuente). Ver
   `references/mantenimiento-de-plantillas.md`.
3. **Scripts solo con librería estándar** de Python (portabilidad, cero
   fricción de instalación). Salida de consola segura para Windows (UTF-8).
4. **Nada de datos privados** de ninguna empresa: ni marcas reales, ni rutas
   locales absolutas, ni caché `.pbi/` (el CI lo revisa).
5. **Verde antes del PR**: `python -m py_compile scripts/*.py`, y los
   validadores sobre los ejemplos (`validar_modelo.py` R1–R12 y
   `validar_pbip.py` P1–P8) deben pasar. Guía completa: `docs/pruebas.md`.
6. **Español neutro** en contenido orientado al usuario; términos técnicos
   estándar (measure, star schema, query folding) en su forma habitual.
