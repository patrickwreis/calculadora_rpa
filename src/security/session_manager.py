# -*- coding: utf-8 -*-
"""Gerenciamento de sessão persistente com tokens no banco de dados."""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from src.database import get_database_manager


class SessionManager:
    """Gerencia persistência de sessão usando tokens no banco de dados.
    
    Quando usuário faz login, um token é gerado e armazenado no banco.
    Ao fazer refresh (F5), o token é verificado e a sessão é restaurada.
    """
    
    SESSION_EXPIRY_HOURS = 24
    TOKEN_LENGTH = 32  # Tamanho do token aleatório
    
    @staticmethod
    def save_session(user_id: Optional[int], username: str, email: str, is_admin: bool) -> str:
        """Salva dados de sessão gerando um token no banco de dados.
        
        Args:
            user_id: ID do usuário (não pode ser None)
            username: Nome de usuário
            email: Email do usuário
            is_admin: Se é admin
            
        Returns:
            Token de sessão para armazenar em cookie/URL
        """
        if user_id is None:
            raise ValueError("user_id não pode ser None")
        
        # Gera token aleatório
        token = secrets.token_urlsafe(SessionManager.TOKEN_LENGTH)
        expiry = datetime.utcnow() + timedelta(hours=SessionManager.SESSION_EXPIRY_HOURS)
        
        # Salva token no banco de dados
        db = get_database_manager()
        db.update_session_token(user_id, token, expiry)
        
        # Salva em session_state para uso imediato
        st.session_state.auth_user = username
        st.session_state.auth_user_id = user_id
        st.session_state.auth_user_email = email
        st.session_state.auth_is_admin = is_admin
        st.session_state.auth_session_token = token
        st.session_state.auth_session_time = datetime.now().isoformat()
        
        # Salva token em query_params para manter entre refreshes
        st.query_params["session_token"] = token
        
        return token
    
    @staticmethod
    def restore_session() -> bool:
        """Restaura sessão verificando token no banco de dados.
        
        Returns:
            True se sessão foi restaurada com sucesso
        """
        # Se já tem sessão válida em session_state, não restaura
        if "auth_user" in st.session_state and st.session_state.auth_user:
            return True
        
        # Tenta restaurar de query_params
        if "session_token" not in st.query_params:
            return False
        
        try:
            token = st.query_params["session_token"]
            if isinstance(token, list):
                token = token[0]
            
            if not token:
                return False
            
            # Verifica token no banco de dados
            db = get_database_manager()
            user = db.get_user_by_session_token(token)
            
            if not user or not user.is_active:
                return False
            
            # Verifica expiração
            if user.session_token_expiry and datetime.utcnow() > user.session_token_expiry:
                # Token expirou, limpa
                db.update_session_token(user.id, None, None)
                SessionManager.clear_session()
                return False
            
            # Restaura sessão
            st.session_state.auth_user = user.username
            st.session_state.auth_user_id = user.id
            st.session_state.auth_user_email = user.email
            st.session_state.auth_is_admin = user.is_admin
            st.session_state.auth_session_token = token
            st.session_state.auth_session_time = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def clear_session() -> None:
        """Limpa toda a sessão de autenticação."""
        # Remove token do banco de dados
        if "auth_user_id" in st.session_state:
            try:
                db = get_database_manager()
                user_id = st.session_state.auth_user_id
                if user_id:
                    db.update_session_token(user_id, None, None)
            except Exception:
                pass
        
        # Remove de session_state
        keys_to_delete = [key for key in st.session_state.keys() 
                         if isinstance(key, str) and key.startswith("auth_")]
        for key in keys_to_delete:
            del st.session_state[key]
        
        # Remove de query_params
        if "session_token" in st.query_params:
            del st.query_params["session_token"]
    
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
