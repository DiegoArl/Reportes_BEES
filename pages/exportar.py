import streamlit as st
from Scripts.salidas import df_a_excel

st.header("Exportar")

if "df_procesado" not in st.session_state:
    st.warning("No hay datos procesados")
    st.stop()

df = st.session_state["df_procesado"]

st.subheader("Preview")
st.write(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
st.dataframe(df.head(50))

if st.button("Generar Excel"):
    excel = df_a_excel(df)
    st.session_state.df_procesado
    st.download_button(
        "Descargar Excel",
        excel,
        file_name="resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
