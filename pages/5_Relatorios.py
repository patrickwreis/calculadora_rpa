# -*- coding: utf-8 -*-
"""Reports page for RPA calculations analysis with professional UI"""
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.calculator.utils import format_currency, format_percentage
from src.database import DatabaseManager
from src.export import ExportManager
from src.ui import EmptyStateManager


def load_data():
    """Load all calculations from database"""
    try:
        db_manager = DatabaseManager()
        success, calculations, error_msg = db_manager.get_all_calculations()
        if success:
            return calculations
        else:
            st.error(f"Erro ao carregar dados: {error_msg}")
            return []
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return []


def create_export_section(calculations):
    """Create section with PDF and Excel export buttons"""
    if not calculations:
        return
    
    st.divider()
    st.subheader("📥 Exportar Relatórios")
    
    # Convert calculations to dictionaries for export
    calc_dicts = [
        {
            'process_name': calc.process_name,
            'department': calc.department or '—',
            'complexity': calc.complexity or '—',
            'people_involved': calc.people_involved or 0,
            'systems_quantity': calc.systems_quantity or 0,
            'daily_transactions': calc.daily_transactions or 0,
            'hourly_rate': calc.hourly_rate or 0.0,
            'current_time_per_month': calc.current_time_per_month or 0.0,
            'rpa_implementation_cost': calc.rpa_implementation_cost or 0.0,
            'rpa_monthly_cost': calc.rpa_monthly_cost or 0.0,
            'maintenance_percentage': calc.maintenance_percentage or 0.0,
            'infra_license_cost': calc.infra_license_cost or 0.0,
            'other_costs': calc.other_costs or 0.0,
            'monthly_savings': calc.monthly_savings or 0.0,
            'annual_savings': calc.annual_savings or 0.0,
            'roi_first_year': calc.roi_first_year or 0.0,
            'roi_percentage_first_year': calc.roi_percentage_first_year or 0.0,
            'payback_period_months': calc.payback_period_months or 0.0,
        }
        for calc in calculations
    ]
    
    col1, col2, col3 = st.columns(3)
    
    # PDF Export
    with col1:
        with st.spinner("⏳ Gerando PDF..."):
            success, pdf_buffer, error_msg = ExportManager.export_to_pdf(calc_dicts)
        
        if success:
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_buffer,
                file_name=f"relatorio_roi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="pdf_export"
            )
        else:
            st.error(f"Erro ao gerar PDF: {error_msg}")
    
    # Excel Export
    with col2:
        with st.spinner("⏳ Gerando Excel..."):
            success, excel_buffer, error_msg = ExportManager.export_to_excel(calc_dicts)
        
        if success:
            st.download_button(
                label="📊 Baixar Excel",
                data=excel_buffer,
                file_name=f"relatorio_roi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="excel_export"
            )
        else:
            st.error(f"Erro ao gerar Excel: {error_msg}")
    
    # CSV Export
    with col3:
        df = pd.DataFrame([
            {
                "Processo": calc.process_name,
                "Departamento": calc.department or "N/A",
                "ROI Ano 1": calc.roi_percentage_first_year,
                "Payback (meses)": calc.payback_period_months,
                "Economia Anual": calc.annual_savings,
            }
            for calc in calculations
        ])
        
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📋 Baixar CSV",
            data=csv,
            file_name=f"relatorio_roi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="csv_export"
        )



