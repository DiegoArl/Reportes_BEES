import streamlit as st

@st.cache_data(show_spinner=False)
def cargar_catalogo(df):
    return df.copy()