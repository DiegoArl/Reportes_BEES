import streamlit as st
from datetime import datetime
from Scripts.carga import Cargador
from Scripts.delivery import DeliveryBuilder
from Scripts.salidas import Exportador


class DeliveryPage:

    def _seleccionar_empresa(self):
        st.write("Seleccione la empresa")
        return st.selectbox(
            "Seleccione la empresa",
            ["Nestlé", "D'onofrio"],
            key="empresa_delivery",
            label_visibility="collapsed"
        )

    def _cargar_archivo(self):
        archivo = st.file_uploader("Sube el módulo de clientes", type=["csv", "xlsx"])
        if archivo:
            try:
                st.session_state.delivery = Cargador.leer_archivo(archivo)
                st.success("Archivo subido correctamente")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    def _verificar_datos(self):
        if "delivery" not in st.session_state:
            st.warning("No se ha cargado el módulo de clientes")
            st.stop()

    def _procesar(self, empresa):
        df = st.session_state["delivery"]
        try:
            return DeliveryBuilder.construir(df, empresa)
        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")
            del st.session_state["delivery"]
            st.stop()

    def _mostrar_resultado(self, df_delivery):
        if df_delivery.empty:
            return
        st.subheader("Módulo de Clientes")
        st.write(f"Filas: {df_delivery.shape[0]} | Columnas: {df_delivery.shape[1]}")
        st.dataframe(df_delivery.head(100))

    def _boton_descarga(self, df_delivery):
        nombre_archivo = f"import-bees-delivery_{datetime.now().strftime('%d%m%Y')}.csv"
        try:
            csv_data = Exportador.a_csv(df_delivery).getvalue()
        except Exception as e:
            st.error(f"Error al generar el archivo de descarga: {e}")
            return
        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name=nombre_archivo,
            mime="text/csv"
        )

    def render(self):
        st.header("Delivery Window")
        c1, _, _ = st.columns(3)
        with c1:
            empresa = self._seleccionar_empresa()

        self._cargar_archivo()
        self._verificar_datos()

        df_delivery = self._procesar(empresa)
        self._mostrar_resultado(df_delivery)
        self._boton_descarga(df_delivery)


DeliveryPage().render()
