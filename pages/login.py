"""
login.py - Página de login com IP real
"""

import os
import streamlit as st

from config import CONFIG
from core.security import Security
from core.ip_utils import IPUtils
from ui.components import UIComponents


class LoginPage:
    """Página de login com captura de IP"""
    
    def __init__(self, auth, audit):
        self.auth = auth
        self.audit = audit
    
    def render(self):
        """Renderiza a página de login"""
        st.title(f"🔐 {CONFIG.app_title}")
        
        # Capturar IP do usuário
        client_ip = IPUtils.get_client_ip()
        ip_masked = IPUtils.mask_ip(client_ip)
        
        if os.path.exists(CONFIG.logo_path):
            import base64
            with open(CONFIG.logo_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
                <style>
                .stApp {{
                    background-size: contain;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                }}
                </style>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container():
                st.markdown("""
                <div style="text-align: center; margin-bottom: 30px;">
                    <h3 style="color: #1e3a8a;">NASST Digital</h3>
                    <p style="color: #6b7280;">Sistema de Controle de Vacinação</p>
                </div>
                """, unsafe_allow_html=True)

                # Mostrar IP (opcional, para debug)
                st.caption(f"🌐 Seu IP: {ip_masked}")

                with st.form("login_form"):
                    login = st.text_input("👤 Usuário", placeholder="Digite seu login")
                    senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")

                    col_btn1, col_btn2 = st.columns([3, 1])
                    with col_btn1:
                        submit = st.form_submit_button("🔓 Entrar", type="primary", use_container_width=True)
                    with col_btn2:
                        reset = st.form_submit_button("🔄 Limpar", type="secondary", use_container_width=True)

                    if submit:
                        if not login or not senha:
                            st.error("⚠️ Preencha todos os campos!")
                            # Registrar tentativa com IP
                            self.audit.registrar(
                                login if login else "ANÔNIMO",
                                "AUTH",
                                "Tentativa de login falha",
                                "Campos vazios",
                                ip_address=client_ip
                            )
                        else:
                            with st.spinner("Validando credenciais..."):
                                # Passar o IP real para o auth service
                                usuario = self.auth.login(login, senha, ip=client_ip)
                                
                                if usuario:
                                    # Guarda TANTO o login quanto o nome
                                    st.session_state.logado = True
                                    st.session_state.usuario_login = login
                                    st.session_state.usuario_nome = usuario["nome"]
                                    st.session_state.nivel_acesso = usuario["nivel_acesso"]
                                    st.session_state.pagina_atual = "dashboard"
                                    st.session_state.usuario_ip = client_ip  # Salvar IP na sessão
                                    st.success(f"✅ Bem-vindo(a), {usuario['nome']}!")

                                    self.audit.registrar(
                                        login,
                                        "AUTH",
                                        "Login realizado",
                                        f"Login bem-sucedido: {usuario['nome']}",
                                        ip_address=client_ip
                                    )

                                    st.rerun()
                                else:
                                    st.error("❌ Login ou senha incorretos!")
                                    # Já registrado dentro do auth.login, mas vamos garantir
                                    self.audit.registrar(
                                        login,
                                        "AUTH",
                                        "Tentativa de login falha",
                                        "Credenciais inválidas",
                                        ip_address=client_ip
                                    )

        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; color: #6b7280; font-size: 12px;">
                <p>NASST Digital v1.1 | Sistema de Controle de Vacinação</p>
                <p>© 2026 - Todos os direitos reservados</p>
                <p>🌐 Seu endereço IP: {ip_masked}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
