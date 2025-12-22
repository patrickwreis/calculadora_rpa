"""Page-level service for common operations"""
from typing import Dict, Optional, Tuple
import streamlit as st
from src.database import get_database_manager


class PageService:
    """Centralized page utilities and context management"""

    @staticmethod
    def get_user_context() -> Dict[str, any]:
        """Get current user context (auth state and filters)
        
        Returns:
            Dict with user_id, is_admin, and user_filter for queries
        """
        current_user_id = st.session_state.get("auth_user_id", 1)
        is_admin = st.session_state.get("auth_is_admin", False)
        
        # Regular users see only their data; admins see all by default
        user_filter = None if is_admin else current_user_id
        
        return {
            "current_user_id": current_user_id,
            "is_admin": is_admin,
            "user_filter": user_filter,
        }

    @staticmethod
    def require_auth() -> bool:
        """Check if user is authenticated, redirect to home if not
        
        Returns:
            True if authenticated, False otherwise
        """
        if "auth_user_id" not in st.session_state:
            st.error("🔒 Autenticação necessária")
            st.info("Por favor, faça login na página inicial")
            st.stop()
            return False
        return True

    @staticmethod
    def load_calculations(user_filter: Optional[int] = None, use_cache: bool = True) -> Tuple[bool, list, Optional[str]]:
        """Load calculations with spinner
        
        Args:
            user_filter: User ID to filter by (None = all, only for admins)
            use_cache: Whether to use cached data
            
        Returns:
            Tuple of (success, calculations, error_message)
        """
        with st.spinner("⏳ Carregando processos..."):
            db = get_database_manager()
            return db.get_all_calculations(user_id=user_filter, use_cache=use_cache)

    @staticmethod
    def check_admin() -> bool:
        """Check if current user is admin
        
        Returns:
            True if admin, False otherwise
        """
        return st.session_state.get("auth_is_admin", False)

    @staticmethod
    def get_admin_checkbox(label: str = "🌐 Ver todos os processos") -> bool:
        """Get admin toggle checkbox for viewing all data
        
        Args:
            label: Checkbox label
            
        Returns:
            True if checked, False otherwise
        """
        if PageService.check_admin():
            return st.checkbox(label, value=True)
        return False
