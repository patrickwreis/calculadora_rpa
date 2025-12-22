# -*- coding: utf-8 -*-
"""Dashboard Executivo - Overview, Ranking e Análise Comparativa com 3 Abas"""
import streamlit as st

from config import APP_NAME
from src.database import DatabaseManager
from src.ui.auth import require_auth
from src.ui.auth_components import render_logout_button
from src.ui import EmptyStateManager
from src.calculator.utils import format_currency, calculate_automation_metrics
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
    st.switch_page("streamlit_app.py")

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

# Calcula FTE (Full Time Equivalent) - considera 220h/mês como padrão (44h semanais CLT Brasil)
HOURS_PER_FTE = 220
total_fte = 0.0
for c in calculations:
    metrics_calc = calculate_automation_metrics(
        expected_automation_percentage=c.expected_automation_percentage,
        exception_rate=getattr(c, 'exception_rate', 0.0)
    )
    freed_hours = c.current_time_per_month * (metrics_calc["fully_automated_pct"] / 100.0)
    total_fte += freed_hours / HOURS_PER_FTE

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "🔢 Processos",
        metrics["total_processes"],
        help="Total de processos analisados"
    )

with col2:
    st.metric(
        "💰 Economia Anual",
        format_currency(metrics["total_savings"]),
        delta=f"R$ {(metrics['total_savings']/12):,.0f}/mês",
        help="Economia total por ano"
    )

with col3:
    st.metric(
        "👥 FTE Liberado",
        f"{total_fte:.1f}",
        delta="Full Time Equivalent",
        help="Total de pessoas equivalentes liberadas (220h/mês - CLT Brasil)"
    )

with col4:
    st.metric(
        "💡 ROI Médio",
        f"{metrics['avg_roi']:.1f}%",
        delta=f"Mediana: {metrics['median_roi']:.1f}%",
        help="Retorno médio vs. mediano no primeiro ano"
    )

with col5:
    st.metric(
        "⏱️ Payback Médio",
        f"{metrics['avg_payback']:.1f}m",
        delta=f"Min: {metrics['min_payback']:.1f}m | Max: {metrics['max_payback']:.1f}m",
        help="Tempo médio para recuperar investimento"
    )

with col6:
    st.metric(
        "💻 Investimento Total",
        format_currency(metrics["total_investment"]),
        help="Total investido em RPA"
    )

# Destaques
st.markdown("#### 🏅 Destaques")
best_roi_calc = max(calculations, key=lambda c: c.roi_percentage_first_year)
best_payback_calc = min(calculations, key=lambda c: c.payback_period_months)
best_savings_calc = max(calculations, key=lambda c: c.annual_savings)

# Calcula FTE por processo e encontra o maior
calc_with_fte = []
for c in calculations:
    metrics_calc = calculate_automation_metrics(
        expected_automation_percentage=c.expected_automation_percentage,
        exception_rate=getattr(c, 'exception_rate', 0.0)
    )
    freed_hours = c.current_time_per_month * (metrics_calc["fully_automated_pct"] / 100.0)
    fte_value = freed_hours / HOURS_PER_FTE
    calc_with_fte.append((c, fte_value))

best_fte_calc, best_fte_value = max(calc_with_fte, key=lambda x: x[1])

colh1, colh2, colh3, colh4 = st.columns(4)

with colh1:
    st.metric(
        "Maior ROI",
        f"{best_roi_calc.process_name}",
        delta=f"{best_roi_calc.roi_percentage_first_year:.0f}%",
        help="Processo com maior ROI na seleção atual"
    )

with colh2:
    st.metric(
        "Menor payback",
        f"{best_payback_calc.process_name}",
        delta=f"{best_payback_calc.payback_period_months:.1f} meses",
        help="Processo com menor tempo de payback"
    )

