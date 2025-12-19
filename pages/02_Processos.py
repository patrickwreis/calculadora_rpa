# -*- coding: utf-8 -*-
"""Results History Page with Rankings"""
import streamlit as st
import pandas as pd
from src.database import DatabaseManager
from src.ui.styles import apply_custom_styles
from src.ui.components import header
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

# Apply custom styles
apply_custom_styles()

# Initialize database
db_manager = DatabaseManager()

# Page header
header("Histórico de Cálculos", "Visualize, classifique e gerencie todos os seus cálculos de ROI")

# Get calculations
calculations = db_manager.get_all_calculations()

if not calculations:
    st.info("📋 Nenhum cálculo salvo ainda. Comece criando um novo cálculo!")
    st.stop()

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

st.divider()

# Detailed view
st.subheader("🔍 Detalhes dos Cálculos")

selected_calc_id = st.selectbox(
    "Selecione um cálculo para visualizar detalhes:",
    [calc.id for calc in calculations],
    format_func=lambda x: f"ID {x} - {next(c.process_name for c in calculations if c.id == x)}",
)

selected_calc = next(c for c in calculations if c.id == selected_calc_id)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 Informações do Processo")
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

# Delete option
col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🗑️ Excluir Cálculo", type="secondary"):
        # Defensive check: ensure selected_calc_id is a valid int before deleting
        try:
            if selected_calc_id is None:
                st.error("❌ Nenhum cálculo selecionado para exclusão.")
            else:
                calc_id_int = int(selected_calc_id)
                deleted = db_manager.delete_calculation(calc_id_int)
                if deleted:
                    st.success("✅ Cálculo excluído!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Não foi possível excluir o cálculo (não encontrado).")
        except Exception as e:
            st.error(f"❌ Erro ao excluir cálculo: {e}")
