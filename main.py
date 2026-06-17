import streamlit as st

delivery_page = st.Page("pages/Delivery Window.py", title="Delivery Window", icon="🚚")
gps_page = st.Page("pages/Reporte GPS.py", title="Reporte GPS", icon="🗺️")

pg = st.navigation({
    "Entregas": [delivery_page],
    "Reportes": [gps_page]
})
pg.run()
