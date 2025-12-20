# -*- coding: utf-8 -*-
"""Rankings Page - Top processes by ROI, Payback, and Savings with Advanced Visualizations"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import APP_NAME
from src.analysis.ranking import (
    rank_by_annual_savings,
    rank_by_payback,
    rank_by_roi,
)
from src.calculator.utils import format_currency, format_months, format_percentage
from src.database import DatabaseManager

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Rankings",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database
db_manager = DatabaseManager()

# Title and header
st.title("🏆 Rankings de Processos")
st.markdown("Veja quais processos têm melhor desempenho em ROI, Payback e Economia")
st.divider()

# Get calculations
success, calculations, error_msg = db_manager.get_all_calculations()

if not success or not calculations:
    if error_msg:
        st.error(f"❌ Erro ao carregar cálculos: {error_msg}")
    else:
        st.info("📋 Nenhum cálculo salvo ainda. Comece criando um novo cálculo!")
    st.stop()

# ========== TOP 3 PODIUM ==========
st.markdown("### 🥇 Pódio - Top 3 ROI")

roi_rankings = rank_by_roi(calculations, top=3)

podium_cols = st.columns(3)

# Gold - 1st place
with podium_cols[0]:
    if len(roi_rankings) >= 1:
        c = roi_rankings[0]
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <p style='font-size: 48px; margin: 0;'>🥇</p>
            <h3 style='margin: 10px 0 5px 0;'>1º Lugar</h3>
            <p style='margin: 5px 0; font-size: 16px; font-weight: bold;'>{}</p>
            <p style='margin: 5px 0; font-size: 18px; font-weight: bold; color: white;'>{:.1f}%</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.9;'>{}</p>
        </div>
        """.format(c.process_name, c.roi_percentage_first_year, format_currency(c.annual_savings)), 
        unsafe_allow_html=True)

# Silver - 2nd place  
with podium_cols[1]:
    if len(roi_rankings) >= 2:
        c = roi_rankings[1]
        st.markdown("""
        <div style='background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <p style='font-size: 48px; margin: 0;'>🥈</p>
            <h3 style='margin: 10px 0 5px 0;'>2º Lugar</h3>
            <p style='margin: 5px 0; font-size: 16px; font-weight: bold;'>{}</p>
            <p style='margin: 5px 0; font-size: 18px; font-weight: bold; color: white;'>{:.1f}%</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.9;'>{}</p>
        </div>
        """.format(c.process_name, c.roi_percentage_first_year, format_currency(c.annual_savings)), 
        unsafe_allow_html=True)

# Bronze - 3rd place
with podium_cols[2]:
    if len(roi_rankings) >= 3:
        c = roi_rankings[2]
        st.markdown("""
        <div style='background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <p style='font-size: 48px; margin: 0;'>🥉</p>
            <h3 style='margin: 10px 0 5px 0;'>3º Lugar</h3>
            <p style='margin: 5px 0; font-size: 16px; font-weight: bold;'>{}</p>
            <p style='margin: 5px 0; font-size: 18px; font-weight: bold; color: white;'>{:.1f}%</p>
            <p style='margin: 0; font-size: 12px; opacity: 0.9;'>{}</p>
        </div>
        """.format(c.process_name, c.roi_percentage_first_year, format_currency(c.annual_savings)), 
        unsafe_allow_html=True)

st.divider()

# ========== TABS WITH DIFFERENT RANKINGS ==========
tab1, tab2, tab3, tab4 = st.tabs(["📈 ROI (%)", "⏱️ Payback", "💰 Economia", "📊 Comparativo"])

# ========== TAB 1: ROI RANKINGS ==========
with tab1:
    st.markdown("### 📈 Top 10 - Melhor ROI (%)")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Create ROI chart
        roi_data = pd.DataFrame([
            {
                "Processo": c.process_name,
                "ROI (%)": c.roi_percentage_first_year,
                "Departamento": getattr(c, 'department', 'N/A')
            }
            for c in rank_by_roi(calculations, top=10)
        ])
        
        fig_roi = px.bar(
            roi_data,
            x="ROI (%)",
            y="Processo",
            orientation='h',
            color="ROI (%)",
            color_continuous_scale="Viridis",
            title="Top 10 Processos por ROI",
            height=500,
            hover_data={"Departamento": True}
        )
        fig_roi.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            hovermode="closest",
            margin=dict(l=200, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_roi)
    
    with col2:
        st.markdown("#### 🎯 Estatísticas de ROI")
        roi_values = [c.roi_percentage_first_year for c in calculations]
        st.metric("ROI Máximo", f"{max(roi_values):.1f}%")
        st.metric("ROI Mínimo", f"{min(roi_values):.1f}%")
        st.metric("ROI Médio", f"{sum(roi_values)/len(roi_values):.1f}%")
        st.metric("Mediana", f"{sorted(roi_values)[len(roi_values)//2]:.1f}%")

