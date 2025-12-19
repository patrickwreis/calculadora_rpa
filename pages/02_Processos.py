# -*- coding: utf-8 -*-
"""Results History Page with Rankings and CRUD Operations"""
import streamlit as st
import pandas as pd
from datetime import datetime
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
    page_title=f"{APP_NAME} - Histórico",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Initialize database
db_manager = DatabaseManager()

# Page header
page_header("Histórico de Cálculos", "Visualize, classifique e gerencie todos os seus cálculos de ROI")

# Get calculations
calculations = db_manager.get_all_calculations()

if not calculations:
    st.info("📋 Nenhum cálculo salvo ainda. Comece criando um novo cálculo!")
    st.stop()

# Tab navigation
tab1, tab2, tab3 = st.tabs(["📊 Rankings e Resumo", "✏️ Editar/Excluir", "🔍 Detalhes"])

# ========== TAB 1: RANKINGS ==========
with tab1:
    # Rankings
    st.subheader("🏆 Rankings")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Top ROI (%)**")
        for i, c in enumerate(rank_by_roi(calculations, top=5), start=1):
            st.write(f"{i}. {c.process_name} — {format_percentage(c.roi_percentage_first_year)}")

    with col2:
        st.markdown("**Melhor Payback (meses)**")
        for i, c in enumerate(rank_by_payback(calculations, top=5), start=1):
            st.write(f"{i}. {c.process_name} — {format_months(c.payback_period_months)}")

    with col3:
        st.markdown("**Maior Economia Anual**")
        for i, c in enumerate(rank_by_annual_savings(calculations, top=5), start=1):
            st.write(f"{i}. {c.process_name} — {format_currency(c.annual_savings)}")

    st.divider()

    # Create dataframe
    data = []
    for calc in calculations:
        data.append(
            {
                "ID": calc.id,
                "Processo": calc.process_name,
                "Economia Mensal": format_currency(calc.monthly_savings),
                "Economia Anual": format_currency(calc.annual_savings),
                "Payback": format_months(calc.payback_period_months),
                "ROI %": format_percentage(calc.roi_percentage_first_year),
                "Data": calc.created_at.strftime("%d/%m/%Y %H:%M"),
            }
        )

    df = pd.DataFrame(data)

    st.subheader("📊 Resumo dos Cálculos")
    st.dataframe(df, width="stretch")


# ========== TAB 2: EDITAR/EXCLUIR ==========
with tab2:
    st.subheader("✏️ Editar Cálculo")
    
    # Select calculation to edit
    selected_calc_id = st.selectbox(
        "Selecione um cálculo para editar:",
        [calc.id for calc in calculations],
        format_func=lambda x: f"ID {x} - {next(c.process_name for c in calculations if c.id == x)}",
        key="edit_selectbox"
    )
    
    selected_calc = next(c for c in calculations if c.id == selected_calc_id)
    
    st.divider()
    
    # Edit form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Informações do Processo")
        process_name = st.text_input("Nome do Processo", value=selected_calc.process_name)
        current_time = st.number_input("Horas/Mês", value=selected_calc.current_time_per_month, min_value=0.0)
        people_involved = st.number_input("Pessoas Envolvidas", value=selected_calc.people_involved, min_value=1)
        hourly_rate = st.number_input("Taxa Horária (R$)", value=selected_calc.hourly_rate, min_value=0.0)
        automation_percentage = st.slider("Automação Esperada (%)", value=int(selected_calc.expected_automation_percentage), min_value=0, max_value=100)
    
    with col2:
        st.markdown("### 💰 Custos")
        rpa_implementation = st.number_input("Custo de Implementação (R$)", value=selected_calc.rpa_implementation_cost, min_value=0.0)
        rpa_monthly = st.number_input("Custo Mensal RPA (R$)", value=selected_calc.rpa_monthly_cost, min_value=0.0)
        monthly_savings = st.number_input("Economia Mensal (R$)", value=selected_calc.monthly_savings, min_value=0.0)
        annual_savings = st.number_input("Economia Anual (R$)", value=selected_calc.annual_savings, min_value=0.0)
    
    st.divider()
    
    # Buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Atualizar", type="primary", use_container_width=True):
            update_data = {
                "process_name": process_name,
                "current_time_per_month": current_time,
                "people_involved": people_involved,
                "hourly_rate": hourly_rate,
                "expected_automation_percentage": automation_percentage,
                "rpa_implementation_cost": rpa_implementation,
                "rpa_monthly_cost": rpa_monthly,
                "monthly_savings": monthly_savings,
                "annual_savings": annual_savings,
                "updated_at": datetime.utcnow(),
            }
            
            updated = db_manager.update_calculation(int(selected_calc_id), update_data)
            if updated:
                st.success("✅ Cálculo atualizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar cálculo")
    
    with col2:
        if st.button("🗑️ Excluir", type="secondary", use_container_width=True):
            if db_manager.delete_calculation(int(selected_calc_id)):
                st.success("✅ Cálculo excluído com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao excluir cálculo")


# ========== TAB 3: DETALHES COMPLETOS ==========
with tab3:
    st.subheader("🔍 Detalhes Completos do Cálculo")
    
    # Select calculation to view
    selected_calc_id = st.selectbox(
        "Selecione um cálculo para visualizar detalhes completos:",
        [calc.id for calc in calculations],
        format_func=lambda x: f"ID {x} - {next(c.process_name for c in calculations if c.id == x)}",
        key="details_selectbox"
    )
    
    selected_calc = next(c for c in calculations if c.id == selected_calc_id)
    
    st.divider()
    
    # Detailed view
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Informações do Processo")
        st.write(f"**ID:** {selected_calc.id}")
        st.write(f"**Nome:** {selected_calc.process_name}")
        st.write(f"**Horas/Mês:** {selected_calc.current_time_per_month}")
        st.write(f"**Pessoas Envolvidas:** {selected_calc.people_involved}")
        st.write(f"**Taxa Horária:** {format_currency(selected_calc.hourly_rate)}")
        st.write(f"**Automação Esperada:** {selected_calc.expected_automation_percentage:.0f}%")
    
    with col2:
        st.markdown("### 💰 Resultados")
        st.write(f"**Economia Mensal:** {format_currency(selected_calc.monthly_savings)}")
        st.write(f"**Economia Anual:** {format_currency(selected_calc.annual_savings)}")
        st.write(f"**Payback:** {format_months(selected_calc.payback_period_months)}")
        st.write(f"**ROI 1º Ano:** {format_percentage(selected_calc.roi_percentage_first_year)}")
        st.write(f"**Retorno Absoluto:** {format_currency(selected_calc.roi_first_year)}")
    
    st.divider()
    
    # Costs breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Custos")
        st.write(f"**Implementação:** {format_currency(selected_calc.rpa_implementation_cost)}")
        st.write(f"**Mensal:** {format_currency(selected_calc.rpa_monthly_cost)}")
    
    with col2:
        st.markdown("### 📅 Timestamps")
        st.write(f"**Criado em:** {selected_calc.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        st.write(f"**Atualizado em:** {selected_calc.updated_at.strftime('%d/%m/%Y %H:%M:%S')}")
