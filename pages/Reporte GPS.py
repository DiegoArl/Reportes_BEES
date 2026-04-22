import streamlit as st
import pandas as pd
from Scripts.carga import leer_archivos_clasificados, leer_archivo, leer_archivo_tareas, mostrar_preview, cargar_archivo
from Scripts.indicador_gps import unir_tablas, aplicar_estilos
from Scripts.indicador_adopcion import adopcion_tabla, aplicar_estilos_ado
from Scripts.indicador_tareas import tabla_tareas, aplicar_estilos_tareas
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.set_page_config(
    page_title="Automatización de Reportería",
    layout="wide"
)

st.title("Reporte Indicador GPS Efectivo")

def archivos_gps_cargados():
    requeridos = [
        "usuarios",
        "df_checkin",
        "df_visitas"
    ]
    return all(k in st.session_state for k in requeridos)

def archivos_tareas_cargados():
    requeridos = [
        "usuarios",
        "tareas"
    ]
    return all(k in st.session_state for k in requeridos)

def archivos_adopcion_cargados():
    requeridos = [
        "usuarios",
        "modulo"
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

c1, c2, c3 = st.columns(3)
with c1:
    archivos_bees = st.file_uploader(
        "Sube archivos GPS-visitas-venta",
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
with c2:
    cargar_archivo(
        "Sube archivo de Tareas",
        "tareas_file",
        "tareas",
        leer_archivo_tareas
    )

with c3:
    cargar_archivo(
        "Sube Módulo de Ventas",
        "modulo_file",
        "modulo",
        leer_archivo
    )

    if "modulo" in st.session_state:

        fecha_min = st.session_state.modulo["fecha"].min()
        fecha_max = st.session_state.modulo["fecha"].max()

        rango_fechas = st.date_input(
            "Rango de fechas",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max,
            key="rango_adopcion"
        )


st.divider()

if st.button(
    "Procesar Reporte Diario",
    disabled=not archivos_gps_cargados(),
    key="btn_procesar_reporte"
):

    df_resultado_gps = unir_tablas(
        st.session_state.usuarios,
        st.session_state.df_checkin,
        st.session_state.df_visitas
    )

    st.subheader("Resultado GPS")
    styled_df_gps = aplicar_estilos(df_resultado_gps)

    st.dataframe(
        styled_df_gps,
        width='stretch'
    )


if st.button(
    "Procesar Reporte Tareas",
    disabled=not archivos_tareas_cargados(),
    key="btn_procesar_tareas"
):

    st.subheader("Resultado Tareas")


    df_resultado_tareas = tabla_tareas(
        st.session_state.tareas,
        st.session_state.usuarios
    )

    styled_df_tareas = aplicar_estilos_tareas(df_resultado_tareas)

    st.dataframe(
        styled_df_tareas,
        width='stretch'
    )

if st.button(
    "Procesar Reporte Adopción",
    disabled=not archivos_adopcion_cargados(),
    key="btn_procesar_adopcion"
):

    df_modulo = st.session_state.modulo.copy()

    rango = st.session_state.get("rango_adopcion")
    if rango and len(rango) == 2:
        f_ini, f_fin = rango

    df_resultado_adopcion = adopcion_tabla(
        st.session_state.usuarios,
        df_modulo,
        f_ini,
        f_fin
    )

    st.subheader("Resultado Adopción")
    styled_df_ado = aplicar_estilos_ado(df_resultado_adopcion)

    st.dataframe(
        styled_df_ado,
        width='stretch'
    )