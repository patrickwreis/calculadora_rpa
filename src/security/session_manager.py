# -*- coding: utf-8 -*-
"""Gerenciamento de sessão persistente com tokens no banco de dados."""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from src.database import get_database_manager

logger = logging.getLogger(__name__)


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
        
        # Salva token TANTO em query_params (para F5) QUANTO em session_state (para navegação)
        st.query_params["session_token"] = token
        st.session_state.persistent_session_token = token  # Backup para navegação entre páginas
        
        logger.info(f"Sessão salva para: {username} (token: {token[:20]}...)")
        
        return token
    
    @staticmethod
    def restore_session() -> bool:
        """Restaura sessão verificando token no banco de dados.
        
        Tenta duas fontes:
        1. query_params["session_token"] - para F5 (refresh)
        2. session_state.persistent_session_token - para navegação entre páginas
        
        Returns:
            True se sessão foi restaurada com sucesso
        """
        # Tenta primeiro query_params (F5 refresh)
        token = None
        
        if "session_token" in st.query_params:
            token = st.query_params["session_token"]
            if isinstance(token, list):
                token = token[0]
            logger.debug(f"Token de query_params: {token[:20] if token else 'None'}...")
        
        # Se não achou em query_params, tenta session_state (navegação entre páginas)
        if not token and "persistent_session_token" in st.session_state:
            token = st.session_state.persistent_session_token
            logger.debug(f"Token de session_state: {token[:20] if token else 'None'}...")
            # Restaura token em query_params também
            if token:
                st.query_params["session_token"] = token
        
        if not token:
            logger.debug("Nenhum token encontrado")
            return False
        
        try:
            # Verifica token no banco de dados
            db = get_database_manager()
            user = db.get_user_by_session_token(token)
            
            if not user:
                logger.warning(f"Usuário não encontrado para token: {token[:20]}...")
                return False
            
            if not user.is_active:
                logger.warning(f"Usuário não está ativo: {user.username}")
                return False
            
            logger.debug(f"Usuário encontrado: {user.username}")
            
            # Verifica expiração
            if user.session_token_expiry and datetime.utcnow() > user.session_token_expiry:
                # Token expirou, limpa
                logger.info(f"Token expirado para usuário: {user.username}")
                db.update_session_token(user.id, None, None)
                SessionManager.clear_session()
                return False
            
            # Restaura sessão
            logger.info(f"Restaurando sessão para: {user.username}")
            st.session_state.auth_user = user.username
            st.session_state.auth_user_id = user.id
            st.session_state.auth_user_email = user.email
            st.session_state.auth_is_admin = user.is_admin
            st.session_state.auth_session_token = token
            st.session_state.auth_session_time = datetime.now().isoformat()
            st.session_state.persistent_session_token = token  # Backup para navegação
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar sessão: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def clear_session() -> None:
        """Limpa toda a sessão de autenticação (banco, query_params, session_state)."""
        # Remove token do banco de dados
        if "auth_user_id" in st.session_state:
            try:
                db = get_database_manager()
                user_id = st.session_state.auth_user_id
                if user_id:
                    db.update_session_token(user_id, None, None)
                    logger.info(f"Token removido do banco para user_id: {user_id}")
            except Exception as e:
                logger.error(f"Erro ao remover token do banco: {str(e)}")
        
        # Remove de session_state (inclusive backup)
        keys_to_delete = [key for key in st.session_state.keys() 
                         if isinstance(key, str) and (key.startswith("auth_") or key == "persistent_session_token")]
        for key in keys_to_delete:
            del st.session_state[key]
        
        # Remove de query_params
        if "session_token" in st.query_params:
            del st.query_params["session_token"]
        
        logger.info("Sessão completamente limpa")
    
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
