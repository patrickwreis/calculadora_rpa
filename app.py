# -*- coding: utf-8 -*-
"""
ROI RPA Calculator - Main Application Entry Point
Professional tool for analyzing ROI of RPA implementations
"""
import streamlit as st
from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from src.ui.auth import require_auth

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Calculadora de ROI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)

# Main header
if not require_auth(form_key="app_login_form"):
    st.stop()

st.title("📈 ROI RPA Analyzer")
st.markdown("Calcule o retorno real de suas automações RPA")

st.divider()

# Overview section
col1, col2 = st.columns(2)
with col1:
    st.subheader("🎯 O que é?")
    st.write("""
    Uma ferramenta profissional para análise financeira de projetos de automação RPA.
    
    - 📊 Calcular economia mensal e anual
    - ⏱️ Determinar o payback period
    - 📈 Obter ROI detalhado
    - 💾 Armazenar histórico de projetos
    """)

with col2:
    st.subheader("🚀 Como usar?")
    st.write("""
    1. Acesse **Novo Processo** para criar um cálculo
    2. Preencha os dados do processo atual
    3. Informe os custos de implementação
    4. Visualize os resultados de ROI
    5. Salve para referência futura
    """)

st.divider()

st.subheader("📋 Funcionalidades")
st.write("""
- **Calculadora Inteligente**: Análise profissional baseada em horas, custos e taxas
- **Histórico Completo**: Visualize, compare e gerencie seus projetos
- **Dados Seguros**: Armazenamento local sem limite de cálculos
""")

st.divider()

st.info(f"**{APP_NAME}** v{APP_VERSION}\n\n{APP_DESCRIPTION}")
