# -*- coding: utf-8 -*-
"""Dashboard Executivo - Overview, Ranking e Análise Comparativa com 3 Abas"""
import streamlit as st
import pandas as pd

from config import APP_NAME
from src.database import DatabaseManager
from src.ui.auth import require_auth
from src.ui.auth_components import render_logout_button
from src.ui import EmptyStateManager
from src.services import (
    MetricsCalculator,
    PageService,
    DataFrameBuilder,
    ChartFactory,
)

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Auth gate
if "auth_user" not in st.session_state or st.session_state.auth_user is None:
    st.switch_page("app.py")

if not require_auth(form_key="dashboard_login"):
    st.stop()

render_logout_button("dashboard")

# ========== DATA LOADING ==========
user_context = PageService.get_user_context()
current_user_id = user_context["current_user_id"]
is_admin = user_context["is_admin"]
user_filter = user_context["user_filter"]

with st.spinner("⏳ Carregando dados do dashboard..."):
    db_manager = DatabaseManager()
    success, calculations, error_msg = db_manager.get_all_calculations(
        user_id=user_filter, use_cache=True
    )

if not success:
    EmptyStateManager.show_error_message(f"Erro ao carregar dashboard: {error_msg}")
    st.stop()

if not calculations:
    EmptyStateManager.show_no_processes_empty_state()
    st.stop()

# ========== HEADER ==========
st.title("📊 Dashboard Executivo")
if is_admin and user_filter is None:
    st.markdown("Visão geral de **todos os processos RPA** (Admin)")
else:
    st.markdown("Visão geral dos **seus processos RPA**")
st.divider()

# ========== KEY METRICS - ALWAYS VISIBLE ==========
st.markdown("### 📈 Indicadores Principais")

metrics = MetricsCalculator.aggregate_metrics(calculations)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "🔢 Processos",
        metrics["total_processes"],
        help="Total de processos analisados"
    )

with col2:
    from src.calculator.utils import format_currency
    st.metric(
        "💰 Economia Anual",
        format_currency(metrics["total_savings"]),
        delta=f"R$ {(metrics['total_savings']/12):,.0f}/mês",
        help="Economia total por ano"
    )

with col3:
    st.metric(
        "💡 ROI Médio",
        f"{metrics['avg_roi']:.1f}%",
        delta=f"Mediana: {metrics['median_roi']:.1f}%",
        help="Retorno médio vs. mediano no primeiro ano"
    )

with col4:
    st.metric(
        "⏱️ Payback Médio",
        f"{metrics['avg_payback']:.1f}m",
        delta=f"Min: {metrics['min_payback']:.1f}m | Max: {metrics['max_payback']:.1f}m",
        help="Tempo médio para recuperar investimento"
    )

with col5:
    st.metric(
        "💻 Investimento Total",
        format_currency(metrics["total_investment"]),
        help="Total investido em RPA"
    )

st.divider()

# ========== TABS - ANALYSIS SECTIONS ==========
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏆 Ranking", "🔍 Comparativo"])

# ====== TAB 1: OVERVIEW ======
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Distribuição de Automação")
        classification = MetricsCalculator.classify_processes(calculations)
        automation_data = {
            "Altamente Automatizável (≥70%)": {
                "count": len(classification["highly_automatable"]),
                "label": "≥70% automação"
            },
            "Parcialmente (30-70%)": {
                "count": len(classification["partially_automatable"]),
                "label": "30-70% automação"
            },
            "Complexo (<30%)": {
                "count": len(classification["complex"]),
                "label": "<30% automação"
            },
        }
        fig_automation = ChartFactory.pie_distribution(
            automation_data, title=""
        )
        st.plotly_chart(fig_automation, use_container_width=True)
    
    with col2:
        st.markdown("#### ⏱️ Distribuição de Payback")
        payback_dist = MetricsCalculator.payback_distribution(calculations)
        fig_payback = ChartFactory.pie_distribution(
            payback_dist, title=""
        )
        st.plotly_chart(fig_payback, use_container_width=True)
    
    st.markdown("#### 🏆 Top 5 Processos por ROI")
    top_5 = MetricsCalculator.top_by_metric(calculations, metric="roi", top=5)
    df_top5 = DataFrameBuilder.build_calculations_table(
        top_5,
        columns=["process", "automation", "investment", "annual_savings", "roi", "payback"],
        include_rank=True
    )
    st.dataframe(df_top5, use_container_width=True, hide_index=True)

