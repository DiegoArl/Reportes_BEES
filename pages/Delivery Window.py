import streamlit as st
from datetime import datetime
from Scripts.salidas import df_a_csv
from Scripts.carga import leer_archivo
from Scripts.delivery import construir_delivery

st.header("Delivery Window")

c1, c2, c3 = st.columns(3)
with c1:
    st.write("Seleccione la empresa")
    empresa_delivery = st.selectbox(
        "Seleccione la empresa", 
        ["Nestlé", "D'onofrio"], 
        key="empresa_delivery", 
        label_visibility="collapsed"
    )

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
    df_delivery = construir_delivery(df, empresa_delivery)
except Exception:
    st.error("Error procesando el archivo. Verifique el formato o cambie de archivo.")
    del st.session_state["delivery"]
    st.stop()

if not df_delivery.empty:
    st.subheader("Módulo de Clientes")
    st.write(f"Filas: {df_delivery.shape[0]} | Columnas: {df_delivery.shape[1]}")
    st.dataframe(df_delivery.head(100))

    fecha_actual = datetime.now()
    nombre_archivo = f"import-bees-delivery_{fecha_actual.strftime('%d%m%Y')}.csv"

    st.download_button(
        label="Descargar CSV",
        data=df_a_csv(df_delivery).getvalue(),
        file_name=nombre_archivo,
        mime="text/csv"
    )