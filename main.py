import streamlit as st
import datetime as datetime
import config as constant
from auth import generar_token, validar_token, enviar_token

AUTHORIZED_USERS = [
    e.strip().lower()
    for e in st.secrets["AUTHORIZED_USERS"].split(",")
]

def login():
    st.title(constant.COMPANY_NAME)
    c1, c2 = st.columns(2)

    with c1:
        st.image(constant.LOGO_PATH)

    with c2:
        st.header("Inicio de sesión")

        email = st.text_input("Email autorizado").strip().lower()

        if st.button("Enviar token"):
            if email in AUTHORIZED_USERS:
                token = generar_token(email)
                enviar_token(email, token)
                st.success("Token enviado al correo")
            else:
                st.error("Usuario no autorizado")

        token_input = st.text_input("Token", type="password")

        if st.button("Ingresar"):
            if validar_token(email, token_input):
                st.session_state.user = email
                st.session_state.login_time = datetime.datetime.now()
                st.rerun()
            else:
                st.error("Token inválido o expirado")

def logout():
    st.title("Sesión iniciada")
    st.write(f"Email: {st.session_state.user}")
    st.write(f"Fecha y hora de inicio: {st.session_state.login_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if st.button("Log out"):
        del st.session_state.user
        del st.session_state.login_time
        st.rerun()

login_page = st.Page(login, title="Login", icon="🔐")
logout_page = st.Page(logout, title="Logout", icon="🚪")

delivery_page = st.Page("pages/Delivery Window.py", title="Delivery Window", icon="🚚")
gps_page = st.Page("pages/Reporte GPS.py", title="Reporte GPS", icon="🗺️")

if "user" in st.session_state:
    pg = st.navigation(
        {
            "Cuenta": [logout_page],
            "Entregas": [delivery_page],
            "Reportes": [gps_page]
        }
    )
else:
    pg = st.navigation({"Cuenta": [login_page]})

pg.run()