# ====== TAB 2: RANKING ======
with tab2:
    st.markdown("#### 🏆 Top 10 Processos")
    
    # Metric selector
    ranking_metric = st.radio(
        "Ordenar por:",
        options=["ROI", "Payback", "Economia"],
        horizontal=True
    )
    
    # Get top 10 by selected metric
    if ranking_metric == "ROI":
        top_10 = MetricsCalculator.top_by_metric(calculations, metric="roi", top=10)
        metric_col = "ROI (%)"
        ascending = False
    elif ranking_metric == "Payback":
        top_10 = MetricsCalculator.top_by_metric(calculations, metric="payback", top=10)
        metric_col = "Payback (meses)"
        ascending = True
    else:  # Economia
        top_10 = MetricsCalculator.top_by_metric(calculations, metric="savings", top=10)
        metric_col = "Economia/Ano"
        ascending = False
    
    # Prepare data for chart
    ranking_data = []
    for i, calc in enumerate(top_10, 1):
        if ranking_metric == "ROI":
            value = calc.roi_percentage_first_year
        elif ranking_metric == "Payback":
            value = calc.payback_period_months
        else:
            value = calc.annual_savings
        
        ranking_data.append({
            "Processo": f"{i}. {calc.process_name}",
            metric_col: value
        })
    
    df_ranking = pd.DataFrame(ranking_data)
    
    # Create chart
    fig_ranking = ChartFactory.bar_ranking(
        df_ranking,
        metric_col=metric_col,
        process_col="Processo",
        title=f"Top 10 por {ranking_metric}",
        ascending=ascending,
        height=500
    )
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    st.markdown("#### 📊 Tabela Detalhada (Top 10)")
    df_top10 = DataFrameBuilder.build_calculations_table(
        top_10,
        columns=["process", "department", "automation", "investment", "annual_savings", "roi", "payback"],
        include_rank=True
    )
    st.dataframe(df_top10, use_container_width=True, hide_index=True)

# ====== TAB 3: COMPARATIVO ======
with tab3:
    st.markdown("#### 📊 Análise de Correlação: ROI vs Payback")
    
    # Prepare scatter data
    scatter_data = pd.DataFrame([
        {
            "Processo": c.process_name,
            "ROI (%)": c.roi_percentage_first_year,
            "Payback (meses)": c.payback_period_months,
            "Economia/Ano": c.annual_savings,
            "Automação (%)": c.expected_automation_percentage,
        }
        for c in calculations
    ])
    
    fig_scatter = ChartFactory.scatter_correlation(
        scatter_data,
        x_col="ROI (%)",
        y_col="Payback (meses)",
        size_col="Economia/Ano",
        color_col="Automação (%)",
        title="Correlação: ROI vs Payback (tamanho = economia)",
        height=500
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("#### 💰 Distribuição de ROI")
    fig_roi_dist = ChartFactory.histogram_distribution(
        scatter_data,
        col="ROI (%)",
        title="Distribuição de ROI (%)",
        nbins=15,
        height=400
    )
    st.plotly_chart(fig_roi_dist, use_container_width=True)

st.divider()

# ========== DETAILED TABLE - ALWAYS AT BOTTOM ==========
st.markdown("### 📋 Todos os Processos")

# Add filters
col1, col2, col3 = st.columns(3)

with col1:
    automation_filter = st.slider(
        "Filtrar por Automação (%)",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=5
    )

with col2:
    payback_filter = st.slider(
        "Filtrar por Payback (meses)",
        min_value=0,
        max_value=int(metrics["max_payback"]) + 1,
        value=(0, int(metrics["max_payback"]) + 1),
        step=1
    )

with col3:
    roi_filter = st.slider(
        "Filtrar por ROI (%)",
        min_value=int(metrics["min_roi"]),
        max_value=int(metrics["max_roi"]) + 1,
        value=(int(metrics["min_roi"]), int(metrics["max_roi"]) + 1),
        step=50
    )

# Apply filters
filtered_calculations = [
    c for c in calculations
    if (automation_filter[0] <= c.expected_automation_percentage <= automation_filter[1]
        and payback_filter[0] <= c.payback_period_months <= payback_filter[1]
        and roi_filter[0] <= c.roi_percentage_first_year <= roi_filter[1])
]

if filtered_calculations:
    df_all = DataFrameBuilder.build_detailed_table(filtered_calculations)
    st.dataframe(
        df_all,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Processo": st.column_config.TextColumn(width="large"),
            "Departamento": st.column_config.TextColumn(width="medium"),
            "Automação": st.column_config.TextColumn(width="small"),
            "Investimento": st.column_config.TextColumn(width="medium"),
            "Economia/Mês": st.column_config.TextColumn(width="medium"),
            "Economia/Ano": st.column_config.TextColumn(width="medium"),
            "ROI (%)": st.column_config.TextColumn(width="small"),
            "Payback (meses)": st.column_config.TextColumn(width="small"),
            "Capacidade (h/mês)": st.column_config.TextColumn(width="small"),
        }
    )
else:
    st.info("Nenhum processo encontrado com esses filtros")
