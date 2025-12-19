# -*- coding: utf-8 -*-
"""
ROI RPA Calculator - Main Application Entry Point
Professional tool for analyzing ROI of RPA implementations
"""
import streamlit as st
from src.ui.styles import apply_custom_styles
from config import APP_NAME, APP_VERSION, APP_DESCRIPTION

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Calculadora de ROI",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_custom_styles()

# Main header
st.title("📈 ROI RPA Analyzer")
st.markdown("Calcule o retorno real de suas automações RPA")

st.divider()

# Welcome section
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 O que é?
    
    Uma ferramenta profissional para análise financeira de projetos de automação RPA.
    Com ela você consegue:
    
    - 📊 Calcular economia mensual e anual
    - ⏱️ Determinar o payback period
    - 📈 Obter ROI detalhado
    - 💾 Armazenar histórico de projetos
    """)

with col2:
    st.markdown("""
    ### 🚀 Por que usar?
    
    Tome decisões baseadas em dados reais:
    
    - ✅ Justifique investimentos com números
    - ✅ Compare diferentes cenários
    - ✅ Gerencie portfólio de projetos
    - ✅ Acompanhe resultados alcançados
    """)

st.divider()

# Features section
st.markdown("### 💎 Funcionalidades Principais")

feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown("""
    #### 🧮 Calculadora Inteligente
    
    Análise profissional com base em:
    - Horas atuais de trabalho
    - Custo de implementação
    - Manutenção mensal
    - Taxa de automação
    """)

with feat_col2:
    st.markdown("""
    #### 📋 Histórico Completo
    
    Gerencie todos os seus cálculos:
    - Visualize todos os projetos
    - Compare resultados
    - Acompanhe a evolução
    - Exporte dados
    """)

with feat_col3:
    st.markdown("""
    #### 🔐 Dados Seguros
    
    Controle total dos dados:
    - Armazenamento local
    - Sem limite de cálculos
    - Fácil de gerenciar
    - Pronto para produção
    """)

st.divider()

# Call to action
st.markdown("""
<div style="text-align: center; padding: 2rem; background: rgba(66, 184, 133, 0.1); border-radius: 8px; border: 1px solid rgba(66, 184, 133, 0.3);">
    <h3>Pronto para começar?</h3>
    <p>Acesse <strong>Novo processo</strong> no menu lateral para criar seu primeiro cálculo de ROI</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Footer
st.markdown(f"""
<div style="text-align: center; color: #a0a8c0; padding: 2rem 0;">
    <p><strong>{APP_NAME}</strong> v{APP_VERSION}</p>
    <p>{APP_DESCRIPTION}</p>
    <p style="font-size: 0.9rem; margin-top: 2rem;">Desenvolvido com ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)