with colh3:
    st.metric(
        "Maior economia anual",
        f"{best_savings_calc.process_name}",
        delta=f"{format_currency(best_savings_calc.annual_savings)}",
        help="Processo com maior economia anual estimada"
    )

with colh4:
    st.metric(
        "Maior FTE liberado",
        f"{best_fte_calc.process_name}",
        delta=f"{best_fte_value:.2f} FTE",
        help="Processo que libera mais pessoas equivalentes"
    )

st.divider()

# ========== TABS - ANALYSIS SECTIONS ==========
tab1, tab2 = st.tabs([
    "📈 Overview",
    "🏅 Ranking & Comparativo",
])

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
        st.plotly_chart(fig_automation, width='stretch')
    
    with col2:
        st.markdown("#### ⏱️ Distribuição de Payback")
        payback_dist = MetricsCalculator.payback_distribution(calculations)
        fig_payback = ChartFactory.pie_distribution(
            payback_dist, title=""
        )
        st.plotly_chart(fig_payback, width='stretch')
    
    st.markdown("#### 🏆 Top 5 Processos por ROI")
    top_5 = MetricsCalculator.top_by_metric(calculations, metric="roi", top=5)
    df_top5 = DataFrameBuilder.build_calculations_table(
        top_5,
        columns=["process", "automation", "investment", "annual_savings", "roi", "payback"],
        include_rank=True
    )
    st.dataframe(df_top5, width='stretch', hide_index=True)

# ====== TAB 2: RANKING & COMPARATIVO ======
with tab2:
    st.markdown("#### 🏆 Ranking e Comparativo")

    col_a, col_b, col_c = st.columns([2, 1, 2])

    with col_a:
        ranking_metric = st.radio(
            "Ordenar por:",
            options=["ROI", "Payback", "Economia"],
            horizontal=True,
            help="ROI e Economia em ordem decrescente; Payback em ordem crescente."
        )

    with col_b:
        top_n = st.selectbox(
            "Quantidade (quando sem filtro)",
            options=[10, 20, 50, 100],
            index=0,
            help="Usado apenas quando nenhum processo é selecionado."
        )

    process_names = [c.process_name for c in calculations]
    default_selection = []

    with col_c:
        selected_processes = st.multiselect(
            "Filtrar processos (vazio = todos)",
            options=process_names,
            default=default_selection,
            max_selections=5,
        )

    metric_key = {
        "ROI": "roi",
        "Payback": "payback",
        "Economia": "savings",
    }[ranking_metric]

    if selected_processes:
        base_set = [c for c in calculations if c.process_name in selected_processes]
        top_limit = len(base_set)
    else:
        base_set = calculations
        top_limit = top_n

    ordered_set = MetricsCalculator.top_by_metric(
        base_set,
        metric=metric_key,
        top=top_limit
    )

    if not ordered_set:
        st.info("Nenhum processo encontrado.")
    else:
        highlight_cols = {
            "ROI": "ROI (%)",
            "Payback": "Payback (meses)",
            "Economia": "Economia/Ano",
        }
        order_col = highlight_cols[ranking_metric]

        st.markdown(f"##### 📋 Tabela — ordenado por {order_col}")
        df_rank = DataFrameBuilder.build_calculations_table(
            ordered_set,
            columns=["process", "department", "automation", "investment", "annual_savings", "roi", "payback"],
            include_rank=True,
        )

        st.dataframe(
            df_rank,
            width='stretch',
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn(label="#", width="small"),
                "Processo": st.column_config.TextColumn(width="large"),
                "Departamento": st.column_config.TextColumn(width="medium"),
                "Automação": st.column_config.TextColumn(width="small"),
                "Investimento": st.column_config.TextColumn(width="medium"),
                "Economia/Ano": st.column_config.TextColumn(width="medium"),
                "ROI (%)": st.column_config.TextColumn(width="small"),
                "Payback (meses)": st.column_config.TextColumn(width="small"),
            },
        )

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
        width='stretch',
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
