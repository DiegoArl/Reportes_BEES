import streamlit as st
from datetime import datetime
from Scripts.salidas import df_a_csv
from Scripts.carga import leer_archivo
from Scripts.delivery import construir_delivery

st.header("Delivery Window")

archivo_delivery = st.file_uploader(
    "Sube el módulo de clientes",
    type=["csv", "xlsx"]
)

if archivo_delivery:
    try:
        st.session_state.delivery = leer_archivo(archivo_delivery)
        st.success("Archivo subido correctamente")

    except Exception as e:
        st.error(str(e))

if "delivery" not in st.session_state:
    st.warning("No se ha cargado el módulo de clientes")
    st.stop()

df = st.session_state["delivery"]
try:
    df_delivery = df_a_csv(construir_delivery(df))
except Exception:
    st.error("Error procesando el archivo. Verifique el formato o cambie de archivo.")
    del st.session_state["delivery"]
    st.stop()

if not df.empty:
    st.subheader("Módulo de Clientes")
    st.write(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    st.dataframe(df.head())

    fecha_actual = datetime.now()
    nombre_archivo = f"import-bees-delivery_{fecha_actual.strftime('%d%m%Y')}.csv"

    st.download_button(
        label="Descargar CSV",
        data=df_delivery.getvalue(),
        file_name=nombre_archivo,
        mime="text/csv"
    )