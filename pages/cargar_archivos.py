import streamlit as st
import pandas as pd
from Scripts.carga import leer_archivos_clasificados, leer_archivo_tareas, leer_archivo
from Scripts.transformaciones import procesar_df

st.header("Cargar archivos BEES ONE")

archivos_bees = st.file_uploader(
    "Sube archivos gps-visitas-venta",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

if archivos_bees:
    try:
        st.session_state.df_checkin, st.session_state.df_ventas, st.session_state.df_visitas = leer_archivos_clasificados(archivos_bees)
        st.success("Archivos identificados correctamente")

    except Exception as e:
        st.error(str(e))

if "df_visitas" in st.session_state and not st.session_state.df_visitas.empty:
    st.subheader("Check-In")
    st.write(f"Filas: {st.session_state.df_checkin.shape[0]} | Columnas: {st.session_state.df_checkin.shape[1]}")
    st.dataframe(st.session_state.df_checkin.head())
    st.subheader("Visitas")
    st.write(f"Filas: {st.session_state.df_visitas.shape[0]} | Columnas: {st.session_state.df_visitas.shape[1]}")
    st.dataframe(st.session_state.df_visitas.head())

if "df_ventas" in st.session_state and st.session_state.df_ventas is not None:
    if not st.session_state.df_ventas.empty:
        st.subheader("Ventas")
        st.write(f"Filas: {st.session_state.df_ventas.shape[0]} | Columnas: {st.session_state.df_ventas.shape[1]}")
        st.dataframe(st.session_state.df_ventas.head())

archivo_tareas = st.file_uploader(
    "Sube archivos Tareas",
    type=["csv", "xlsx"]
)

if archivo_tareas:
    try:
        st.session_state.tareas = leer_archivo_tareas(archivo_tareas)
        st.success("Archivo subido correctamente")

    except Exception as e:
        st.error(str(e))

if "tareas" in st.session_state and st.session_state.tareas is not None:
    if not st.session_state.tareas.empty:
        st.subheader("Tareas")
        st.write(f"Filas: {st.session_state.tareas.shape[0]} | Columnas: {st.session_state.tareas.shape[1]}")
        st.dataframe(st.session_state.tareas.head())

archivo_modulo_ventas = st.file_uploader(
    "Sube Módulo de Ventas",
    type=["csv", "xlsx"]
)

if archivo_modulo_ventas:
    try:
        st.session_state.modulo = leer_archivo(archivo_modulo_ventas)
        st.success("Archivo subido correctamente")
        
    except Exception as e:
        st.error(str(e))

if "modulo" in st.session_state and st.session_state.modulo is not None:
    if not st.session_state.modulo.empty:
        st.subheader("Modulo de ventas")
        st.write(f"Filas: {st.session_state.modulo.shape[0]} | Columnas: {st.session_state.modulo.shape[1]}")
        st.dataframe(st.session_state.modulo.head())