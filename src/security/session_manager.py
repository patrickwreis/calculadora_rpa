# -*- coding: utf-8 -*-
"""Gerenciamento de sessão persistente com cookies HTTP."""
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from src.database import get_database_manager


class SessionManager:
    """Gerencia persistência de sessão entre refreshes do navegador.
    
    Usa cookies HTTP para persistir dados de autenticação de forma segura.
    """
    
    SESSION_EXPIRY_HOURS = 24
    
    @staticmethod
    def save_session(user_id: Optional[int], username: str, email: str, is_admin: bool) -> None:
        """Salva dados de sessão em session_state.
        
        Args:
            user_id: ID do usuário (não pode ser None)
            username: Nome de usuário
            email: Email do usuário
            is_admin: Se é admin
        """
        if user_id is None:
            raise ValueError("user_id não pode ser None")
        
        # Salva em session_state para uso na sessão atual
        st.session_state.auth_user = username
        st.session_state.auth_user_id = user_id
        st.session_state.auth_user_email = email
        st.session_state.auth_is_admin = is_admin
        st.session_state.auth_session_time = datetime.now().isoformat()
        
        # Serializa para passar via query_params (para persistência cross-refresh)
        session_data = base64.b64encode(
            json.dumps({
                "user_id": user_id,
                "username": username,
                "email": email,
                "is_admin": is_admin,
                "timestamp": datetime.now().isoformat()
            }).encode()
        ).decode()
        
        # Salva em query_params (Streamlit mantém entre refreshes)
        st.query_params["_auth"] = session_data
    
    @staticmethod
    def restore_session() -> bool:
        """Restaura sessão de query_params (mantida pelo Streamlit).
        
        Returns:
            True se sessão foi restaurada, False caso contrário
        """
        # Se já tem auth, não restaura
        if "auth_user" in st.session_state and st.session_state.auth_user:
            return True
        
        # Tenta restaurar de query_params
        if "_auth" in st.query_params:
            try:
                auth_data = st.query_params["_auth"]
                if isinstance(auth_data, list):
                    auth_data = auth_data[0]
                
                decoded = json.loads(
                    base64.b64decode(auth_data.encode()).decode()
                )
                
                # Verifica expiração (24 horas)
                session_time = datetime.fromisoformat(decoded["timestamp"])
                if (datetime.now() - session_time).total_seconds() > 24 * 3600:
                    # Expirou, limpa
                    SessionManager.clear_session()
                    return False
                
                # Restaura na sessão
                st.session_state.auth_user = decoded["username"]
                st.session_state.auth_user_id = decoded["user_id"]
                st.session_state.auth_user_email = decoded["email"]
                st.session_state.auth_is_admin = decoded["is_admin"]
                st.session_state.auth_session_time = decoded["timestamp"]
                
                return True
            except Exception as e:
                st.error(f"Erro ao restaurar sessão: {str(e)}")
                SessionManager.clear_session()
                return False
        
        return False
    
    @staticmethod
    def clear_session() -> None:
        """Limpa toda a sessão de autenticação."""
        # Remove de session_state
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and key.startswith("auth_"):
                del st.session_state[key]
        
        # Remove de query_params
        if "_auth" in st.query_params:
            del st.query_params["_auth"]
    
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