# ========== TAB 2: PAYBACK RANKINGS ==========
with tab2:
    st.markdown("### ⏱️ Top 10 - Menor Payback")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Create Payback chart
        payback_data = pd.DataFrame([
            {
                "Processo": c.process_name,
                "Payback (meses)": c.payback_period_months,
                "Departamento": getattr(c, 'department', 'N/A')
            }
            for c in rank_by_payback(calculations, top=10)
        ])
        
        fig_payback = px.bar(
            payback_data,
            x="Payback (meses)",
            y="Processo",
            orientation='h',
            color="Payback (meses)",
            color_continuous_scale="RdYlGn_r",
            title="Top 10 Processos por Payback (Menor é Melhor)",
            height=500,
            hover_data={"Departamento": True}
        )
        fig_payback.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            hovermode="closest",
            margin=dict(l=200, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_payback)
    
    with col2:
        st.markdown("#### ⏳ Estatísticas de Payback")
        payback_values = [c.payback_period_months for c in calculations]
        st.metric("Payback Mínimo", f"{min(payback_values):.1f} meses")
        st.metric("Payback Máximo", f"{max(payback_values):.1f} meses")
        st.metric("Payback Médio", f"{sum(payback_values)/len(payback_values):.1f} meses")
        
        # Classification
        fast = len([p for p in payback_values if p <= 6])
        medium = len([p for p in payback_values if 6 < p <= 12])
        slow = len([p for p in payback_values if p > 12])
        st.markdown(f"""
        **Classificação:**
        - ⚡ Rápido (≤6m): {fast}
        - 🔄 Médio (6-12m): {medium}
        - 🐢 Longo (>12m): {slow}
        """)

# ========== TAB 3: SAVINGS RANKINGS ==========
with tab3:
    st.markdown("### 💰 Top 10 - Maior Economia Anual")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Create Savings chart
        savings_data = pd.DataFrame([
            {
                "Processo": c.process_name,
                "Economia Anual": c.annual_savings,
                "Departamento": getattr(c, 'department', 'N/A')
            }
            for c in rank_by_annual_savings(calculations, top=10)
        ])
        
        fig_savings = px.bar(
            savings_data,
            x="Economia Anual",
            y="Processo",
            orientation='h',
            color="Economia Anual",
            color_continuous_scale="Greens",
            title="Top 10 Processos por Economia Anual",
            height=500,
            hover_data={"Departamento": True}
        )
        fig_savings.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            hovermode="closest",
            margin=dict(l=200, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_savings)
    
    with col2:
        st.markdown("#### 💵 Estatísticas de Economia")
        savings_values = [c.annual_savings for c in calculations]
        total_savings = sum(savings_values)
        
        st.metric("Economia Total/Ano", format_currency(total_savings))
        st.metric("Economia Máxima", format_currency(max(savings_values)))
        st.metric("Economia Mínima", format_currency(min(savings_values)))
        st.metric("Economia Média", format_currency(sum(savings_values)/len(savings_values)))

# ========== TAB 4: COMPARATIVE ANALYSIS ==========
with tab4:
    st.markdown("### 📊 Análise Comparativa")
    
    # Create comparison dataframe
    comparison_data = []
    for i, calc in enumerate(sorted(calculations, key=lambda x: x.roi_percentage_first_year, reverse=True)[:10], 1):
        comparison_data.append({
            "Posição": i,
            "Processo": calc.process_name,
            "ROI %": f"{calc.roi_percentage_first_year:.1f}",
            "Payback": f"{calc.payback_period_months:.1f}m",
            "Economia/Ano": format_currency(calc.annual_savings),
            "Investimento": format_currency(calc.rpa_implementation_cost),
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    st.dataframe(
        comparison_df,
        hide_index=True,
        column_config={
            "Posição": st.column_config.NumberColumn(width="small"),
            "Processo": st.column_config.TextColumn(width="large"),
            "ROI %": st.column_config.TextColumn(width="small"),
            "Payback": st.column_config.TextColumn(width="small"),
            "Economia/Ano": st.column_config.TextColumn(width="medium"),
            "Investimento": st.column_config.TextColumn(width="medium"),
        }
    )
    
    st.divider()
    
    # Scatter plot: ROI vs Payback
    scatter_data = pd.DataFrame([
        {
            "Processo": c.process_name,
            "ROI %": c.roi_percentage_first_year,
            "Payback": c.payback_period_months,
            "Economia": c.annual_savings,
            "Departamento": getattr(c, 'department', 'N/A')
        }
        for c in calculations
    ])
    
    fig_scatter = px.scatter(
        scatter_data,
        x="ROI %",
        y="Payback",
        size="Economia",
        hover_name="Processo",
        hover_data={"Departamento": True, "ROI %": ":.1f", "Payback": ":.1f"},
        title="ROI vs Payback (tamanho = Economia Anual)",
        height=500,
        color_discrete_sequence=["#1f77b4"]
    )
    
    # Add reference lines
    fig_scatter.add_hline(y=12, line_dash="dash", line_color="red", annotation_text="Limite 1 ano")
    fig_scatter.add_vline(x=100, line_dash="dash", line_color="green", annotation_text="ROI 100%")
    
    fig_scatter.update_layout(
        hovermode="closest",
        margin=dict(l=60, r=20, t=60, b=60)
    )
    
    st.plotly_chart(fig_roi)

st.divider()

# ========== EXPORT DATA ==========
st.markdown("### 📥 Exportar Dados")

export_col1, export_col2, col3 = st.columns(3)

with export_col1:
    # Create full ranking export data
    full_rankings = []
    for calc in sorted(calculations, key=lambda x: x.roi_percentage_first_year, reverse=True):
        full_rankings.append({
            "Processo": calc.process_name,
            "Departamento": getattr(calc, 'department', 'N/A'),
            "ROI %": f"{calc.roi_percentage_first_year:.2f}",
            "Payback (meses)": f"{calc.payback_period_months:.2f}",
            "Economia Anual": format_currency(calc.annual_savings),
            "Economia Mensal": format_currency(calc.monthly_savings),
            "Investimento": format_currency(calc.rpa_implementation_cost),
            "Automação %": f"{calc.expected_automation_percentage:.0f}",
        })
    
    df_export = pd.DataFrame(full_rankings)
    csv = df_export.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 Baixar Rankings (CSV)",
        data=csv,
        file_name="rankings_processos.csv",
        mime="text/csv"
    )

with export_col2:
    st.info("💡 Os dados acima incluem todos os processos ordenados por ROI")
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
