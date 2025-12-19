# -*- coding: utf-8 -*-
"""Dashboard - Overview and Statistics"""
import streamlit as st
from src.database import DatabaseManager
from src.ui.components import page_header
from src.calculator.utils import format_currency, format_percentage
from config import APP_NAME

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database
db_manager = DatabaseManager()

# Page header
page_header("Dashboard", "Visão geral de todos os seus processos RPA")

# Get calculations
calculations = db_manager.get_all_calculations()

if not calculations:
    st.info("📋 Nenhum processo cadastrado ainda. Comece criando um novo cálculo na aba 'Novo Processo'!")
    st.stop()

st.divider()

# ========== MAIN METRICS ==========
st.markdown("### 📊 Resumo Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Processos", len(calculations))

with col2:
    total_annual_savings = sum(c.annual_savings for c in calculations)
    st.metric("Economia Anual Total", format_currency(total_annual_savings))

with col3:
    avg_roi = sum(c.roi_percentage_first_year for c in calculations) / len(calculations)
    st.metric("ROI Médio 1º Ano", f"{avg_roi:.1f}%")

with col4:
    avg_payback = sum(c.payback_period_months for c in calculations) / len(calculations)
    st.metric("Payback Médio", f"{avg_payback:.1f} meses")

st.divider()

# ========== TOP PERFORMERS ==========
st.markdown("### 🏆 Top Performers")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Maior ROI")
    top_roi = max(calculations, key=lambda x: x.roi_percentage_first_year)
    st.write(f"**{top_roi.process_name}**")
    st.write(f"ROI: {top_roi.roi_percentage_first_year:.1f}%")
    st.write(f"Economia Anual: {format_currency(top_roi.annual_savings)}")

with col2:
    st.subheader("⏱️ Menor Payback")
    top_payback = min(calculations, key=lambda x: x.payback_period_months)
    st.write(f"**{top_payback.process_name}**")
    st.write(f"Payback: {top_payback.payback_period_months:.1f} meses")
    st.write(f"Economia Mensal: {format_currency(top_payback.monthly_savings)}")

st.divider()

# ========== INVESTMENT SUMMARY ==========
st.markdown("### 💰 Resumo de Investimento")

col1, col2, col3 = st.columns(3)

total_implementation = sum(c.rpa_implementation_cost for c in calculations)
total_monthly_cost = sum(c.rpa_monthly_cost for c in calculations)
total_monthly_savings = sum(c.monthly_savings for c in calculations)

with col1:
    st.metric("Investimento Total", format_currency(total_implementation))

with col2:
    st.metric("Custo Mensal Total", format_currency(total_monthly_cost))

with col3:
    net_monthly_benefit = total_monthly_savings - total_monthly_cost
    st.metric("Benefício Líquido Mensal", format_currency(net_monthly_benefit), 
              delta=f"{(net_monthly_benefit/total_monthly_savings*100) if total_monthly_savings > 0 else 0:.0f}%" if net_monthly_benefit > 0 else None)

st.divider()

# ========== PROCESS LIST ==========
st.markdown("### 📋 Lista de Processos")

# Create a simple dataframe for display
data = []
for calc in calculations:
    data.append({
        "Processo": calc.process_name,
        "Departamento": getattr(calc, 'department', 'N/A'),
        "Economia Anual": format_currency(calc.annual_savings),
        "ROI %": f"{calc.roi_percentage_first_year:.1f}%",
        "Payback": f"{calc.payback_period_months:.1f} meses",
        "Status": "✅ Ativo",
    })

# Display with native streamlit table (simpler and cleaner)
st.dataframe(data, width='stretch', hide_index=True)

st.divider()

# ========== DISTRIBUTION INFO ==========
st.markdown("### 📈 Distribuição")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Complexidade")
    complexity_counts = {}
    for calc in calculations:
        complexity = getattr(calc, 'complexity', 'Não definida')
        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
    
    for complexity, count in complexity_counts.items():
        st.write(f"• {complexity}: {count} processo(s)")

with col2:
    st.subheader("Status de Automação")
    automatable = len([c for c in calculations if c.expected_automation_percentage >= 70])
    partial = len([c for c in calculations if 30 <= c.expected_automation_percentage < 70])
    complex_ones = len([c for c in calculations if c.expected_automation_percentage < 30])
    
    st.write(f"• Altamente Automatizável (≥70%): {automatable}")
    st.write(f"• Parcialmente Automatizável (30-70%): {partial}")
    st.write(f"• Complexo (<30%): {complex_ones}")
