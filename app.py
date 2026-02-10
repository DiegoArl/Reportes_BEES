import streamlit as st

st.set_page_config(
    page_title= "Automatización de Reportería",
    layout="wide"
)

st.title("Reporte Indicador GPS Efectivo - Adopción - Alcance Tareas")

if "df_procesado" in st.session_state:
    st.success("Archivo Cargado y Procesado")
else:
    st.info("Aún no se han cargado los archivos")