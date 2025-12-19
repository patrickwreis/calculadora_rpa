# -*- coding: utf-8 -*-
"""Reports page for RPA calculations analysis"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.database import DatabaseManager
from src.calculator.utils import format_currency, format_percentage


def load_data():
    """Load all calculations from database"""
    try:
        db_manager = DatabaseManager()
        return db_manager.get_all_calculations()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return []


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
        st.bar_chart(df.set_index("Departamento")["Qtd. Processos"])
    
    with col2:
        st.bar_chart(df.set_index("Departamento")["ROI Médio (%)"])


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
        st.metric("Investimento Total", format_currency(total_investment))
    
    with col2:
        total_monthly = df["Economia Mensal"].sum()
        st.metric("Economia Mensal Total", format_currency(total_monthly))
    
    with col3:
        total_annual = df["Economia Anual"].sum()
        st.metric("Economia Anual Total", format_currency(total_annual))


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
        st.metric("Payback Rápido (≤6m)", fast)
    with col2:
        st.metric("Payback Médio (6-12m)", medium)
    with col3:
        st.metric("Payback Longo (>12m)", long)


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


if __name__ == "__main__":
    main()
