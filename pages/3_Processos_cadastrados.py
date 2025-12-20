# -*- coding: utf-8 -*-
"""Process Management - Simplified Single Page"""
from datetime import datetime

import pandas as pd
import streamlit as st

from config import APP_NAME
from src.calculator.utils import format_currency, format_percentage, format_months
from src.database import DatabaseManager
from src.ui.components import page_header

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Processos",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database
db_manager = DatabaseManager()

# Page header
page_header("Histórico de Processos", "Visualize, edite e gerencie todos os seus cálculos de ROI")

# Get calculations
calculations = db_manager.get_all_calculations()

if not calculations:
    st.info("📋 Nenhum processo salvo ainda. Comece criando um novo cálculo!")
    st.stop()

# ========== SELECTION SECTION ==========
st.markdown("### 🎯 Selecione um Processo")

selected_process_id = st.selectbox(
    "Escolha um processo para visualizar e editar:",
    [calc.id for calc in calculations],
    format_func=lambda x: f"ID {x} - {next(c.process_name for c in calculations if c.id == x)}",
    key="main_selectbox"
)

selected_calc = next(c for c in calculations if c.id == selected_process_id)

st.divider()

# ========== DETAILS SECTION ==========
st.markdown(f"### 📋 Detalhes: {selected_calc.process_name}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("ROI 1º Ano", f"{selected_calc.roi_percentage_first_year:.1f}%")

with col2:
    st.metric("Payback", format_months(selected_calc.payback_period_months))

with col3:
    st.metric("Economia Anual", format_currency(selected_calc.annual_savings))

with col4:
    st.metric("Economia Mensal", format_currency(selected_calc.monthly_savings))

# Expandable details
with st.expander("📌 Informações Completas", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Informações do Processo**")
        st.write(f"• Horas/Mês: {selected_calc.current_time_per_month}")
        st.write(f"• Pessoas: {selected_calc.people_involved}")
        st.write(f"• Taxa Horária: {format_currency(selected_calc.hourly_rate)}")
        st.write(f"• Automação: {selected_calc.expected_automation_percentage:.1f}%")
        st.write(f"• Departamento: {getattr(selected_calc, 'department', 'N/A')}")
    
    with col2:
        st.write("**Características**")
        st.write(f"• Complexidade: {getattr(selected_calc, 'complexity', 'N/A')}")
        st.write(f"• Sistemas: {getattr(selected_calc, 'systems_quantity', 'N/A')}")
        st.write(f"• Transações/Dia: {getattr(selected_calc, 'daily_transactions', 'N/A')}")
        st.write(f"• Taxa Erro: {getattr(selected_calc, 'error_rate', 0):.0f}%")
        st.write(f"• Taxa Exceção: {getattr(selected_calc, 'exception_rate', 0):.0f}%")
    
    with col3:
        st.write("**Custos RPA**")
        st.write(f"• Implementação: {format_currency(selected_calc.rpa_implementation_cost)}")
        st.write(f"• Mensal: {format_currency(selected_calc.rpa_monthly_cost)}")
        st.write(f"• Multas Evitadas: {format_currency(getattr(selected_calc, 'fines_avoided', 0))}")
        st.write(f"• SLA Reduzida: {format_currency(getattr(selected_calc, 'sql_savings', 0))}")
        st.write(f"• Criado: {selected_calc.created_at.strftime('%d/%m/%Y %H:%M')}")

st.divider()

# ========== ACTION BUTTONS ==========
st.markdown("### ⚙️ Ações")

col1, col2, col3, col4 = st.columns([1, 1, 2, 2])

with col1:
    if st.button("✏️ Editar", type="primary", width='stretch'):
        st.session_state.edit_modal = True

with col2:
    if st.button("🗑️ Excluir", type="secondary", width='stretch'):
        st.session_state.delete_modal = True

# ========== EDIT MODAL ==========
@st.dialog("Editar Processo", width="large")
def edit_process_modal():
    st.markdown(f"**Editando:** {selected_calc.process_name}")
    st.divider()
    
    with st.form("edit_form"):
        # Informações Básicas
        st.markdown("### 📋 Informações Básicas")
        col1, col2 = st.columns(2)
        
        with col1:
            process_name = st.text_input(
                "Nome do Processo",
                value=selected_calc.process_name,
            )
        
        with col2:
            department = st.text_input(
                "Área / Departamento",
                value=getattr(selected_calc, 'department', ''),
            )
        
        # Características do Processo
        st.markdown("### 🔧 Características do Processo")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            people = st.number_input(
                "Pessoas Envolvidas",
                value=int(selected_calc.people_involved),
                min_value=1,
                step=1
            )
        
        with col2:
            current_time = st.number_input(
                "Tempo Atual (horas/mês)",
                value=float(selected_calc.current_time_per_month),
                min_value=0.0,
                step=0.5
            )
        
        with col3:
            hourly_rate = st.number_input(
                "Taxa Horária (R$)",
                value=float(selected_calc.hourly_rate),
                min_value=0.0,
                step=1.0,
                format="%.2f"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            complexity = st.selectbox(
                "Complexidade",
                ["Baixa", "Média", "Alta"],
                index=["Baixa", "Média", "Alta"].index(getattr(selected_calc, 'complexity', 'Média'))
            )
        
        with col2:
            systems_quantity = st.number_input(
                "Quantidade de Sistemas",
                value=int(getattr(selected_calc, 'systems_quantity', 1)),
                min_value=1,
                step=1
            )
        
        with col3:
            daily_transactions = st.number_input(
                "Volume de Transações/Dia",
                value=int(getattr(selected_calc, 'daily_transactions', 100)),
                min_value=1,
                step=10
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            error_rate = st.number_input(
                "Taxa de Erro (%)",
                value=float(getattr(selected_calc, 'error_rate', 0)),
                min_value=0,
                max_value=100,
                step=1
            )
        
        with col2:
            exception_rate = st.number_input(
                "Taxa de Exceção (%)",
                value=float(getattr(selected_calc, 'exception_rate', 0)),
                min_value=0,
                max_value=100,
                step=1
            )
        
        # Automação
        st.markdown("### ⚙️ Automação")
        automation_pct = st.number_input(
            "Automação Esperada (%)",
            value=float(selected_calc.expected_automation_percentage),
            min_value=0.0,
            max_value=100.0,
            step=1.0
        )
        
        # Custos de Implementação
        st.markdown("### 💰 Custos de Implementação")
        col1, col2 = st.columns(2)
        
        with col1:
            impl_cost = st.number_input(
                "Custo de Implementação (R$)",
                value=float(selected_calc.rpa_implementation_cost),
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
        
        with col2:
            maintenance_percentage = st.number_input(
                "Manutenção Anual (% do desenvolvimento)",
                value=float(getattr(selected_calc, 'maintenance_percentage', 10)),
                min_value=0,
                max_value=100,
                step=1
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            infra_license_cost = st.number_input(
                "Custo com Infra/Licenças (R$ mensal)",
                value=float(getattr(selected_calc, 'infra_license_cost', 0)),
                min_value=0.0,
                step=10.0,
                format="%.2f"
            )
        
        with col2:
            other_costs = st.number_input(
                "Outros Custos (R$ - uma vez)",
                value=float(getattr(selected_calc, 'other_costs', 0)),
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
        
        monthly_cost = (impl_cost * maintenance_percentage) / 100 / 12
        monthly_rpa_cost = monthly_cost + infra_license_cost
        
        # Benefícios Adicionais
        st.markdown("### 🎁 Benefícios Adicionais")
        col1, col2 = st.columns(2)
        
        with col1:
            fines_avoided = st.number_input(
                "Multas Evitadas (R$ mensal)",
                value=float(getattr(selected_calc, 'fines_avoided', 0)),
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
        
        with col2:
            sql_savings = st.number_input(
                "SLA Reduzida (R$ mensal)",
                value=float(getattr(selected_calc, 'sql_savings', 0)),
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
        
        st.divider()
        
        # Botões
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.form_submit_button("💾 Salvar", type="primary", width='stretch'):
                # Recalculate savings including additional benefits
                base_savings = (current_time * people * hourly_rate * automation_pct / 100)
                monthly_savings = base_savings + fines_avoided + sql_savings
                annual_savings = monthly_savings * 12
                
                update_data = {
                    # Basic Information
                    "process_name": process_name,
                    "department": department,
                    
                    # Process Characteristics
                    "people_involved": int(people),
                    "current_time_per_month": float(current_time),
                    "hourly_rate": float(hourly_rate),
                    "complexity": complexity,
                    "systems_quantity": int(systems_quantity),
                    "daily_transactions": int(daily_transactions),
                    "error_rate": float(error_rate),
                    "exception_rate": float(exception_rate),
                    
                    # Automation Settings
                    "expected_automation_percentage": float(automation_pct),
                    
                    # Implementation Costs
                    "rpa_implementation_cost": float(impl_cost),
                    "maintenance_percentage": float(maintenance_percentage),
                    "infra_license_cost": float(infra_license_cost),
                    "other_costs": float(other_costs),
                    "rpa_monthly_cost": float(monthly_rpa_cost),
                    
                    # Additional Benefits
                    "fines_avoided": float(fines_avoided),
                    "sql_savings": float(sql_savings),
                    
                    # Calculated Results
                    "monthly_savings": monthly_savings,
                    "annual_savings": annual_savings,
                    "payback_period_months": impl_cost / monthly_savings if monthly_savings > 0 else 0,
                    "roi_first_year": (annual_savings - impl_cost),
                    "roi_percentage_first_year": ((annual_savings - impl_cost) / impl_cost * 100) if impl_cost > 0 else 0,
                    
                    # Timestamp
                    "updated_at": datetime.utcnow(),
                }
                
                db_manager.update_calculation(selected_id, update_data)
                st.success("✅ Processo atualizado com sucesso!")
                st.session_state.edit_modal = False
                st.sleep(0.5)
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancelar", width='stretch'):
                st.session_state.edit_modal = False
                st.rerun()

# ========== DELETE CONFIRMATION MODAL ==========
@st.dialog("Confirmar Exclusão", width="small")
def delete_confirmation_modal():
    st.warning(f"⚠️ Você está prestes a excluir o processo: **{selected_calc.process_name}**")
    st.write("Esta ação é **irreversível** e não pode ser desfeita.")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Sim, Excluir", type="secondary", width='stretch', key="confirm_delete"):
            if db_manager.delete_calculation(selected_id):
                st.success("✅ Processo excluído com sucesso!")
                st.session_state.delete_modal = False
                st.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Erro ao excluir o processo")
    
    with col2:
        if st.button("❌ Cancelar", width='stretch', key="cancel_delete"):
            st.session_state.delete_modal = False
            st.rerun()

# ========== TRIGGER MODALS ==========
if st.session_state.get("edit_modal", False):
    edit_process_modal()

if st.session_state.get("delete_modal", False):
    delete_confirmation_modal()
