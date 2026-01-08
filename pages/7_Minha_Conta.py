# -*- coding: utf-8 -*-
"""Página de conta do usuário: troca de senha."""
import streamlit as st

from src.security import SessionManager
from src.ui.auth import require_auth, verify_password, hash_password
from src.database.db_manager import get_database_manager

st.set_page_config(
    page_title="Minha Conta",
    page_icon="👤",
    layout="centered",
)

# Restaura sessão ou redireciona
SessionManager.ensure_auth(redirect_page="streamlit_app.py")
# Gate de auth (renderiza login se necessário)
if not require_auth(form_key="my_account_login"):
    st.stop()

# Dados do usuário atual
username = st.session_state.get("auth_user")
user_id = st.session_state.get("auth_user_id")
user_email = st.session_state.get("auth_user_email")

st.title("👤 Minha Conta")
st.caption(f"Usuário: {username} | Email: {user_email or '—'}")

st.divider()
st.subheader("Alterar senha")

with st.form("change_password_form"):
    current_password = st.text_input("Senha atual", type="password")
    new_password = st.text_input("Nova senha", type="password", help="Mínimo 4 caracteres")
    confirm_password = st.text_input("Confirmar nova senha", type="password")
    submitted = st.form_submit_button("Salvar nova senha", type="primary", use_container_width=True)

    if submitted:
        if not current_password or not new_password or not confirm_password:
            st.error("❌ Preencha todos os campos.")
        elif len(new_password) < 4:
            st.error("❌ A nova senha deve ter pelo menos 4 caracteres.")
        elif new_password != confirm_password:
            st.error("❌ A confirmação não confere.")
        else:
            db = get_database_manager()
            user = db.get_user_by_username(username)
            if not user:
                st.error("❌ Usuário não encontrado.")
            elif not verify_password(current_password, user.password_hash):
                st.error("❌ Senha atual incorreta.")
            else:
                hashed = hash_password(new_password)
                ok = db.update_user_password(username, hashed)
                if ok:
                    st.success("✅ Senha alterada com sucesso. Faça login novamente com a nova senha.")
                    # Opcional: limpar sessão para forçar novo login
                    SessionManager.clear_session()
                else:
                    st.error("❌ Não foi possível alterar a senha.")

st.markdown("---")
st.caption("Dica: use uma senha forte e única para esta conta.")
