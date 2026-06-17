import streamlit as st
import warnings
from Scripts.carga import Cargador
from Scripts.indicador_gps import IndicadorGPS
from Scripts.indicador_adopcion import IndicadorAdopcion
from Scripts.indicador_tareas import IndicadorTareas

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.set_page_config(page_title="Automatización de Reportería", layout="wide")


class ReportePage:

    def _gps_listo(self):
        return all(k in st.session_state for k in ["usuarios", "df_checkin", "df_visitas"])

    def _tareas_listo(self):
        return all(k in st.session_state for k in ["usuarios", "tareas"])

    def _adopcion_listo(self):
        return all(k in st.session_state for k in ["usuarios", "modulo"])

    def _seccion_usuarios(self):
        Cargador.cargar_archivo(
            "Sube archivo de usuarios",
            "usuarios_file",
            "usuarios",
            Cargador.leer_archivo
        )
        if "usuarios" in st.session_state:
            Cargador.mostrar_preview(st.session_state.usuarios, "Usuarios")

    def _seccion_archivos_bees(self):
        archivos_bees = st.file_uploader(
            "Sube archivos GPS-visitas-venta",
            type=["csv", "xlsx"],
            accept_multiple_files=True,
            key="bees_files"
        )
        if archivos_bees:
            try:
                df_checkin, df_ventas, df_visitas = Cargador.leer_archivos_clasificados(archivos_bees)
                st.session_state.df_checkin = df_checkin
                st.session_state.df_ventas = df_ventas
                st.session_state.df_visitas = df_visitas
                st.success("Archivos identificados correctamente")
            except Exception as e:
                st.error(f"Error clasificando archivos: {e}")

    def _seccion_tareas(self):
        Cargador.cargar_archivo(
            "Sube archivo de Tareas",
            "tareas_file",
            "tareas",
            Cargador.leer_archivo_tareas
        )

    def _seccion_modulo_ventas(self):
        Cargador.cargar_archivo(
            "Sube Módulo de Ventas",
            "modulo_file",
            "modulo",
            Cargador.leer_archivo
        )
        if "modulo" in st.session_state:
            fecha_min = st.session_state.modulo["fecha"].min()
            fecha_max = st.session_state.modulo["fecha"].max()
            st.date_input(
                "Rango de fechas",
                value=(fecha_min, fecha_max),
                min_value=fecha_min,
                max_value=fecha_max,
                key="rango_adopcion"
            )

    def _procesar_gps(self):
        try:
            df_resultado = IndicadorGPS.unir_tablas(
                st.session_state.usuarios,
                st.session_state.df_checkin,
                st.session_state.df_visitas
            )
            st.subheader("Resultado GPS")
            st.dataframe(IndicadorGPS.aplicar_estilos(df_resultado), width='stretch')
        except Exception as e:
            st.error(f"Error procesando reporte GPS: {e}")

    def _procesar_tareas(self):
        try:
            df_resultado = IndicadorTareas.calcular(
                st.session_state.tareas,
                st.session_state.usuarios
            )
            st.subheader("Resultado Tareas")
            st.dataframe(IndicadorTareas.aplicar_estilos(df_resultado), width='stretch')
        except Exception as e:
            st.error(f"Error procesando reporte de tareas: {e}")

    def _procesar_adopcion(self):
        try:
            df_modulo = st.session_state.modulo.copy()
            rango = st.session_state.get("rango_adopcion")
            f_ini, f_fin = rango if rango and len(rango) == 2 else (None, None)

            df_resultado = IndicadorAdopcion.calcular(
                st.session_state.usuarios,
                df_modulo,
                f_ini,
                f_fin
            )
            st.subheader("Resultado Adopción")
            st.dataframe(IndicadorAdopcion.aplicar_estilos(df_resultado), width='stretch')
        except Exception as e:
            st.error(f"Error procesando reporte de adopción: {e}")

    def render(self):
        st.title("Reporte Indicador GPS Efectivo")
        st.header("Cargar archivos BEES ONE")

        self._seccion_usuarios()

        c1, c2, c3 = st.columns(3)
        with c1:
            self._seccion_archivos_bees()
        with c2:
            self._seccion_tareas()
        with c3:
            self._seccion_modulo_ventas()

        st.divider()

        if st.button("Procesar Reporte Diario", disabled=not self._gps_listo(), key="btn_gps"):
            self._procesar_gps()

        if st.button("Procesar Reporte Tareas", disabled=not self._tareas_listo(), key="btn_tareas"):
            self._procesar_tareas()

        if st.button("Procesar Reporte Adopción", disabled=not self._adopcion_listo(), key="btn_adopcion"):
            self._procesar_adopcion()


ReportePage().render()
