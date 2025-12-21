# -*- coding: utf-8 -*-
"""Simple auth layer for Streamlit pages.

Regras:
- Por padrão a autenticação é obrigatória.
- Credenciais padrão de desenvolvimento: admin / admin (substitua via env AUTH_USERNAME/AUTH_PASSWORD).
- Pode ser desabilitada apenas se AUTH_REQUIRED=false.
"""
import os
from typing import Optional

import streamlit as st
from passlib.context import CryptContext

from src.database import DatabaseManager


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def auth_required() -> bool:
    """Flag global (env AUTH_REQUIRED=false desativa)."""
    return os.getenv("AUTH_REQUIRED", "true").lower() != "false"


def _ensure_default_admin(db: DatabaseManager) -> None:
    """Create default admin if none exists (admin/admin or env overrides)."""
    from src.models import User
    admin_user = os.getenv("AUTH_USERNAME") or "admin"
    admin_pass = os.getenv("AUTH_PASSWORD") or "admin"
    existing = db.get_user_by_username(admin_user)
    if existing:
        return
    db.create_user(admin_user, hash_password(admin_pass), is_admin=True, is_active=True)


def _authenticate(db: DatabaseManager, username: str, password: str) -> Optional[dict]:
    user = db.get_user_by_username(username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return {"id": user.id, "username": user.username, "is_admin": user.is_admin}


def require_auth(form_key: str = "login_form", db_manager: Optional[DatabaseManager] = None) -> bool:
    """Aplica autenticação obrigatória com usuários no banco.

    Retorna True se autenticado ou se auth estiver desativada.
    """
    if not auth_required():
        return True

    db = db_manager or DatabaseManager()
    _ensure_default_admin(db)

    # Já autenticado
    if st.session_state.get("auth_user"):
        return True

    st.info("🔒 Faça login para acessar.")
    with st.form(form_key):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar", type="primary")

    if submit:
        user_info = _authenticate(db, username, password)
        if user_info:
            st.session_state.auth_user = user_info["username"]
            st.session_state.auth_user_id = user_info["id"]
            st.session_state.auth_is_admin = user_info.get("is_admin", False)
            st.success("✅ Autenticado")
            st.rerun()
        else:
            st.error("❌ Credenciais inválidas")

    return False


def logout():
    """Limpa estado de autenticação."""
    st.session_state.pop("auth_user", None)
    st.session_state.pop("auth_user_id", None)
    st.session_state.pop("auth_is_admin", None)