# -*- coding: utf-8 -*-
"""Componentes reutilizáveis de autenticação com UX aprimorado"""
import streamlit as st
import re
from typing import Optional


def render_logout_button(page_key: str) -> None:
    """Renderiza botão de logout consistente em todas as páginas
    
    Args:
        page_key: Identificador único da página para evitar conflito de keys
    """
    if "auth_user" in st.session_state and st.session_state.auth_user:
        # Header com informações do usuário
        col1, col2, col3 = st.columns([9, 2, 1])
        
        with col2:
            # Mostrar email ao invés de username
            user_email = st.session_state.get("auth_user_email", st.session_state.auth_user)
            st.markdown(f"""
                <div style='text-align: right; padding: 10px 0;'>
                    <small style='color: #666;'>👤 {user_email}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🚪 Sair", key=f"{page_key}_logout", use_container_width=True, type="secondary"):
                # Limpar toda sessão de autenticação
                for key in list(st.session_state.keys()):
                    if key.startswith("auth_"):
                        del st.session_state[key]
                st.success("👋 Logout realizado com sucesso!")
                st.switch_page("streamlit_app.py")


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """Valida formato de email
    
    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, "Email é obrigatório"
    
    # Regex mais rigoroso para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    if len(email) > 254:
        return False, "Email muito longo"
    
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Valida força da senha
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 6:
        return False, "Senha deve ter no mínimo 6 caracteres"
    
    if len(password) > 128:
        return False, "Senha muito longa (máximo 128 caracteres)"
    
    # Verificar complexidade mínima
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        return False, "Senha deve conter letras e números"
    
    return True, None


def get_password_strength(password: str) -> tuple[str, str]:
    """Calcula força da senha
    
    Returns:
        (strength_label, color)
    """
    score = 0
    
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    
    if score <= 2:
        return "Fraca", "#ff4444"
    elif score <= 4:
        return "Média", "#ffaa00"
    else:
        return "Forte", "#00aa00"


def show_password_strength(password: str) -> None:
    """Exibe indicador visual de força da senha"""
    if password:
        strength, color = get_password_strength(password)
        st.markdown(f"""
            <div style='margin: 5px 0;'>
                <small>Força da senha: <span style='color: {color}; font-weight: bold;'>{strength}</span></small>
            </div>
        """, unsafe_allow_html=True)


def sanitize_input(text: str) -> str:
    """Sanitiza entrada do usuário"""
    if not text:
        return ""
    # Remove espaços em branco nas extremidades
    text = text.strip()
    # Remove caracteres de controle
    text = "".join(char for char in text if ord(char) >= 32 or char == '\n')
    return text


def show_auth_success_message(email: str) -> None:
    """Mostra mensagem de sucesso de login com animação"""
    st.success(f"✅ Bem-vindo(a), **{email}**!")
    st.balloons()


def show_register_success_message() -> None:
    """Mostra mensagem de sucesso de cadastro"""
    st.success("✅ Cadastro realizado com sucesso!")
    st.info("💡 Use seu email e senha para fazer login na aba ao lado.")
