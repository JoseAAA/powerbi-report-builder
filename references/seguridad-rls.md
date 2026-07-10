# Seguridad del modelo — RLS y OLS

> Plantilla viva · actualizado 2026-07 · fuentes: Microsoft Learn (RLS guidance, Fabric security); SQLBI/Tabular Editor · ver `mantenimiento-de-plantillas.md`

Objetivo: mostrar a cada usuario **solo los datos que le corresponden**, sin
duplicar reportes. Aplica en proyectos **intermedio/complejo** (varias áreas,
sedes, vendedores, clientes externos). Se define en el modelo (TMDL) y se asignan
miembros en el Power BI Service.

## Cuándo usar cada mecanismo

| Mecanismo | Qué oculta | Caso típico |
|---|---|---|
| **RLS** (Row-Level Security) | **Filas** según el usuario | cada gerente ve su sede; cada vendedor su cartera |
| **OLS** (Object-Level Security) | **Tablas o columnas** enteras | ocultar `Salario`, datos médicos, márgenes a ciertos roles |

RLS y OLS se complementan. OLS se edita con herramientas externas (Tabular Editor),
no desde Desktop.

## RLS estático (por rol)

Un rol = un filtro fijo. Simple cuando hay pocos grupos estables.

```tmdl
role Sede_Lima
	modelPermission: read

	tablePermission Sede = Sede[Sede] = "Lima"
```

Creas un rol por grupo (`Sede_Lima`, `Sede_Arequipa`…) y en el Service asignas
personas/grupos de seguridad a cada rol. Desventaja: no escala si hay muchos
grupos.

## RLS dinámico (recomendado) — un rol para todos

Un **solo rol** filtra distinto por persona, usando su identidad y una **tabla de
seguridad** (usuario → qué puede ver). Es el patrón preferido y el que mejor
escala, sobre todo con usuarios externos.

1. Agrega una tabla `Seguridad Usuario` (Usuario UPN, dimensión que controla —
   p. ej. `ID Sede`), relacionada con la dimensión correspondiente.
2. Define **un** rol con un filtro basado en `USERPRINCIPALNAME()`:

```tmdl
role Seguridad Dinamica
	modelPermission: read

	tablePermission 'Seguridad Usuario' = 'Seguridad Usuario'[Usuario UPN] = USERPRINCIPALNAME()
```

Con la relación `Seguridad Usuario → Sede → hecho`, el filtro se propaga y cada
quien ve lo suyo. `USERPRINCIPALNAME()` devuelve el UPN en el Service (usa
`USERNAME()` solo para pruebas locales).

## Buenas prácticas (Microsoft + SQLBI)

- **Filtra en la dimensión**, no en el hecho (más rápido; el filtro se propaga por
  la relación 1→*).
- **Sin columnas calculadas** en la expresión RLS; que la tabla de seguridad sea
  pequeña e indexada por el UPN.
- Verifica que las **relaciones** existan y estén en la dirección correcta; RLS mal
  propagado es la causa #1 de "veo todo / no veo nada".
- **Prueba real**: "Ver como rol" en Desktop usa TU identidad. Para RLS dinámico
  con usuarios **externos/invitados**, inicia sesión como ese usuario en el Service:
  es la única forma de confirmar que el UPN resuelve bien.
- Documenta cada rol (qué filtra, quién lo administra) — va en la doc del modelo.
- RLS **no** cifra datos ni protege el `.pbix`/PBIP en disco; es seguridad de
  consumo en el Service. Combínala con permisos de workspace/app.

## Dónde encaja en el flujo

- Se **modela** junto con la Fase 4 (relaciones ya definidas). Ver
  `references/fase4-modelado.md`.
- Se **asigna y prueba** en la Fase de entrega. Ver `references/entrega-git-y-mcp.md`.

## Fuentes

- Microsoft Learn — *Row-level security (RLS) guidance in Power BI Desktop*:
  https://learn.microsoft.com/en-us/power-bi/guidance/rls-guidance
- Microsoft Learn — *Restrict data access with RLS (Fabric security)*:
  https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security
- Tabular Editor — *Row-level security in Power BI semantic models*:
  https://tabulareditor.com/blog/row-level-security-in-power-bi-semantic-models
