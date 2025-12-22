# -*- coding: utf-8 -*-
"""Simple auth layer for Streamlit pages.

Regras:
- Por padrão a autenticação é obrigatória.
- Credenciais padrão de desenvolvimento: admin / admin (substitua via env AUTH_USERNAME/AUTH_PASSWORD).
- Pode ser desabilitada apenas se AUTH_REQUIRED=false.
"""
import os
import smtplib
from typing import Optional, Tuple, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
import bcrypt

from src.database import DatabaseManager


def _truncate_for_bcrypt(password: str) -> str:
    # bcrypt only considers the first 72 bytes; truncate to avoid errors
    return password[:72]


def send_password_reset_email(email: str, username: str, temp_password: str) -> bool:
    """Enviar email de recuperação de senha via SMTP.
    
    Configurar variáveis de ambiente:
    - SMTP_SERVER: endereço do servidor SMTP (padrão: smtp.gmail.com)
    - SMTP_PORT: porta do servidor (padrão: 587)
    - EMAIL_SENDER: email para envio (ex: seu_email@gmail.com)
    - EMAIL_PASSWORD: senha ou app password
    """
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("EMAIL_SENDER", "")
        sender_password = os.getenv("EMAIL_PASSWORD", "")
        
        if not sender_email or not sender_password:
            st.warning("⚠️ Email não configurado. Senha temporária exibida na tela.")
            return False
        
        # Criar mensagem
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "🔐 Recuperação de Senha - Sistema RPA"
        
        body = f"""Olá {username},

Você solicitou recuperação de senha. Use a senha temporária abaixo para fazer login:

{'=' * 40}
Senha Temporária: {temp_password}
{'=' * 40}

Após fazer login, altere sua senha para uma mais segura.

Se você não solicitou esta recuperação, ignore este email.

Atenciosamente,
Sistema de Cálculo de ROI em RPA
"""
        
        message.attach(MIMEText(body, "plain", "utf-8"))
        
        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao enviar email: {str(e)}")
        return False


def hash_password(password: str) -> str:
    truncated = _truncate_for_bcrypt(password).encode("utf-8")
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    truncated = _truncate_for_bcrypt(password).encode("utf-8")
    return bcrypt.checkpw(truncated, hashed.encode("utf-8"))


def auth_required() -> bool:
    """Flag global (env AUTH_REQUIRED=false desativa)."""
    return os.getenv("AUTH_REQUIRED", "true").lower() != "false"


def _load_credentials(db: DatabaseManager) -> Tuple[dict, Dict[str, Dict[str, Any]]]:
    """Montar credenciais para streamlit-authenticator a partir dos usuários ativos."""
    users = db.list_active_users()
    credentials = {"usernames": {}}
    lookup: Dict[str, Dict[str, Any]] = {}

    for user in users:
        credentials["usernames"][user.username] = {
            "name": user.username,
            "password": user.password_hash,
        }
        lookup[user.username] = {
            "id": user.id,
            "is_admin": bool(user.is_admin),
        }

    return credentials, lookup


def _ensure_default_admin(db: DatabaseManager) -> None:
    """Create default admin if none exists (admin/admin or env overrides)."""
    from src.models import User
    admin_user = os.getenv("AUTH_USERNAME") or "admin"
    admin_pass = os.getenv("AUTH_PASSWORD") or "admin"
    admin_email = os.getenv("AUTH_EMAIL") or "admin@localhost"
    existing = db.get_user_by_username(admin_user)
    if existing:
        return
    db.create_user(admin_user, hash_password(admin_pass), email=admin_email, is_admin=True, is_active=True)


