import streamlit as st
from Scripts.salidas import df_a_excel

st.header("Exportar")

if "df_procesado" not in st.session_state:
    st.warning("No hay datos procesados")
    st.stop()

try:
    excel = df_a_excel(st.session_state["df_procesado"])

    st.download_button(
        "Descargar Excel",
        excel,
        file_name="resultado.xlsx"
    )

except ValueError as e:
    st.error(str(e))