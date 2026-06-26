# Cómo probar el framework

Guía de pruebas en **3 niveles**. Requisitos: Python 3.8+ (solo librería estándar).
Nivel 2: Power BI Desktop (marzo 2026+). Nivel 3: Claude Code.

> Windows: usa una carpeta de salida corta (p. ej. `C:\demo`) — rutas muy profundas
> topan con el límite MAX_PATH (260 caracteres).

---

## Nivel 1 — Los scripts (sin instalar nada)

Desde la raíz del repo:

```bash
# 1) Marca -> theme.json (valida contraste WCAG)
python scripts/generar_theme.py --marca assets/marca/ejemplos/ejemplo-corporativo.json --salida C:/demo/theme.json
#    Esperado: "OK ... contraste texto/fondo: ... (AA OK)"

# 2) Editar un theme existente (quirúrgico)
python scripts/editar_theme.py --archivo C:/demo/theme.json --modo oscuro --primario "#1E8449"
#    Esperado: lista "antes → después" + re-chequeo WCAG [OK]

# 3) Código Power Query M por fuente (parametrizado, folding-friendly)
python scripts/generar_conexion_m.py --fuente sql --servidor pServidor --base Ventas --esquema dbo --tabla vw_Ventas
#    Esperado: bloque "let ... in" + sección "PARAMETROS a crear"

# 4) Datos de ejemplo multi-dominio
python scripts/generar_datos_ejemplo.py --dominio ventas --salida C:/demo/datos
#    Esperado: 4 CSV + modelo-ejemplo.m + "Integridad referencial: OK".
#    La RutaBase del .m es un PLACEHOLDER (sin rutas locales); la consola sugiere la real.

# 5) Bootstrap de un proyecto completo — EXIGE elegir el tema (sin defaults silenciosos)
python scripts/init_proyecto.py --nombre "Demo" --dominio ventas --marca assets/marca/ejemplos/ejemplo-corporativo.json --salida C:/demo
#    Variantes: --tema theme.json | --sin-marca (neutro EXPLÍCITO)
#    Sin elección → error con instrucciones (así nunca se ignoran tus colores).

# 6) Validar modelo (R1–R11) y reporte (P1–P7)
python scripts/validar_modelo.py "C:/demo/proyecto-demo/06-mvp/Demo/Demo.SemanticModel"
python scripts/validar_pbip.py   "C:/demo/proyecto-demo/06-mvp/Demo/Demo.Report"
#    Esperado: "OK  Sin hallazgos ..." (exit 0)
```

### Bonus — el validador SÍ detecta fallas

```bash
mkdir -p C:/demo/malo
printf 'table Ventas\n\tcolumn Importe\n\t\tdataType: int64\n\t\tsummarizeBy: sum\n\n\tmeasure Margen = SUM(Ventas[Util]) / SUM(Ventas[Ingreso])\n' > C:/demo/malo/Ventas.tmdl
python scripts/validar_modelo.py C:/demo/malo
#    Esperado: R3 (ALTA), R1, R8... y exit=1
```
Y para el reporte: borra `themeCollection` de un `report.json` → `validar_pbip.py`
debe reportar **P7 [ALTA]** ("tema no cableado: los colores NO se aplican").

### Seguridad
```bash
python scripts/scaffold_pbip.py --nombre "../fuera" --dominio ventas --salida C:/demo
#    Esperado: ERROR de --nombre inválido (no escribe fuera de --salida)
```

---

## Nivel 2 — El dashboard en Power BI Desktop

1. Abre `example/proyecto-demo-ventas/06-mvp/Demo-Ventas/Demo-Ventas.pbip`.
2. Pulsa **Actualizar ahora** si lo pide (la tabla calculada `_ Medidas` se llena).
3. Verifica: modelo estrella (Calendario + Region + Producto + Ventas), tarjeta
   `Indicador %` y barras por Producto **con los colores del tema** (azul navy
   `#1B4D77` como color 1), y sin tablas `LocalDateTable_`.

---

## Nivel 3 — El asistente (skills)

1. Instala el plugin:
   `/plugin marketplace add <ruta-o-URL-del-repo>` →
   `/plugin install powerbi-report-builder@powerbi-report-builder-marketplace`
2. Prueba: *"Quiero un dashboard de ventas"* · *"Audita este PBIP"* ·
   `/powerbi-report-builder:powerbi-mvp`.
3. Evals en `evals/evals.json`: pasa los prompts y compara con `expected_output`.

## Checklist

- [ ] Nivel 1 completo: 8 scripts corren; validadores OK en limpio y detectan en malo.
- [ ] Nivel 2: el `.pbip` abre, colores del tema aplicados.
- [ ] Nivel 3: el plugin enruta por perfil/nivel y respeta los colores del usuario.
