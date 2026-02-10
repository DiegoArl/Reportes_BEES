import pandas as pd

def leer_archivo(archivo):
    nombre = archivo.name.lower()

    if nombre.endswith(".csv"):
        return pd.read_csv(archivo, low_memory=False)
    elif nombre.endswith((".xlsx", ".xls")):
        return pd.read_excel(archivo)
    
    else:
        raise ValueError("Formato no soportado")

def leer_archivo_tareas(archivo):
    def separar_csv(df_tareas):
        df_tareas_2 = df_tareas.copy()
        df_tareas_2 = df_tareas.iloc[:, 0].str.split(";", expand=True)
        col = df_tareas.columns[0].split(";")
        df_tareas_2.columns= col
        return df_tareas_2
    
    df = leer_archivo(archivo)

    if df.shape[1] == 1 and ";" in df.columns[0]:
        df = separar_csv(df)

    return df

def leer_archivos_clasificados(archivos):
    CHECK_IN_KEYS = {
    "Nombre del Rep. Ventas",
    "Primer check-in",
    "Último check-out",
    "Ruta Efectiva"
    }

    VENTAS_KEYS = {
        "bdr_id",
        "Orders",
        "Total Revenue"
    }

    VISITAS_KEYS = {
        "Visitas planificadas",
        "Visitas completadas",
        "GPS Ok visitas"
    }
    df_checkin = None
    df_ventas = None
    df_visitas = None

    def limpiar_df(df):
        if df is None:
            return None
        if df.shape[1] >= 2:
            df = df.dropna(subset=[df.columns[1]])
        return df
    
    def separar_nombre_codigo(df):
        if df is None:
            return None
        df = df.copy()

        col = None
        if "Nombre del Rep. Ventas" in df.columns:
            col = "Nombre del Rep. Ventas"
        elif "Rep. Ventas" in df.columns:
            col = "Rep. Ventas"

        if not col:
            return df

        temp = df[col].str.split(" - ", n=1, expand=True)
        if temp.shape[1] == 1:
            temp[1] = None

        df.loc[:, "Rep. Ventas"] = temp[0]
        df.loc[:, "Codigo"] = temp[1].fillna(temp[0])

        if col != "Rep. Ventas":
            df = df.drop(columns=[col])

        nuevas = ["Codigo", "Rep. Ventas"]
        resto = [c for c in df.columns if c not in nuevas]
        df = df[nuevas + resto]

        return df
    
    for archivo in archivos:
        df = leer_archivo(archivo)

        cols = set(df.columns)

        if CHECK_IN_KEYS.issubset(cols):
            df_checkin = separar_nombre_codigo(limpiar_df(df))

        elif VENTAS_KEYS.issubset(cols):
            df_ventas = separar_nombre_codigo(limpiar_df(df))

        elif VISITAS_KEYS.issubset(cols):
            df_visitas = separar_nombre_codigo(limpiar_df(df))

    if df_checkin is None or df_visitas is None:
        raise ValueError("Faltan archivos obligatorios: Check-In o Visitas")

    return df_checkin, df_ventas, df_visitas