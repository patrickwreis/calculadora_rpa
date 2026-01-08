# -*- coding: utf-8 -*-
"""Administração de usuários - reset manual de senha e ativação."""
import secrets
import streamlit as st

from src.security import SessionManager
from src.ui.auth import require_auth, hash_password
from src.database.db_manager import get_database_manager

st.set_page_config(
    page_title="Administração de Usuários",
    page_icon="🛠️",
    layout="wide",
)

# Restaura sessão (URL token) ou redireciona
SessionManager.ensure_auth(redirect_page="streamlit_app.py")
# Garante login (renderiza formulário se necessário)
if not require_auth(form_key="admin_users_login"):
    st.stop()

# Apenas admins podem entrar
if not st.session_state.get("auth_is_admin", False):
    st.warning("⚠️ Apenas administradores podem acessar esta página.")
    st.stop()

st.title("🛠️ Administração de Usuários")
st.caption("Reset manual de senha e ativação/desativação. Compartilhe a senha temporária com o usuário de forma segura.")

# Controles
col_filters = st.columns([2, 1, 1])
with col_filters[0]:
    search = st.text_input("Buscar (usuário ou email)", placeholder="ex: joao ou joao@empresa.com")
with col_filters[1]:
    include_inactive = st.checkbox("Incluir inativos", value=True)
with col_filters[2]:
    st.write("")

# Dados
db = get_database_manager()
# Fallback para instâncias antigas em cache (após hot-reload)
if not hasattr(db, "list_users"):
    from src.database.db_manager import DatabaseManager
    db = DatabaseManager()
users = db.list_users(include_inactive=include_inactive)

# Filtro simples
if search:
    term = search.lower().strip()
    users = [u for u in users if term in (u.username or "").lower() or term in (u.email or "").lower()]

if not users:
    st.info("Nenhum usuário encontrado com os filtros atuais.")
    st.stop()

st.markdown("#### Usuários")

for user in users:
    with st.container(border=True):
        col_info, col_status, col_actions = st.columns([3, 1.2, 1.8])

        with col_info:
            st.markdown(f"**{user.username}**")
            st.caption(user.email or "(sem email)")
            st.caption(f"Admin: {'✅' if user.is_admin else '❌'}")

        with col_status:
            status_label = "✅ Ativo" if user.is_active else "⛔ Inativo"
            st.metric("Status", status_label)

        with col_actions:
            # Ativar / desativar
            if user.is_active:
                if st.button("Desativar", key=f"deact_{user.id}", use_container_width=True):
                    if db.set_user_active(user.id, False):
                        st.success("Usuário desativado.")
                        st.rerun()
                    else:
                        st.error("Não foi possível desativar.")
            else:
                if st.button("Ativar", key=f"act_{user.id}", use_container_width=True):
                    if db.set_user_active(user.id, True):
                        st.success("Usuário ativado.")
                        st.rerun()
                    else:
                        st.error("Não foi possível ativar.")

            # Reset de senha manual
            if st.button("Resetar senha (temp)", key=f"reset_{user.id}", use_container_width=True):
                temp_password = secrets.token_urlsafe(8)
                hashed = hash_password(temp_password)
                ok = db.update_user_password(user.username, hashed)
                if ok:
                    st.success("Senha temporária gerada. Compartilhe de forma segura.")
                    st.info(f"Senha: **{temp_password}**")
                else:
                    st.error("Falha ao resetar senha.")

st.markdown("---")
st.markdown("ℹ️ Dica: compartilhe a senha temporária por um canal seguro e peça para o usuário alterá-la após o primeiro login.")
