import pandas as pd
import streamlit as st


class Cargador:

    CHECK_IN_KEYS = {"Nombre del Rep. Ventas", "Primer check-in", "Ruta Efectiva"}
    VENTAS_KEYS = {"bdr_id", "Orders", "Total Revenue"}
    VISITAS_KEYS = {"Visitas planificadas", "Visitas completadas", "GPS Ok visitas"}
    VISITAS_ALIAS = {
        "bdr_gps_ok": "GPS Ok visitas",
        "bdr_%_gps_ok": "% GPS Ok visitas",
        "bdr_gps_ok_2_min": "GPS Ok > 2 min Visitas",
        "bdr_%_gps_ok_2_min": "% GPS Ok > 2 min visitas"
    }

    @staticmethod
    def leer_archivo(archivo):
        archivo.seek(0)
        nombre = archivo.name.lower()
        if nombre.endswith(".csv"):
            return pd.read_csv(archivo, sep=None, engine="python")
        elif nombre.endswith((".xlsx", ".xls")):
            return pd.read_excel(archivo)
        raise ValueError("Formato no soportado")

    @staticmethod
    def leer_archivo_tareas(archivo):
        df = Cargador.leer_archivo(archivo)
        if df.shape[1] == 1:
            df = df.iloc[:, 0].str.split(";", expand=True)
        return df

    @staticmethod
    def _limpiar_df(df):
        if df is None:
            return None
        if df.shape[1] >= 2:
            df = df.dropna(subset=[df.columns[1]])
        return df

    @staticmethod
    def _separar_nombre_codigo(df):
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
        return df[nuevas + resto]

    @classmethod
    def leer_archivos_clasificados(cls, archivos):
        df_checkin = df_ventas = df_visitas = None

        for archivo in archivos:
            df = cls.leer_archivo(archivo)
            cols = set(df.columns)

            if any(c in cols for c in cls.VISITAS_ALIAS):
                df = df.rename(columns=cls.VISITAS_ALIAS)
                cols = set(df.columns)

            if cls.CHECK_IN_KEYS.issubset(cols):
                df_checkin = cls._separar_nombre_codigo(cls._limpiar_df(df))
            elif cls.VENTAS_KEYS.issubset(cols):
                df_ventas = cls._separar_nombre_codigo(cls._limpiar_df(df))
            elif cls.VISITAS_KEYS.issubset(cols):
                df_visitas = cls._separar_nombre_codigo(cls._limpiar_df(df))

        if df_checkin is None or df_visitas is None:
            raise ValueError("Faltan archivos obligatorios: Check-In o Visitas")

        return df_checkin, df_ventas, df_visitas

    @staticmethod
    def mostrar_preview(df, titulo):
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.subheader(titulo)
            st.write(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
            st.dataframe(df.head())

    @staticmethod
    def cargar_archivo(label, key_widget, key_data, lector):
        archivo = st.file_uploader(label, type=["csv", "xlsx"], key=key_widget)
        if archivo is None:
            if key_data in st.session_state:
                del st.session_state[key_data]
            return
        try:
            df = lector(archivo)
            st.session_state[key_data] = df
            st.success("Archivo subido correctamente")
        except Exception as e:
            st.error(f"Error al cargar archivo: {e}")
