"""
streamlit_app.py - Entry point otimizado para Streamlit Cloud
"""

import streamlit as st
import os
import sys

# Configurar detecção de ambiente Cloud
os.environ['STREAMLIT_CLOUD'] = 'true'

# Configuração da página DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title="NASST Digital - Controle de Vacinação",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Importar a aplicação principal
from app import main

if __name__ == "__main__":
    main()