def create_summary_report(calculations):
    """Create summary statistics report"""
    if not calculations:
        st.info("Nenhum processo cadastrado para gerar relatório.")
        return
    
    df = pd.DataFrame([
        {
            "Processo": calc.process_name,
            "Departamento": calc.department or "N/A",
            "ROI Ano 1": calc.roi_percentage_first_year,
            "Payback (meses)": calc.payback_period_months,
            "Economia Anual": calc.annual_savings,
            "Data Criação": calc.created_at.strftime("%d/%m/%Y") if calc.created_at else "N/A",
        }
        for calc in calculations
    ])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Processos",
            len(calculations),
            delta=None
        )
    
    with col2:
        avg_roi = df["ROI Ano 1"].mean()
        st.metric(
            "ROI Médio (Ano 1)",
            f"{format_percentage(avg_roi)}",
            delta=None
        )
    
    with col3:
        avg_payback = df["Payback (meses)"].mean()
        st.metric(
            "Payback Médio",
            f"{avg_payback:.1f} meses",
            delta=None
        )
    
    with col4:
        total_savings = df["Economia Anual"].sum()
        st.metric(
            "Economia Anual Total",
            format_currency(total_savings),
            delta=None
        )
    
    st.subheader("Detalhes dos Processos")
    st.dataframe(df, width='stretch', hide_index=True)
    
    # Export button
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Baixar Relatório (CSV)",
        data=csv,
        file_name=f"relatorio_processos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def create_department_report(calculations):
    """Create departmental analysis report"""
    if not calculations:
        return
    
    departments = {}
    for calc in calculations:
        dept = calc.department or "Não Especificado"
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(calc)
    
    dept_data = []
    for dept, calcs in sorted(departments.items()):
        dept_data.append({
            "Departamento": dept,
            "Qtd. Processos": len(calcs),
            "ROI Médio (%)": sum(c.roi_percentage_first_year for c in calcs) / len(calcs),
            "Economia Anual": sum(c.annual_savings for c in calcs),
            "Payback Médio": sum(c.payback_period_months for c in calcs) / len(calcs),
        })
    
    df = pd.DataFrame(dept_data)
    df = df.sort_values("Economia Anual", ascending=False)
    
    st.dataframe(df, width='stretch', hide_index=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_dept_qty = px.bar(
            df,
            x="Departamento",
            y="Qtd. Processos",
            title="Quantidade de Processos por Departamento",
            color="Qtd. Processos",
            color_continuous_scale="Blues",
            height=400
        )
        st.plotly_chart(fig_dept_qty)
    
    with col2:
        fig_dept_roi = px.bar(
            df,
            x="Departamento",
            y="ROI Médio (%)",
            title="ROI Médio por Departamento (%)",
            color="ROI Médio (%)",
            color_continuous_scale="Viridis",
            height=400
        )
        st.plotly_chart(fig_dept_roi)


def create_financial_report(calculations):
    """Create financial analysis report"""
    if not calculations:
        return
    
    financial_data = []
    for calc in calculations:
        financial_data.append({
            "Processo": calc.process_name,
            "Investimento Inicial": calc.rpa_implementation_cost,
            "Custo Mensal": calc.rpa_monthly_cost,
            "Economia Mensal": calc.monthly_savings,
            "Margem (Mês)": calc.monthly_savings - calc.rpa_monthly_cost,
            "Economia Anual": calc.annual_savings,
            "Payback (meses)": calc.payback_period_months,
        })
    
    df = pd.DataFrame(financial_data)
    df = df.sort_values("Economia Anual", ascending=False)
    
    st.dataframe(df, width='stretch', hide_index=True)
    
    # Financial summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_investment = df["Investimento Inicial"].sum()
        st.metric("💻 Investimento Total", format_currency(total_investment))
    
    with col2:
        total_monthly = df["Economia Mensal"].sum()
        st.metric("📅 Economia Mensal Total", format_currency(total_monthly))
    
    with col3:
        total_annual = df["Economia Anual"].sum()
        st.metric("📊 Economia Anual Total", format_currency(total_annual))
    
    st.divider()
    
    # Financial visualizations
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Top processes by savings
        top_df = df.nlargest(8, "Economia Anual")
        fig_econ = px.bar(
            top_df,
            x="Processo",
            y="Economia Anual",
            title="Top 8 Processos - Economia Anual",
            color="Economia Anual",
            color_continuous_scale="Greens",
            height=400
        )
        fig_econ.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig_econ)
    
    with chart_col2:
        # Investment vs Savings scatter
        fig_invest_scatter = px.scatter(
            df.nlargest(10, "Economia Anual"),
            x="Investimento Inicial",
            y="Economia Anual",
            size="Economia Mensal",
            hover_name="Processo",
            title="Investimento vs Economia (Top 10)",
            color_discrete_sequence=["#2ca02c"],
            height=400
        )
        st.plotly_chart(fig_invest_scatter)


def create_timeline_report(calculations):
    """Create payback timeline report"""
    if not calculations:
        return
    
    # Sort by payback period
    sorted_calcs = sorted(calculations, key=lambda x: x.payback_period_months)
    
    timeline_data = []
    for calc in sorted_calcs:
        timeline_data.append({
            "Processo": calc.process_name,
            "Payback (meses)": calc.payback_period_months,
            "Status": "✅ Rápido" if calc.payback_period_months <= 6 
                     else "⏳ Médio" if calc.payback_period_months <= 12 
                     else "⏸️ Longo",
        })
    
    df = pd.DataFrame(timeline_data)
    st.dataframe(df, width='stretch', hide_index=True)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    fast = len([c for c in sorted_calcs if c.payback_period_months <= 6])
    medium = len([c for c in sorted_calcs if 6 < c.payback_period_months <= 12])
    long = len([c for c in sorted_calcs if c.payback_period_months > 12])
    
    with col1:
        st.metric("⚡ Payback Rápido (≤6m)", fast)
    with col2:
        st.metric("🔄 Payback Médio (6-12m)", medium)
    with col3:
        st.metric("🐢 Payback Longo (>12m)", long)
    
    st.divider()
    
    # Timeline visualization
    fig_timeline = px.bar(
        df,
        x="Processo",
        y="Payback (meses)",
        color="Status",
        title="Timeline de Payback - Todos os Processos",
        color_discrete_map={
            "✅ Rápido": "#2ca02c",
            "⏳ Médio": "#ff7f0e",
            "⏸️ Longo": "#d62728"
        },
        height=400
    )
    fig_timeline.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
    st.plotly_chart(fig_timeline)


def main():
    """Main function"""
    st.set_page_config(
        page_title="Relatórios",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Relatórios")
    st.markdown("Análise completa dos processos RPA cadastrados")
    
    # Load data
    calculations = load_data()
    
    if not calculations:
        st.info("Nenhum processo cadastrado. Acesse 'Novo Processo' para começar.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Resumo", "🏢 Departamentos", "💰 Financeiro", "⏱️ Timeline"]
    )
    
    with tab1:
        st.subheader("Resumo Executivo")
        create_summary_report(calculations)
    
    with tab2:
        st.subheader("Análise por Departamento")
        create_department_report(calculations)
    
    with tab3:
        st.subheader("Análise Financeira")
        create_financial_report(calculations)
    
    with tab4:
        st.subheader("Timeline de Payback")
        create_timeline_report(calculations)
    
    # Export section
    create_export_section(calculations)


if __name__ == "__main__":
    main()
