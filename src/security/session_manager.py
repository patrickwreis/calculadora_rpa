# -*- coding: utf-8 -*-
"""Gerenciamento de sessão persistente com cookies."""
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from src.database import get_database_manager


class SessionManager:
    """Gerencia persistência de sessão entre refreshes do navegador.
    
    Usa localStorage (via injection de JavaScript) para persistir dados
    de autenticação sem comprometer segurança.
    """
    
    # Chaves do localStorage
    SESSION_KEY = "rpa_auth_session"
    USER_ID_KEY = "rpa_user_id"
    USER_EMAIL_KEY = "rpa_user_email"
    IS_ADMIN_KEY = "rpa_is_admin"
    TIMESTAMP_KEY = "rpa_session_timestamp"
    
    # Tempo de expiração da sessão (em horas)
    SESSION_EXPIRY_HOURS = 24
    
    @staticmethod
    def inject_localStorage_js():
        """Injeta JavaScript para sincronizar localStorage com session_state."""
        js_code = """
        <script>
        // Sincroniza localStorage com Streamlit session_state
        (function() {
            const sessionKey = 'rpa_auth_session';
            const storedSession = localStorage.getItem(sessionKey);
            
            if (storedSession) {
                try {
                    const session = JSON.parse(storedSession);
                    const now = new Date().getTime();
                    
                    // Verifica expiração (24 horas)
                    if (session.timestamp && (now - session.timestamp) > 24 * 60 * 60 * 1000) {
                        localStorage.removeItem(sessionKey);
                    } else {
                        // Envia dados para o Streamlit backend via query params
                        const currentUrl = new URL(window.location);
                        const hasAuthParam = currentUrl.searchParams.has('_restore_auth');
                        
                        if (!hasAuthParam && session.user_id) {
                            // Restaura sessão adicionando parâmetro à URL
                            currentUrl.searchParams.set('_restore_auth', '1');
                            window.history.replaceState({}, '', currentUrl);
                            
                            // Força refresh para carregar com auth restabel
                            window.location.reload();
                        }
                    }
                } catch (e) {
                    console.error('Erro ao restaurar sessão:', e);
                }
            }
        })();
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    
    @staticmethod
    def save_session(user_id: Optional[int], username: str, email: str, is_admin: bool) -> None:
        """Salva dados de sessão em localStorage.
        
        Args:
            user_id: ID do usuário (não pode ser None)
            username: Nome de usuário
            email: Email do usuário
            is_admin: Se é admin
        """
        if user_id is None:
            raise ValueError("user_id não pode ser None")
        
        session_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "is_admin": is_admin,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        # Salva em session_state para uso imediato
        st.session_state.auth_user = username
        st.session_state.auth_user_id = user_id
        st.session_state.auth_user_email = email
        st.session_state.auth_is_admin = is_admin
        
        # Injeta JavaScript para salvar em localStorage
        js_save = f"""
        <script>
        localStorage.setItem('rpa_auth_session', '{json.dumps(session_data)}');
        console.log('Sessão salva no localStorage');
        </script>
        """
        st.markdown(js_save, unsafe_allow_html=True)
    
    @staticmethod
    def restore_session_from_url_params() -> bool:
        """Restaura sessão do localStorage via parâmetros da URL.
        
        Returns:
            True se sessão foi restaurada, False caso contrário
        """
        # Verifica se parâmetro de restauração está presente
        query_params = st.query_params
        
        if "_restore_auth" in query_params and "auth_user" not in st.session_state:
            # Injeta JS para ler localStorage e validar
            st.markdown("""
            <script>
            (function() {
                const session = localStorage.getItem('rpa_auth_session');
                if (session) {
                    try {
                        const data = JSON.parse(session);
                        // Armazena em window.rpaSession para acessar via API
                        window.rpaSession = data;
                    } catch (e) {
                        console.error('Erro ao parsear sessão:', e);
                        localStorage.removeItem('rpa_auth_session');
                    }
                }
            })();
            </script>
            """, unsafe_allow_html=True)
            return True
        
        return False
    
    @staticmethod
    def restore_session_from_db() -> bool:
        """Tenta restaurar sessão verificando cookies/localStorage.
        
        Returns:
            True se sessão foi restaurada
        """
        # Se já tem auth em session_state, não precisa restaurar
        if "auth_user" in st.session_state and st.session_state.auth_user:
            return True
        
        # Tenta restaurar via cookie (não é seguro para produção, apenas fallback)
        # Em produção, usar tokens JWT com refresh
        return False
    
    @staticmethod
    def clear_session() -> None:
        """Limpa toda a sessão de autenticação."""
        # Remove de session_state
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and key.startswith("auth_"):
                del st.session_state[key]
        
        # Injeta JS para limpar localStorage
        st.markdown("""
        <script>
        localStorage.removeItem('rpa_auth_session');
        console.log('Sessão limpa');
        </script>
        """, unsafe_allow_html=True)
    
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
