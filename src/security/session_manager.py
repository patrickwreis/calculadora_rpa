# -*- coding: utf-8 -*-
"""Gerenciamento de sessão persistente com tokens no banco de dados."""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from src.database import get_database_manager

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SessionManager:
    """Gerencia persistência de sessão usando tokens no banco de dados.
    
    Quando usuário faz login, um token é gerado e armazenado no banco.
    Ao fazer refresh (F5), o token é verificado e a sessão é restaurada.
    """
    
    SESSION_EXPIRY_HOURS = 24
    TOKEN_LENGTH = 32  # Tamanho do token aleatório
    
    @staticmethod
    def save_session(user_id: Optional[int], username: str, email: str, is_admin: bool) -> str:
        """Salva dados de sessão gerando um token no banco de dados."""
        if user_id is None:
            raise ValueError("user_id não pode ser None")
        
        token = secrets.token_urlsafe(SessionManager.TOKEN_LENGTH)
        expiry = datetime.utcnow() + timedelta(hours=SessionManager.SESSION_EXPIRY_HOURS)
        
        # Salva token no banco de dados
        db = get_database_manager()
        db.update_session_token(user_id, token, expiry)
        
        # Salva em session_state
        st.session_state.auth_user = username
        st.session_state.auth_user_id = user_id
        st.session_state.auth_user_email = email
        st.session_state.auth_is_admin = is_admin
        st.session_state.auth_session_token = token
        st.session_state.auth_session_time = datetime.now().isoformat()
        st.session_state.persistent_session_token = token

        msg = f"SESSION SAVED: user={username} (id={user_id}), token={token[:20]}..., expiry={expiry}"
        logger.info(msg)
        
        return token
    
    @staticmethod
    def restore_session() -> bool:
        """Restaura sessão do token armazenado no banco de dados."""
        logger.debug("=" * 80)
        logger.debug("RESTORE_SESSION called")
        logger.debug(f"  session_state has persistent_session_token: {'persistent_session_token' in st.session_state}")
        logger.debug(f"  session_state has auth_user: {'auth_user' in st.session_state}")
        qp = dict(st.query_params)
        token = None
        
        if "persistent_session_token" in st.session_state:
            token = st.session_state.persistent_session_token
            if token:
                logger.debug(f"  Found token in session_state: {token[:20]}...")
            else:
                logger.debug("  Token in session_state is empty")
        
        if not token:
            logger.debug("  No token found - returning False")
            logger.debug("=" * 80)
            return False
        
        try:
            db = get_database_manager()
            user = db.get_user_by_session_token(token)
            
            if not user:
                logger.warning(f"  User not found for token: {token[:20]}...")
                logger.debug("=" * 80)
                return False
            
            if not user.is_active:
                logger.warning(f"  User not active: {user.username}")
                logger.debug("=" * 80)
                return False
            
            logger.debug(f"  User found: {user.username} (id={user.id})")
            
            if user.session_token_expiry and datetime.utcnow() > user.session_token_expiry:
                logger.warning(f"  Token expired for user: {user.username}")
                db.update_session_token(user.id, None, None)
                SessionManager.clear_session()
                logger.debug("=" * 80)
                return False
            
            logger.info(f"RESTORING SESSION for user: {user.username} (id={user.id})")
            st.session_state.auth_user = user.username
            st.session_state.auth_user_id = user.id
            st.session_state.auth_user_email = user.email
            st.session_state.auth_is_admin = user.is_admin
            st.session_state.auth_session_token = token
            st.session_state.auth_session_time = datetime.now().isoformat()
            st.session_state.persistent_session_token = token
            
            logger.info(f"SESSION RESTORED successfully for: {user.username}")
            logger.debug("=" * 80)
            logger.debug("=" * 80)
            return True
            
        except Exception as e:
            logger.error(f"ERROR restoring session: {str(e)}", exc_info=True)
            logger.debug("=" * 80)
            return False
    
    @staticmethod
    def clear_session() -> None:
        """Limpa toda a sessão de autenticação (banco e session_state)."""
        logger.info("CLEARING SESSION")
        
        if "auth_user_id" in st.session_state:
            try:
                db = get_database_manager()
                user_id = st.session_state.auth_user_id
                if user_id:
                    db.update_session_token(user_id, None, None)
                    logger.debug(f"  Token removed from database for user_id: {user_id}")
            except Exception as e:
                logger.error(f"  Error removing token from database: {str(e)}")
        
        keys_to_delete = [key for key in st.session_state.keys() 
                         if isinstance(key, str) and (key.startswith("auth_") or key == "persistent_session_token")]
        for key in keys_to_delete:
            del st.session_state[key]
        logger.debug(f"  Cleared {len(keys_to_delete)} keys from session_state")

        logger.info("SESSION COMPLETELY CLEARED")

        # Não usamos query params para token; nada a limpar aqui

    
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
    
    @staticmethod
    def ensure_auth(redirect_page: str = "streamlit_app.py") -> bool:
        """Garante que a sessão está autenticada, redirecionando se necessário."""
        logger.debug(f"ENSURE_AUTH called from page (will redirect to: {redirect_page})")
        
        if "auth_user" in st.session_state and st.session_state.auth_user:
            logger.debug(f"  Already authenticated as: {st.session_state.auth_user}")
            return True
        
        logger.debug(f"  Not in session_state, attempting restore_session()...")
        
        if SessionManager.restore_session():
            logger.debug(f"  Successfully restored session!")
            return True
        
        logger.warning(f"  Failed to restore session, redirecting to {redirect_page}")
        st.switch_page(redirect_page)
        return False
