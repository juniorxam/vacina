"""
config.py - NASST Digital v1.1
Configurações da aplicação com variáveis de ambiente
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    app_title: str = "NASST Digital - Controle de Vacinação"
    page_icon: str = "💉"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

    # Ano exibido 
    ano_atual: int = 2026

    # DB - usar caminho que funciona no Streamlit Cloud
    db_path_v7: str = os.getenv("DB_PATH", "nasst_sistema_v7.db")
    db_path_v6: str = os.getenv("DB_PATH_V6", "nasst_sistema_v6.db")

    # Logo
    logo_path: str = os.getenv("LOGO_PATH", "LOGO.png")

    # Segurança: senha do admin (com fallback para desenvolvimento)
    admin_login: str = os.getenv("ADMIN_LOGIN", "admin")
    # No Streamlit Cloud, definir via secrets
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Ambiente
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Detectar se está no Streamlit Cloud
    is_streamlit_cloud: bool = os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'


CONFIG = AppConfig()

# Avisos de configuração
if CONFIG.environment == "production" and not CONFIG.admin_password:
    print("⚠️ AVISO: ADMIN_PASSWORD não configurada! Usando senha padrão.")

if CONFIG.is_streamlit_cloud:
    print("🟢 Rodando no Streamlit Cloud - otimizando configurações...")
