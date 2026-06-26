# Seguridad

## Reportar una vulnerabilidad

Abre un *issue* privado (GitHub → Security → Report a vulnerability) o contacta
a los mantenedores. No publiques detalles explotables en issues públicos.

## Alcance y principios de este proyecto

- Los scripts son **herramientas locales de generación/validación** (solo
  librería estándar de Python); no abren puertos ni hacen llamadas de red.
- Entradas de usuario que se convierten en rutas/carpetas están **sanitizadas**
  (p. ej. `--nombre` rechaza separadores de ruta y `..`).
- El repo **no debe contener datos privados**: ni marcas/reportes reales de
  empresas, ni rutas locales con nombres de usuario, ni caché `.pbi/`
  (`.gitignore` + chequeo en CI).
- Credenciales de fuentes de datos **nunca** van en código M ni en el repo:
  usa parámetros y el almacén de credenciales del Power BI Service/gateway.
