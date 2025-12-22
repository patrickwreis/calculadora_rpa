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
            if st.button("➕ Criar Primeiro Processo", key="empty_new_process"):
                st.switch_page("pages/2_Novo_processo.py")
    
    @staticmethod
    def show_error_message(message: str, icon: str = "❌"):
        """Display error message with icon"""
        st.error(f"{icon} {message}")
