# -*- coding: utf-8 -*-
"""
ROI RPA Calculator - Main Application Entry Point
Professional tool for analyzing ROI of RPA implementations
"""
import streamlit as st
from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from src.database import get_database_manager
from src.ui.auth import verify_password, hash_password
from src.ui.auth_components import (
    validate_email, validate_password, show_password_strength,
    sanitize_input, show_auth_success_message, show_register_success_message
)
from src.security import SessionManager

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Calculadora de ROI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)

# Injetar JavaScript para persistência de sessão
SessionManager.inject_localStorage_js()

# Hide page navigation if not logged in
if "auth_user" not in st.session_state or st.session_state.auth_user is None:
    st.markdown("""
        <style>
            /* Hide the page navigation section in sidebar */
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

# Header with Login button
col1, col2, col3 = st.columns([7, 2, 1])
with col1:
    st.title("📈 ROI RPA Analyzer")
with col2:
    if "auth_user" not in st.session_state or st.session_state.auth_user is None:
        if st.button("🔐 Entrar", key="header_login_btn", width='stretch', type="primary"):
            st.session_state.show_auth_modal = True
    else:
        # Mostrar email ao invés de username
        user_email = st.session_state.get("auth_user_email", st.session_state.auth_user)
        st.markdown(f"""
            <div style='text-align: right; padding: 10px 0; font-size: 14px;'>
                👤 <strong>{user_email}</strong>
            </div>
        """, unsafe_allow_html=True)
with col3:
    if "auth_user" in st.session_state and st.session_state.auth_user is not None:
        if st.button("🚪", key="header_logout_btn", width='stretch', type="secondary", help="Sair"):
            SessionManager.clear_session()
            st.rerun()

st.markdown("Calcule o retorno real de suas automações RPA")

st.divider()

# Modal de autenticação
if st.session_state.get("show_auth_modal", False):
    @st.dialog("🔐 Autenticação", width="large")
    def auth_dialog():
        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Cadastrar", "🔄 Esqueci a Senha"])
        
        with tab1:
            st.markdown("### Acesso à Conta")
            login_email = st.text_input(
                "Email", 
                key="modal_login_email",
                placeholder="seu.email@exemplo.com",
                help="Digite o email cadastrado"
            )
            login_password = st.text_input(
                "Senha", 
                type="password", 
                key="modal_login_pass",
                help="Digite sua senha"
            )
            
            st.divider()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ Entrar", key="modal_login_btn", width='stretch', type="primary"):
                    # Sanitizar entrada
                    login_email = sanitize_input(login_email)
                    
                    if not login_email or not login_password:
                        st.error("⚠️ Preencha todos os campos")
                    else:
                        # Validar email
                        is_valid, error_msg = validate_email(login_email)
                        if not is_valid:
                            st.error(f"❌ {error_msg}")
                        else:
                            db = get_database_manager()
                            user = db.get_user_by_email(login_email)
                            
                            if user and verify_password(login_password, user.password_hash):
                                # Salvar sessão persistentemente
                                SessionManager.save_session(
                                    user_id=user.id,
                                    username=user.username,
                                    email=user.email,
                                    is_admin=user.is_admin
                                )
                                st.session_state.show_auth_modal = False
                                show_auth_success_message(user.email)
                                st.rerun()
                            else:
                                st.error("❌ Email ou senha incorretos")
            
            with col3:
                if st.button("❌ Cancelar", key="modal_login_cancel", width='stretch'):
                    st.session_state.show_auth_modal = False
                    st.rerun()
        
        with tab2:
            st.markdown("### Criar Nova Conta")
            reg_email = st.text_input(
                "Email", 
                key="modal_reg_email",
                placeholder="seu.email@exemplo.com",
                help="Use um email válido que você tenha acesso"
            )
            reg_password = st.text_input(
                "Senha", 
                type="password", 
                key="modal_reg_pass",
                help="Mínimo 6 caracteres com letras e números"
            )
            
            # Mostrar força da senha
            show_password_strength(reg_password)
            
            reg_password_confirm = st.text_input(
                "Confirmar Senha", 
                type="password", 
                key="modal_reg_pass_confirm"
            )
            
            st.divider()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ Cadastrar", key="modal_reg_btn", width='stretch', type="primary"):
                    # Sanitizar entradas
                    reg_email = sanitize_input(reg_email)
                    
                    # Validar email
                    is_valid_email, email_error = validate_email(reg_email)
                    if not is_valid_email:
                        st.error(f"❌ {email_error}")
                    # Validar senha
                    elif not reg_password or not reg_password_confirm:
                        st.error("⚠️ Preencha todos os campos")
                    else:
                        is_valid_pass, pass_error = validate_password(reg_password)
                        if not is_valid_pass:
                            st.error(f"❌ {pass_error}")
                        elif reg_password != reg_password_confirm:
                            st.error("❌ As senhas não coincidem")
                        else:
                            db = get_database_manager()
                            if db.get_user_by_email(reg_email):
                                st.error("❌ Este email já está cadastrado")
                            else:
                                # Gerar username a partir do email
                                username = reg_email.split("@")[0]
                                counter = 1
                                original_username = username
                                while db.get_user_by_username(username):
                                    username = f"{original_username}{counter}"
                                    counter += 1
                                
                                hashed_password = hash_password(reg_password)
                                if db.create_user(username, hashed_password, reg_email):
                                    show_register_success_message()
                                    # Aguardar 2 segundos e mudar para aba de login
                                    import time
                                    time.sleep(2)
                                    st.session_state.show_auth_modal = False
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao criar conta. Tente novamente.")
            
            with col3:
                if st.button("❌ Cancelar", key="modal_reg_cancel", width='stretch'):
                    st.session_state.show_auth_modal = False
                    st.rerun()
        
        with tab3:
            st.markdown("### Recuperar Senha")
            st.info("💡 Digite seu email para receber instruções de recuperação de senha.")
            
            recovery_email = st.text_input(
                "Email cadastrado", 
                key="modal_recovery_email",
                placeholder="seu.email@exemplo.com"
            )
            
            st.divider()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("📧 Enviar", key="modal_recovery_btn", width='stretch', type="primary"):
                    recovery_email = sanitize_input(recovery_email)
                    is_valid, error_msg = validate_email(recovery_email)
                    
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                    else:
                        db = get_database_manager()
                        user = db.get_user_by_email(recovery_email)
                        
                        if user:
                            # Gerar senha temporária
                            import secrets
                            import string
                            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                            
                            # Atualizar no banco
                            hashed = hash_password(temp_password)
                            db.update_user_password(user.username, hashed)
                            
                            # Tentar enviar email
                            from src.ui.auth import send_password_reset_email
                            if send_password_reset_email(recovery_email, user.username, temp_password):
                                st.success("✅ Email enviado! Verifique sua caixa de entrada.")
                            else:
                                st.warning(f"⚠️ Não foi possível enviar o email.")
                                st.info(f"🔑 Use esta senha temporária: **{temp_password}**")
                                st.caption("Anote esta senha e faça login para alterá-la.")
                        else:
                            # Por segurança, não revelar se o email existe ou não
                            st.info("📧 Se o email estiver cadastrado, você receberá instruções em breve.")
            
            with col3:
                if st.button("❌ Cancelar", key="modal_recovery_cancel", width='stretch'):
                    st.session_state.show_auth_modal = False
                    st.rerun()
    
    auth_dialog()

# Overview section
col1, col2 = st.columns(2)
with col1:
    st.subheader("🎯 O que é?")
    st.write("""
    Uma ferramenta profissional para análise financeira de projetos de automação RPA.
    
    - 📊 Calcular economia mensal e anual
    - ⏱️ Determinar o payback period
    - 📈 Obter ROI detalhado
    - 💾 Armazenar histórico de projetos
    """)

with col2:
    st.subheader("🚀 Como usar?")
    st.write("""
    1. Acesse **Novo Processo** para criar um cálculo
    2. Preencha os dados do processo atual
    3. Informe os custos de implementação
    4. Visualize os resultados de ROI
    5. Salve para referência futura
    """)

st.divider()

st.subheader("📋 Funcionalidades")
st.write("""
- **Calculadora Inteligente**: Análise profissional baseada em horas, custos e taxas
- **Histórico Completo**: Visualize, compare e gerencie seus projetos
- **Dados Seguros**: Armazenamento local sem limite de cálculos
""")

st.divider()

st.info(f"**{APP_NAME}** v{APP_VERSION}")