def require_auth(form_key: str = "login_form", db_manager: Optional[DatabaseManager] = None) -> bool:
    """Aplica autenticação obrigatória com usuários no banco.

    Retorna True se autenticado ou se auth estiver desativada.
    """
    if not auth_required():
        return True

    from src.database.db_manager import get_database_manager
    db = db_manager or get_database_manager()
    _ensure_default_admin(db)

    # Check session state for existing auth
    if "auth_user" in st.session_state and st.session_state.get("auth_user"):
        return True

    # Enhanced UI with styling
    st.markdown("""
    <style>
        .auth-container {
            max-width: 900px;
            margin: 0 auto;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔐 Área de Autenticação")
    st.divider()
    
    # Use tabs for better organization
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Registrar", "🔄 Recuperar Senha"])
    
    with tab1:
        st.markdown("#### Entre com sua conta")
        login_username = st.text_input("👤 Usuário", key=f"{form_key}_login_user", placeholder="seu usuário")
        login_password = st.text_input("🔒 Senha", type="password", key=f"{form_key}_login_pass", placeholder="sua senha")
        
        if st.button("🔓 Fazer Login", width='stretch', key=f"{form_key}_login_btn", type="primary"):
            if not login_username or not login_password:
                st.error("❌ Usuário e senha são obrigatórios")
            else:
                user = db.get_user_by_username(login_username)
                if not user or not user.is_active:
                    st.error("❌ Usuário não encontrado ou inativo")
                elif not verify_password(login_password, user.password_hash):
                    st.error("❌ Credenciais inválidas")
                else:
                    st.session_state.auth_user = login_username
                    st.session_state.auth_user_id = user.id
                    st.session_state.auth_is_admin = user.is_admin
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
    
    with tab2:
        st.markdown("#### Crie uma nova conta")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("👤 Usuário", key=f"{form_key}_new_user", placeholder="min. 3 caracteres")
        with col2:
            new_email = st.text_input("📧 Email", key=f"{form_key}_new_email", placeholder="seu@email.com")
        
        new_password = st.text_input("🔒 Senha", type="password", key=f"{form_key}_new_pass", placeholder="min. 4 caracteres")
        
        if st.button("✨ Criar Conta", width='stretch', key=f"{form_key}_register_btn", type="primary"):
            if not new_username or not new_password or not new_email:
                st.error("❌ Usuário, email e senha são obrigatórios")
            elif len(new_username) < 3:
                st.error("❌ Usuário deve ter pelo menos 3 caracteres")
            elif len(new_password) < 4:
                st.error("❌ Senha deve ter pelo menos 4 caracteres")
            elif "@" not in new_email:
                st.error("❌ Email inválido")
            else:
                existing_user = db.get_user_by_username(new_username)
                if existing_user:
                    st.error("❌ Usuário já existe")
                else:
                    try:
                        db.create_user(new_username, hash_password(new_password), email=new_email, is_admin=False, is_active=True)
                        st.success(f"✅ Conta criada com sucesso!")
                        st.balloons()
                        st.info(f"🎉 Bem-vindo, **{new_username}**! Agora faça login acima.")
                    except Exception as e:
                        st.error(f"❌ Erro ao criar conta: {str(e)}")
    
    with tab3:
        st.markdown("#### Recuperar acesso à sua conta")
        recovery_user = st.text_input("👤 Digite seu usuário", key=f"{form_key}_recovery_user", placeholder="seu usuário aqui")
        recovery_email = st.text_input("📧 Digite seu email", key=f"{form_key}_recovery_email", placeholder="seu@email.com")
        
        if st.button("🔐 Recuperar Senha", width='stretch', key=f"{form_key}_recovery_btn", type="primary"):
            if not recovery_user or not recovery_email:
                st.error("❌ Usuário e email são obrigatórios")
            else:
                user = db.get_user_by_username(recovery_user)
                if not user:
                    st.error("❌ Usuário não encontrado")
                elif user.email != recovery_email:
                    st.error("❌ Email não corresponde ao usuário")
                else:
                    import random
                    import string
                    temp_pass = "".join(random.choices(string.ascii_letters + string.digits, k=8))
                    db.update_user_password(recovery_user, hash_password(temp_pass))
                    
                    # Tentar enviar email
                    email_sent = send_password_reset_email(user.email, recovery_user, temp_pass)
                    
                    if email_sent:
                        st.success("✅ Email enviado com sucesso!")
                        st.info("📧 Verifique seu email para a senha temporária.")
                    else:
                        st.success("✅ Senha temporária gerada!")
                        st.code(temp_pass, language="text")
                        st.info("Email não foi enviado, mas a senha foi alterada. Use a senha acima.")
                    
                    st.warning("⚠️ **Importante:**\n- Faça login com a senha temporária\n- Altere para uma senha segura após entrar")
    
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>💡 Dica:</strong> Admin padrão: <code>admin</code> / <code>admin</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    return False


def logout():
    """Limpa estado de autenticação."""
    st.session_state.pop("auth_user", None)
    st.session_state.pop("auth_user_id", None)
    st.session_state.pop("auth_is_admin", None)