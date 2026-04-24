import pandas as pd
import streamlit as st

def leer_archivo(archivo):
    archivo.seek(0)
    nombre = archivo.name.lower()
    if nombre.endswith(".csv"):
        return pd.read_csv(
            archivo,
            sep=None,
            engine="python"
        )
    elif nombre.endswith((".xlsx", ".xls")):
        return pd.read_excel(archivo)
    else:
        raise ValueError("Formato no soportado")

def mostrar_preview(df, titulo):
    if isinstance(df, pd.DataFrame) and not df.empty:
        st.subheader(titulo)
        st.write(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
        st.dataframe(df.head())


def cargar_archivo(label, key_widget, key_data, lector):

    archivo = st.file_uploader(
        label,
        type=["csv", "xlsx"],
        key=key_widget
    )

    if archivo is None:
        if key_data in st.session_state:
            del st.session_state[key_data]
        return

    try:
        df = lector(archivo)
        st.session_state[key_data] = df
        st.success("Archivo subido correctamente")

    except Exception as e:
        st.error(str(e))

def leer_archivo_tareas(archivo):
    df = leer_archivo(archivo)
    if df.shape[1] == 1:
        df = df.iloc[:,0].str.split(";", expand=True)

    return df

def leer_archivos_clasificados(archivos):
    CHECK_IN_KEYS = {
    "Nombre del Rep. Ventas",
    "Primer check-in",
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

    Visitas_alter_keys ={
        "bdr_gps_ok": "GPS Ok visitas", 
        "bdr_%_gps_ok": "% GPS Ok visitas",
        "bdr_gps_ok_2_min": "GPS Ok > 2 min Visitas",
        "bdr_%_gps_ok_2_min" : "% GPS Ok > 2 min visitas"
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

        if any(col in cols for col in Visitas_alter_keys.keys()):
            df = df.rename(columns=Visitas_alter_keys)
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