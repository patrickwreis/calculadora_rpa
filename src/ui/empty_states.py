# -*- coding: utf-8 -*-
"""UI Components for empty states and enhanced user experience"""
from typing import Optional
import streamlit as st


class EmptyStateManager:
    """Manager for handling empty states across the application"""
    
    @staticmethod
    def show_no_processes_empty_state():
        """Display empty state when no processes exist"""
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 80px; margin-bottom: 20px;">📋</div>
            <h3 style="color: #1f77b4;">Nenhum Processo Cadastrado</h3>
            <p style="color: #666; margin-bottom: 30px; font-size: 16px;">
                Comece calculando o ROI do seu primeiro processo de RPA!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Criar Primeiro Processo", use_container_width=True, key="empty_new_process"):
                st.switch_page("pages/2_Novo_processo.py")
    
    @staticmethod
    def show_no_results_empty_state(search_term: Optional[str] = None):
        """Display empty state when search returns no results"""
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 60px; margin-bottom: 20px;">🔍</div>
            <h3 style="color: #1f77b4;">Nenhum Resultado Encontrado</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if search_term:
            st.info(f"Nenhum processo encontrado para: '{search_term}'")
        else:
            st.info("Nenhum processo corresponde aos critérios de busca.")
    
    @staticmethod
    def show_no_reports_empty_state():
        """Display empty state when no reports can be generated"""
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 80px; margin-bottom: 20px;">📊</div>
            <h3 style="color: #1f77b4;">Sem Dados para Relatório</h3>
            <p style="color: #666; margin-bottom: 30px; font-size: 16px;">
                Cadastre pelo menos um processo para visualizar relatórios.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Criar Processo Agora", use_container_width=True, key="empty_new_from_reports"):
                st.switch_page("pages/2_Novo_processo.py")
    
    @staticmethod
    def show_deletion_confirmation(item_name: str, on_confirm=None, on_cancel=None):
        """Display deletion confirmation dialog"""
        st.warning(f"⚠️ Deseja realmente deletar '{item_name}'?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Sim, Deletar", key="confirm_delete", use_container_width=True):
                if on_confirm:
                    on_confirm()
                return True
        
        with col2:
            if st.button("❌ Cancelar", key="cancel_delete", use_container_width=True):
                if on_cancel:
                    on_cancel()
                return False
        
        return None
    
    @staticmethod
    def show_success_message(message: str, icon: str = "✅"):
        """Display success message with icon"""
        st.success(f"{icon} {message}")
    
    @staticmethod
    def show_error_message(message: str, icon: str = "❌"):
        """Display error message with icon"""
        st.error(f"{icon} {message}")
    
    @staticmethod
    def show_info_message(message: str, icon: str = "ℹ️"):
        """Display info message with icon"""
        st.info(f"{icon} {message}")
    
    @staticmethod
    def show_loading_with_spinner(message: str):
        """Context manager for showing loading spinner"""
        return st.spinner(f"⏳ {message}")
    
    @staticmethod
    def show_metric_card(title: str, value: str, subtitle: Optional[str] = None):
        """Display a metric card with title and value"""
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        
        with col2:
            st.metric(title, value)
            if subtitle:
                st.caption(subtitle)
    
    @staticmethod
    def show_validation_error(field_name: str, error_message: str):
        """Display validation error for a specific field"""
        st.error(f"**{field_name}:** {error_message}")
    
    @staticmethod
    def show_validation_errors(errors: list):
        """Display multiple validation errors"""
        if errors:
            with st.container(border=True):
                st.subheader("⚠️ Erros de Validação")
                for error in errors:
                    st.markdown(f"• {error}")
    
    @staticmethod
    def show_feature_preview(feature_name: str, coming_soon: bool = False):
        """Display feature preview or coming soon banner"""
        if coming_soon:
            st.info(f"🚀 **{feature_name}** está chegando em breve!")
        else:
            st.info(f"✨ Bem-vindo a **{feature_name}**!")
    
    @staticmethod
    def create_responsive_layout(num_columns: int = 3):
        """Create responsive columns that adapt to screen size"""
        # Streamlit automatically handles responsive behavior
        # This is a helper to standardize column creation
        return st.columns(num_columns)
    
    @staticmethod
    def show_section_header(title: str, icon: Optional[str] = None):
        """Display a styled section header"""
        if icon:
            st.markdown(f"## {icon} {title}")
        else:
            st.markdown(f"## {title}")
        st.divider()
    
    @staticmethod
    def show_help_text(text: str, title: str = "💡 Dica"):
        """Display help/tip text in a collapsible section"""
        with st.expander(title):
            st.markdown(text)
    
    @staticmethod
    def show_data_not_found(entity_type: str = "Dados"):
        """Generic data not found empty state"""
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 60px; margin-bottom: 20px;">🚫</div>
            <h3 style="color: #1f77b4;">{entity_type} Não Encontrado</h3>
            <p style="color: #666;">Os dados que você está procurando não estão disponíveis.</p>
        </div>
        """, unsafe_allow_html=True)
