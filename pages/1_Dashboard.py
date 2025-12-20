# -*- coding: utf-8 -*-
"""Dashboard - Overview and Statistics with Professional UI"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from config import APP_NAME
from src.calculator.utils import format_currency, format_percentage
from src.database import DatabaseManager
from src.ui.components import page_header

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
db_manager = DatabaseManager()

# Get calculations with loading indicator
with st.spinner("⏳ Carregando dados do dashboard..."):
    success, calculations, error_msg = db_manager.get_all_calculations(use_cache=True)
    if not success:
        st.error(f"Erro ao carregar dashboard: {error_msg}")
        st.stop()

if not calculations:
    st.info("📋 Nenhum processo cadastrado ainda. Comece criando um novo cálculo na aba 'Novo Processo'!")
    st.stop()

# ========== HEADER ==========
st.title("📊 Dashboard Executivo")
st.markdown("Visão geral de todos os seus processos RPA")
st.divider()

# ========== KEY METRICS SECTION ==========
st.markdown("### 📈 Indicadores Principais")

with st.spinner("📊 Calculando métricas..."):
    total_processes = len(calculations)
    total_annual_savings = sum(c.annual_savings for c in calculations)
    total_investment = sum(c.rpa_implementation_cost for c in calculations)
    avg_roi = sum(c.roi_percentage_first_year for c in calculations) / len(calculations)
    avg_payback = sum(c.payback_period_months for c in calculations) / len(calculations)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "🔢 Processos",
        total_processes,
        help="Total de processos analisados"
    )

with col2:
    st.metric(
        "💰 Economia Anual",
        format_currency(total_annual_savings),
        delta=f"R$ {(total_annual_savings/12):.0f}/mês",
        help="Economia total por ano"
    )

with col3:
    st.metric(
        "💡 ROI Médio",
        f"{avg_roi:.1f}%",
        delta=f"+{avg_roi-100:.1f}%" if avg_roi > 100 else f"{avg_roi-100:.1f}%",
        help="Retorno médio no primeiro ano"
    )

with col4:
    st.metric(
        "⏱️ Payback Médio",
        f"{avg_payback:.1f}",
        "meses",
        help="Tempo médio para recuperar investimento"
    )

with col5:
    st.metric(
        "💻 Investimento Total",
        format_currency(total_investment),
        help="Total investido em RPA"
    )

st.divider()

# ========== CHARTS SECTION ==========
st.markdown("### 📊 Análises Visuais")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: ROI Distribution
with chart_col1:
    roi_data = pd.DataFrame([
        {"Processo": c.process_name, "ROI %": c.roi_percentage_first_year}
        for c in calculations
    ]).sort_values("ROI %", ascending=True)
    
    fig_roi = px.bar(
        roi_data,
        x="ROI %",
        y="Processo",
        orientation="h",
        title="ROI por Processo (%)",
        color="ROI %",
        color_continuous_scale="RdYlGn",
        labels={"ROI %": "ROI (%)"},
        height=400
    )
    fig_roi.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(l=150, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_roi, use_container_width=True)

# Chart 2: Payback Timeline
with chart_col2:
    payback_data = pd.DataFrame([
        {"Processo": c.process_name, "Payback (meses)": c.payback_period_months}
        for c in calculations
    ]).sort_values("Payback (meses)")
    
    fig_payback = px.bar(
        payback_data,
        x="Payback (meses)",
        y="Processo",
        orientation="h",
        title="Payback por Processo (meses)",
        color="Payback (meses)",
        color_continuous_scale="Viridis",
        height=400
    )
    fig_payback.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(l=150, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_payback, use_container_width=True)

st.divider()

# ========== SAVINGS ANALYSIS ==========
st.markdown("### 💰 Análise de Economia")

savings_col1, savings_col2 = st.columns(2)

with savings_col1:
    # Monthly vs Annual Savings
    savings_data = pd.DataFrame([
        {
            "Processo": c.process_name,
            "Mensal": c.monthly_savings,
            "Anual": c.annual_savings
        }
        for c in sorted(calculations, key=lambda x: x.annual_savings, reverse=True)[:8]
    ])
    
    fig_savings = go.Figure(data=[
        go.Bar(name="Mensal", x=savings_data["Processo"], y=savings_data["Mensal"]),
        go.Bar(name="Anual", x=savings_data["Processo"], y=savings_data["Anual"])
    ])
    fig_savings.update_layout(
        title="Economia Mensal vs Anual (Top 8)",
        barmode="group",
        height=400,
        hovermode="x unified",
        margin=dict(b=80)
    )
    st.plotly_chart(fig_savings, use_container_width=True)

with savings_col2:
    # Investment vs Savings
    top_processes = sorted(calculations, key=lambda x: x.annual_savings, reverse=True)[:8]
    invest_data = pd.DataFrame([
        {
            "Processo": c.process_name,
            "Investimento": c.rpa_implementation_cost,
            "Economia Anual": c.annual_savings
        }
        for c in top_processes
    ])
    
    fig_invest = px.scatter(
        invest_data,
        x="Investimento",
        y="Economia Anual",
        size="Economia Anual",
        hover_name="Processo",
        title="Investimento vs Economia Anual",
        height=400,
        color_discrete_sequence=["#636EFA"]
    )
    fig_invest.update_layout(
        hovermode="closest",
        margin=dict(l=60, r=20, t=40, b=60)
    )
    st.plotly_chart(fig_invest, use_container_width=True)

st.divider()

# ========== TOP PERFORMERS CARDS ==========
st.markdown("### 🏆 Destaques")

top_roi = max(calculations, key=lambda x: x.roi_percentage_first_year)
top_savings = max(calculations, key=lambda x: x.annual_savings)
fastest_payback = min(calculations, key=lambda x: x.payback_period_months)

top_col1, top_col2, top_col3 = st.columns(3)

with top_col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;'>
        <h3 style='margin: 0;'>🎯 Maior ROI</h3>
        <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{:.1f}%</p>
        <p style='margin: 5px 0; font-size: 14px;'><strong>{}</strong></p>
        <p style='margin: 0; font-size: 12px; opacity: 0.9;'>Economia: {}</p>
    </div>
    """.format(
        top_roi.roi_percentage_first_year,
        top_roi.process_name,
        format_currency(top_roi.annual_savings)
    ), unsafe_allow_html=True)

