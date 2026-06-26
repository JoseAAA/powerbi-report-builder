// ===========================================================================
// modelo-ejemplo.m  —  Power Query M para un MVP de modelo estrella
//
// COMO USARLO:
//   1) En Power BI Desktop: Inicio > Transformar datos > Editor avanzado.
//   2) Crea una consulta en blanco POR CADA tabla y pega su bloque.
//      (Cada bloque empieza en "let" y termina en "in <Paso>".)
//   3) Ajusta RutaBase si moviste los CSV.
//
// Convencion: nombres de negocio con espacios, sin prefijos dim_/fact_.
// Tablas: Calendario, Sede, Servicio, Indicadores (el hecho).
//
// La variante SharePoint (Excel.Workbook(Web.Contents(...))) esta INCLUIDA
// COMENTADA al inicio de cada bloque para que la actives cuando migres.
//
// ANTES DE PEGAR: crea una consulta/parametro llamado RutaBase con el valor de
// abajo (Inicio > Administrar parametros, o una consulta en blanco
//   RutaBase = "..."  ). Todos los bloques la referencian.
//   RutaBase = "C:\\CAMBIA-ESTA-RUTA\\datos-ejemplo"
// ===========================================================================


// ---------------------------------------------------------------------------
// TABLA: Calendario
// ---------------------------------------------------------------------------
// IMPORTANTE (modelo de datos):
//   - Marca esta tabla como "Tabla de fecha" usando [Fecha].
//   - Apaga Auto date/time: Archivo > Opciones > Carga de datos.
let
    // --- Variante SharePoint (comentada): descomenta al conectar la fuente real ---
    // url_archivo = "https://<tu-sitio>.sharepoint.com/.../Calendario.xlsx",
    // Origen = Excel.Workbook(Web.Contents(url_archivo), null, true),
    // Hoja = Origen{[Item="Calendario",Kind="Sheet"]}[Data],
    // EncabezadosPromovidos = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),

    // --- Fuente CSV de ejemplo ---
    Origen = Csv.Document(
        File.Contents(RutaBase & "\Calendario.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    EncabezadosPromovidos = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(EncabezadosPromovidos, {
        {"Fecha", type date},
        {"Anio", Int64.Type},
        {"Mes", type text},
        {"NumMes", Int64.Type},
        {"Trimestre", type text},
        {"EsDiaHabil", type text}
    })
in
    #"Tipo cambiado"


// ---------------------------------------------------------------------------
// TABLA: Sede
// ---------------------------------------------------------------------------
let
    // --- Variante SharePoint (comentada): descomenta al conectar la fuente real ---
    // url_archivo = "https://<tu-sitio>.sharepoint.com/.../Sede.xlsx",
    // Origen = Excel.Workbook(Web.Contents(url_archivo), null, true),
    // Hoja = Origen{[Item="Sede",Kind="Sheet"]}[Data],
    // EncabezadosPromovidos = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),

    // --- Fuente CSV de ejemplo ---
    Origen = Csv.Document(
        File.Contents(RutaBase & "\Sede.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    EncabezadosPromovidos = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(EncabezadosPromovidos, {
        {"ID Sede", Int64.Type},
        {"Sede", type text}
    })
in
    #"Tipo cambiado"


// ---------------------------------------------------------------------------
// TABLA: Servicio
// ---------------------------------------------------------------------------
let
    // --- Variante SharePoint (comentada): descomenta al conectar la fuente real ---
    // url_archivo = "https://<tu-sitio>.sharepoint.com/.../Servicio.xlsx",
    // Origen = Excel.Workbook(Web.Contents(url_archivo), null, true),
    // Hoja = Origen{[Item="Servicio",Kind="Sheet"]}[Data],
    // EncabezadosPromovidos = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),

    // --- Fuente CSV de ejemplo ---
    Origen = Csv.Document(
        File.Contents(RutaBase & "\Servicio.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    EncabezadosPromovidos = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(EncabezadosPromovidos, {
        {"ID Servicio", Int64.Type},
        {"Servicio", type text},
        {"Servicio Agrupado", type text}
    })
in
    #"Tipo cambiado"


// ---------------------------------------------------------------------------
// TABLA: Indicadores
// ---------------------------------------------------------------------------
let
    // --- Variante SharePoint (comentada): descomenta al conectar la fuente real ---
    // url_archivo = "https://<tu-sitio>.sharepoint.com/.../Indicadores.xlsx",
    // Origen = Excel.Workbook(Web.Contents(url_archivo), null, true),
    // Hoja = Origen{[Item="Indicadores",Kind="Sheet"]}[Data],
    // EncabezadosPromovidos = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),

    // --- Fuente CSV de ejemplo ---
    Origen = Csv.Document(
        File.Contents(RutaBase & "\Indicadores.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    EncabezadosPromovidos = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(EncabezadosPromovidos, {
        {"Fecha", type date},
        {"ID Sede", Int64.Type},
        {"ID Servicio", Int64.Type},
        {"ID Indicador", Int64.Type},
        {"Num", Int64.Type},
        {"Den", Int64.Type}
    }),
    // Filas filtradas: descarta registros sin denominador (evita dividir por 0).
    #"Filas filtradas" = Table.SelectRows(#"Tipo cambiado", each [Den] <> null and [Den] > 0)
in
    #"Filas filtradas"
