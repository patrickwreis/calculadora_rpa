# -*- coding: utf-8 -*-
"""Rankings Page - Top processes by ROI, Payback, and Savings"""
import streamlit as st
import pandas as pd
from src.database import DatabaseManager
from src.ui.components import page_header
from src.calculator.utils import format_currency, format_percentage, format_months
from src.analysis.ranking import (
    rank_by_roi,
    rank_by_payback,
    rank_by_annual_savings,
)
from config import APP_NAME

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Rankings",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database
db_manager = DatabaseManager()

# Page header
page_header("Rankings de Processos", "Veja quais processos têm melhor desempenho em ROI, Payback e Economia")

# Get calculations
calculations = db_manager.get_all_calculations()

if not calculations:
    st.info("📋 Nenhum cálculo salvo ainda. Comece criando um novo cálculo!")
    st.stop()

# Main rankings section
st.subheader("🏆 Top 5 Processos")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("### 📈 Melhor ROI (%)")
    st.divider()
    roi_rankings = rank_by_roi(calculations, top=5)
    for i, c in enumerate(roi_rankings, start=1):
        st.write(f"**{i}.** {c.process_name}")
        st.write(f"   ROI: {format_percentage(c.roi_percentage_first_year)}")
        st.write("")

with col2:
    st.markdown("### ⏱️ Melhor Payback")
    st.divider()
    payback_rankings = rank_by_payback(calculations, top=5)
    for i, c in enumerate(payback_rankings, start=1):
        st.write(f"**{i}.** {c.process_name}")
        st.write(f"   Payback: {format_months(c.payback_period_months)}")
        st.write("")

with col3:
    st.markdown("### 💰 Maior Economia Anual")
    st.divider()
    savings_rankings = rank_by_annual_savings(calculations, top=5)
    for i, c in enumerate(savings_rankings, start=1):
        st.write(f"**{i}.** {c.process_name}")
        st.write(f"   Economia: {format_currency(c.annual_savings)}")
        st.write("")

st.divider()

# Detailed rankings table
st.subheader("📊 Tabela Comparativa Completa")

# Create comprehensive ranking dataframe
data = []
for calc in calculations:
    data.append(
        {
            "Processo": calc.process_name,
            "Economia Mensal": format_currency(calc.monthly_savings),
            "Economia Anual": format_currency(calc.annual_savings),
            "Payback": format_months(calc.payback_period_months),
            "ROI %": format_percentage(calc.roi_percentage_first_year),
            "Data": calc.created_at.strftime("%d/%m/%Y"),
        }
    )

df = pd.DataFrame(data)

# Display tabs for different sorting
tab1, tab2, tab3 = st.tabs(["🎯 Por ROI", "⏱️ Por Payback", "💸 Por Economia Anual"])

with tab1:
    # Sort by ROI (need to convert format_percentage back to float for sorting)
    # Create a sortable version
    sortable_data = []
    for calc in calculations:
        sortable_data.append({
            "Processo": calc.process_name,
            "Departamento": getattr(calc, 'department', 'N/A'),
            "Economia Mensal": f"R$ {calc.monthly_savings:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "Economia Anual": f"R$ {calc.annual_savings:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "Payback": f"{calc.payback_period_months:.1f}m",
            "ROI %": f"{calc.roi_percentage_first_year:.1f}%",
            "ROI_Sort": calc.roi_percentage_first_year,
        })
    
    df_roi = pd.DataFrame(sortable_data)
    df_roi = df_roi.sort_values("ROI_Sort", ascending=False)
    df_roi = df_roi.drop("ROI_Sort", axis=1)
    st.dataframe(df_roi, width='stretch', hide_index=True)

with tab2:
    # Sort by Payback
    sortable_data = []
    for calc in calculations:
        sortable_data.append({
            "Processo": calc.process_name,
            "Departamento": getattr(calc, 'department', 'N/A'),
            "Economia Mensal": f"R$ {calc.monthly_savings:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "Economia Anual": f"R$ {calc.annual_savings:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "Payback": f"{calc.payback_period_months:.1f}m",
            "ROI %": f"{calc.roi_percentage_first_year:.1f}%",
            "Payback_Sort": calc.payback_period_months,
        })
    
    df_payback = pd.DataFrame(sortable_data)
    df_payback = df_payback.sort_values("Payback_Sort", ascending=True)
    df_payback = df_payback.drop("Payback_Sort", axis=1)
    st.dataframe(df_payback, width='stretch', hide_index=True)

with tab3:
    # Sort by Annual Savings
    sortable_data = []
    for calc in calculations:
        sortable_data.append({
            "Processo": calc.process_name,
            "Departamento": getattr(calc, 'department', 'N/A'),
            "Economia Mensal": f"R$ {calc.monthly_savings:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "Economia Anual": f"R$ {calc.annual_savings:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "Payback": f"{calc.payback_period_months:.1f}m",
            "ROI %": f"{calc.roi_percentage_first_year:.1f}%",
            "Economia_Sort": calc.annual_savings,
        })
    
    df_savings = pd.DataFrame(sortable_data)
    df_savings = df_savings.sort_values("Economia_Sort", ascending=False)
    df_savings = df_savings.drop("Economia_Sort", axis=1)
    st.dataframe(df_savings, width='stretch', hide_index=True)

st.divider()

# Statistics summary
st.subheader("📈 Estatísticas Gerais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_roi = sum(c.roi_percentage_first_year for c in calculations) / len(calculations)
    st.metric("ROI Médio", f"{avg_roi:.1f}%")

with col2:
    avg_payback = sum(c.payback_period_months for c in calculations) / len(calculations)
    st.metric("Payback Médio", f"{avg_payback:.1f}m")

with col3:
    total_savings = sum(c.annual_savings for c in calculations)
    st.metric("Economia Total Anual", format_currency(total_savings))

with col4:
    total_processes = len(calculations)
    st.metric("Total de Processos", total_processes)