with top_col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white;'>
        <h3 style='margin: 0;'>💸 Maior Economia</h3>
        <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{}</p>
        <p style='margin: 5px 0; font-size: 14px;'><strong>{}</strong></p>
        <p style='margin: 0; font-size: 12px; opacity: 0.9;'>Payback: {:.1f} meses</p>
    </div>
    """.format(
        format_currency(top_savings.annual_savings),
        top_savings.process_name,
        top_savings.payback_period_months
    ), unsafe_allow_html=True)

with top_col3:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; color: white;'>
        <h3 style='margin: 0;'>⚡ Payback Mais Rápido</h3>
        <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{:.1f} meses</p>
        <p style='margin: 5px 0; font-size: 14px;'><strong>{}</strong></p>
        <p style='margin: 0; font-size: 12px; opacity: 0.9;'>ROI: {:.1f}%</p>
    </div>
    """.format(
        fastest_payback.payback_period_months,
        fastest_payback.process_name,
        fastest_payback.roi_percentage_first_year
    ), unsafe_allow_html=True)

st.divider()

# ========== DETAILED TABLE ==========
st.markdown("### 📋 Detalhes Completos")

# Create detailed dataframe
detailed_data = []
for calc in calculations:
    detailed_data.append({
        "Processo": calc.process_name,
        "Departamento": getattr(calc, 'department', 'N/A'),
        "Investimento": format_currency(calc.rpa_implementation_cost),
        "Economia/Mês": format_currency(calc.monthly_savings),
        "Economia/Ano": format_currency(calc.annual_savings),
        "ROI (%)": f"{calc.roi_percentage_first_year:.1f}%",
        "Payback": f"{calc.payback_period_months:.1f}m",
        "Automação": f"{calc.expected_automation_percentage:.0f}%",
    })

df_detailed = pd.DataFrame(detailed_data)

# Display with styling
st.dataframe(
    df_detailed,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Processo": st.column_config.TextColumn(width="large"),
        "Departamento": st.column_config.TextColumn(width="medium"),
        "Investimento": st.column_config.TextColumn(width="medium"),
        "Economia/Mês": st.column_config.TextColumn(width="medium"),
        "Economia/Ano": st.column_config.TextColumn(width="medium"),
        "ROI (%)": st.column_config.TextColumn(width="small"),
        "Payback": st.column_config.TextColumn(width="small"),
        "Automação": st.column_config.TextColumn(width="small"),
    }
)

st.divider()

# ========== SUMMARY STATISTICS ==========
st.markdown("### 📊 Distribuição e Estatísticas")

stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.markdown("#### Complexidade")
    complexity_counts = {}
    for calc in calculations:
        complexity = getattr(calc, 'complexity', 'Não definida')
        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
    
    complexity_df = pd.DataFrame(
        list(complexity_counts.items()),
        columns=["Nível", "Quantidade"]
    )
    fig_complexity = px.pie(
        complexity_df,
        values="Quantidade",
        names="Nível",
        title="Distribuição de Complexidade",
        height=300
    )
    st.plotly_chart(fig_complexity, use_container_width=True)

with stat_col2:
    st.markdown("#### Potencial de Automação")
    automation_ranges = {
        "Altamente Automatizável (≥70%)": len([c for c in calculations if c.expected_automation_percentage >= 70]),
        "Parcialmente (30-70%)": len([c for c in calculations if 30 <= c.expected_automation_percentage < 70]),
        "Complexo (<30%)": len([c for c in calculations if c.expected_automation_percentage < 30]),
    }
    
    automation_df = pd.DataFrame(
        list(automation_ranges.items()),
        columns=["Categoria", "Quantidade"]
    )
    fig_automation = px.pie(
        automation_df,
        values="Quantidade",
        names="Categoria",
        title="Potencial de Automação",
        height=300
    )
    st.plotly_chart(fig_automation, use_container_width=True)

with stat_col3:
    st.markdown("#### Status de Payback")
    payback_ranges = {
        "Rápido (<6 meses)": len([c for c in calculations if c.payback_period_months < 6]),
        "Médio (6-12 meses)": len([c for c in calculations if 6 <= c.payback_period_months <= 12]),
        "Longo (>12 meses)": len([c for c in calculations if c.payback_period_months > 12]),
    }
    
    payback_df = pd.DataFrame(
        list(payback_ranges.items()),
        columns=["Categoria", "Quantidade"]
    )
    fig_payback_dist = px.pie(
        payback_df,
        values="Quantidade",
        names="Categoria",
        title="Distribuição de Payback",
        height=300
    )
    st.plotly_chart(fig_payback_dist, use_container_width=True)
