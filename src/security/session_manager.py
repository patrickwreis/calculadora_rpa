# -*- coding: utf-8 -*-
"""Gerenciamento de sessão persistente com session_state."""
from datetime import datetime
from typing import Optional, Dict, Any
import streamlit as st


class SessionManager:
    """Gerencia persistência de sessão entre refreshes do navegador.
    
    Streamlit persiste session_state automaticamente entre refreshes,
    então apenas precisamos gerenciar o ciclo de vida da sessão.
    """
    
    SESSION_EXPIRY_HOURS = 24
    
    @staticmethod
    def save_session(user_id: Optional[int], username: str, email: str, is_admin: bool) -> None:
        """Salva dados de sessão em session_state (Streamlit cuida da persistência).
        
        Args:
            user_id: ID do usuário (não pode ser None)
            username: Nome de usuário
            email: Email do usuário
            is_admin: Se é admin
        """
        if user_id is None:
            raise ValueError("user_id não pode ser None")
        
        # Salva em session_state - Streamlit mantém automaticamente entre refreshes
        st.session_state.auth_user = username
        st.session_state.auth_user_id = user_id
        st.session_state.auth_user_email = email
        st.session_state.auth_is_admin = is_admin
        st.session_state.auth_session_time = datetime.now().isoformat()
    
    @staticmethod
    def restore_session() -> bool:
        """Valida se a sessão atual é válida.
        
        Returns:
            True se sessão existe e é válida
        """
        # Se não tem auth, nada a validar
        if not ("auth_user" in st.session_state and st.session_state.auth_user):
            return False
        
        # Verifica expiração
        if "auth_session_time" in st.session_state:
            try:
                session_time = datetime.fromisoformat(st.session_state.auth_session_time)
                if (datetime.now() - session_time).total_seconds() > 24 * 3600:
                    # Sessão expirou
                    SessionManager.clear_session()
                    return False
            except Exception:
                return False
        
        # Sessão válida
        return True
    
    @staticmethod
    def clear_session() -> None:
        """Limpa toda a sessão de autenticação."""
        keys_to_delete = [key for key in st.session_state.keys() 
                         if isinstance(key, str) and key.startswith("auth_")]
        for key in keys_to_delete:
            del st.session_state[key]
    
    @staticmethod
    def get_session_data() -> Optional[Dict[str, Any]]:
        """Retorna dados da sessão atual.
        
        Returns:
            Dict com dados da sessão ou None
        """
        if "auth_user" in st.session_state and st.session_state.auth_user:
            return {
                "user": st.session_state.auth_user,
                "user_id": st.session_state.get("auth_user_id"),
                "email": st.session_state.get("auth_user_email"),
                "is_admin": st.session_state.get("auth_is_admin", False)
            }
        return None
