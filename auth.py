import secrets
import time
import smtplib
from email.mime.text import MIMEText
import streamlit as st

AUTHORIZED_USERS = st.secrets["AUTHORIZED_USERS"].split(",")

TOKENS = {}  # {email: {"token": str, "expira": float}}

def generar_token(email):
    token = secrets.token_urlsafe(6)
    TOKENS[email] = {
        "token": token,
        "expira": time.time() + 300  # 5 min
    }
    return token

def validar_token(email, token_input):
    data = TOKENS.get(email)
    if not data:
        return False
    if time.time() > data["expira"]:
        return False
    return data["token"] == token_input

def enviar_token(email, token):
    msg = MIMEText(f"Tu token de acceso es: {token}\nExpira en 5 minutos.")
    msg["Subject"] = "Token de acceso"
    msg["From"] = st.secrets["EMAIL_USER"]
    msg["To"] = email

    with smtplib.SMTP_SSL(st.secrets["SMTP_SERVER"], st.secrets["SMTP_PORT"]) as server:
        server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg)