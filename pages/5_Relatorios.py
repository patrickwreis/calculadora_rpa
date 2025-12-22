# -*- coding: utf-8 -*-
"""Reports page for RPA calculations analysis with professional UI"""
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.calculator.utils import format_currency, format_percentage, calculate_automation_metrics
from src.database import DatabaseManager
from src.export import ExportManager
from src.ui import EmptyStateManager
from src.ui.auth import require_auth
from src.ui.auth_components import render_logout_button
from src.security import SessionManager

# Auth gate - ensure session is restored before any checks
SessionManager.ensure_auth(redirect_page="streamlit_app.py")

# Auth gate
if not require_auth(form_key="relatorios_login"):
    st.stop()

# Header com logout
render_logout_button("relatorios")


def compute_efficiency(calc):
    """Return freed hours/month and freed FTE based on automation and exceptions."""
    metrics = calculate_automation_metrics(
        expected_automation_percentage=calc.expected_automation_percentage,
        exception_rate=getattr(calc, "exception_rate", 0.0),
    )
    freed_hours = (calc.current_time_per_month or 0.0) * (metrics["fully_automated_pct"] / 100.0)
    freed_fte = freed_hours / 220 if freed_hours else 0.0
    return freed_hours, freed_fte


def load_data(user_id=None):
    """Load calculations from database
    
    Args:
        user_id: If provided, filter by user_id. None returns all calculations.
    """
    try:
        db_manager = DatabaseManager()
        success, calculations, error_msg = db_manager.get_all_calculations(user_id=user_id)
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
    calc_dicts = []
    for calc in calculations:
        freed_hours, freed_fte = compute_efficiency(calc)
        calc_dicts.append({
            'process_name': calc.process_name,
            'department': calc.department or '—',
            'complexity': calc.complexity or '—',
            'people_involved': calc.people_involved or 0,
            'systems_quantity': calc.systems_quantity or 0,
            'daily_transactions': calc.daily_transactions or 0,
            'hourly_rate': calc.hourly_rate or 0.0,
            'current_time_per_month': calc.current_time_per_month or 0.0,
            'freed_hours_per_month': freed_hours,
            'freed_fte': freed_fte,
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
        })
    
    col1, col2, col3 = st.columns(3)
    
    # PDF Export
    with col1:
        with st.spinner("⏳ Gerando PDF..."):
            success, pdf_buffer, error_msg = ExportManager.export_to_pdf(calc_dicts)
        
        if success and pdf_buffer is not None:
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
        
        if success and excel_buffer is not None:
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
                "Horas Liberadas/mês": compute_efficiency(calc)[0],
                "FTE Liberado": compute_efficiency(calc)[1],
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
    
    data_list = []
    for calc in calculations:
        freed_hours, freed_fte = compute_efficiency(calc)
        data_list.append({
            "Processo": calc.process_name,
            "Departamento": calc.department or "N/A",
            "Horas Liberadas/mês": freed_hours,
            "FTE Liberado": freed_fte,
            "ROI Ano 1": calc.roi_percentage_first_year,
            "Payback (meses)": calc.payback_period_months,
            "Economia Anual": calc.annual_savings,
            "Data Criação": calc.created_at.strftime("%d/%m/%Y") if calc.created_at else "N/A",
        })
    
    df = pd.DataFrame(data_list)
    
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
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "Processo": st.column_config.TextColumn(width="large"),
            "Departamento": st.column_config.TextColumn(width="medium"),
            "Horas Liberadas/mês": st.column_config.NumberColumn(format="%.1f", width="small"),
            "FTE Liberado": st.column_config.NumberColumn(format="%.2f", width="small"),
            "ROI Ano 1": st.column_config.NumberColumn(format="%.1f%%", width="small"),
            "Payback (meses)": st.column_config.NumberColumn(format="%.1f", width="small"),
            "Economia Anual": st.column_config.NumberColumn(format="R$ %.2f", width="medium"),
            "Data Criação": st.column_config.TextColumn(width="medium"),
        }
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
        total_freed_hours = sum(compute_efficiency(c)[0] for c in calcs)
        total_freed_fte = sum(compute_efficiency(c)[1] for c in calcs)
        dept_data.append({
            "Departamento": dept,
            "Qtd. Processos": len(calcs),
            "Horas Liberadas/mês": total_freed_hours,
            "FTE Liberado": total_freed_fte,
            "ROI Médio (%)": sum(c.roi_percentage_first_year for c in calcs) / len(calcs),
            "Economia Anual": sum(c.annual_savings for c in calcs),
            "Payback Médio": sum(c.payback_period_months for c in calcs) / len(calcs),
        })
    
    df = pd.DataFrame(dept_data)
    df = df.sort_values("Economia Anual", ascending=False)
    
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "Departamento": st.column_config.TextColumn(width="large"),
            "Qtd. Processos": st.column_config.NumberColumn(width="small"),
            "Horas Liberadas/mês": st.column_config.NumberColumn(format="%.1f", width="small"),
            "FTE Liberado": st.column_config.NumberColumn(format="%.2f", width="small"),
            "ROI Médio (%)": st.column_config.NumberColumn(format="%.1f%%", width="medium"),
            "Economia Anual": st.column_config.NumberColumn(format="R$ %.2f", width="medium"),
            "Payback Médio": st.column_config.NumberColumn(format="%.1f", width="small"),
        }
    )
    
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
        freed_hours, freed_fte = compute_efficiency(calc)
        financial_data.append({
            "Processo": calc.process_name,
            "Horas Liberadas/mês": freed_hours,
            "FTE Liberado": freed_fte,
            "Investimento Inicial": calc.rpa_implementation_cost,
            "Custo Mensal": calc.rpa_monthly_cost,
            "Economia Mensal": calc.monthly_savings,
            "Margem (Mês)": calc.monthly_savings - calc.rpa_monthly_cost,
            "Economia Anual": calc.annual_savings,
            "Payback (meses)": calc.payback_period_months,
        })
    
    df = pd.DataFrame(financial_data)
    df = df.sort_values("Economia Anual", ascending=False)
    
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "Processo": st.column_config.TextColumn(width="large"),
            "Horas Liberadas/mês": st.column_config.NumberColumn(format="%.1f", width="small"),
            "FTE Liberado": st.column_config.NumberColumn(format="%.2f", width="small"),
            "Investimento Inicial": st.column_config.NumberColumn(format="R$ %.2f", width="medium"),
            "Custo Mensal": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Economia Mensal": st.column_config.NumberColumn(format="R$ %.2f", width="medium"),
            "Margem (Mês)": st.column_config.NumberColumn(format="R$ %.2f", width="medium"),
            "Economia Anual": st.column_config.NumberColumn(format="R$ %.2f", width="medium"),
            "Payback (meses)": st.column_config.NumberColumn(format="%.1f", width="small"),
        }
    )
    
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
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "Processo": st.column_config.TextColumn(width="large"),
            "Payback (meses)": st.column_config.NumberColumn(format="%.1f", width="medium"),
            "Status": st.column_config.TextColumn(width="medium"),
        }
    )
    
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
    
    # Get current user for filtering
    current_user_id = st.session_state.get("auth_user_id", 1)
    is_admin = st.session_state.get("auth_is_admin", False)
    user_filter = None if is_admin else current_user_id
    
    if is_admin and user_filter is None:
        st.markdown("Análise completa de **todos os processos RPA** cadastrados (Admin)")
    else:
        st.markdown("Análise completa dos **seus processos RPA** cadastrados")
    
    # Load data
    calculations = load_data(user_id=user_filter)
    
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
