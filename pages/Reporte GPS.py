import streamlit as st
import pandas as pd
from Scripts.carga import leer_archivos_clasificados, leer_archivo_tareas, leer_archivo
from Scripts.indicador_gps import unir_tablas, aplicar_estilos

st.set_page_config(
    page_title="Automatización de Reportería",
    layout="wide"
)

st.title("Reporte Indicador GPS Efectivo - Adopción - Alcance Tareas")


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


def todos_los_archivos_cargados():
    requeridos = [
        "usuarios",
        "df_checkin",
        "df_visitas"
    ]
    return all(k in st.session_state for k in requeridos)


st.header("Cargar archivos BEES ONE")

cargar_archivo(
    "Sube archivo de usuarios",
    "usuarios_file",
    "usuarios",
    leer_archivo
)

if "usuarios" in st.session_state:
    mostrar_preview(st.session_state.usuarios, "Usuarios")

archivos_bees = st.file_uploader(
    "Sube archivos gps-visitas-venta",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    key="bees_files"
)

if archivos_bees:
    try:

        df_checkin, df_ventas, df_visitas = leer_archivos_clasificados(archivos_bees)

        st.session_state.df_checkin = df_checkin
        st.session_state.df_ventas = df_ventas
        st.session_state.df_visitas = df_visitas

        st.success("Archivos identificados correctamente")

    except Exception as e:
        st.error(str(e))



st.divider()

if st.button(
    "Procesar Reporte Diario",
    disabled=not todos_los_archivos_cargados(),
    key="btn_procesar_reporte"
):

    df_resultado = unir_tablas(
        st.session_state.usuarios,
        st.session_state.df_checkin,
        st.session_state.df_visitas
    )

    st.subheader("Resultado GPS")
    styled_df = aplicar_estilos(df_resultado)

    st.dataframe(
        styled_df,
        use_container_width=True
    )