# -*- coding: utf-8 -*-
"""Main Calculator Page - Based on Verzel Calculator"""
import streamlit as st
from src.calculator import ROICalculator, ROIInput
from src.calculator.utils import format_currency, format_percentage, format_months, validate_input
from src.ui.components import page_header
from src.database import DatabaseManager
from config import APP_NAME, APP_DESCRIPTION
import datetime

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Calculadora",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)




# Initialize session state
if "calculator_results" not in st.session_state:
    st.session_state.calculator_results = None

if "show_results" not in st.session_state:
    st.session_state.show_results = False

# Initialize components
calculator = ROICalculator()
db_manager = DatabaseManager()

# Page header
st.title("Calculadora de Economia RPA")
st.markdown("Analise a viabilidade e calcule o ROI da implementação de RPA na sua empresa")

st.divider()

# Main form container
st.subheader("Dados do Processo")
st.markdown("Informe os dados atuais do processo que será automatizado para calcular a viabilidade do RPA")

# Create form with all inputs
with st.form("roi_form"):
    
    # Basic Information Section
    st.markdown("### Informações Básicas")
    
    col1, col2 = st.columns(2)
    with col1:
        process_name = st.text_input(
            "Nome do Processo *",
            placeholder="Ex: Processamento de Facturas",
            help="Identificar claramente o processo a ser automatizado"
        )
    
    with col2:
        department = st.text_input(
            "Área / Departamento *",
            placeholder="Ex: Financeiro",
            help="Departamento ou área responsável pelo processo"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        people_involved = st.number_input(
            "Número de funcionários *",
            min_value=1,
            max_value=100,
            value=5,
            step=1,
            help="Quantas pessoas executam esse processo atualmente?"
        )
    
    with col2:
        days_per_month = st.number_input(
            "Dias trabalhados no mês *",
            min_value=1,
            max_value=31,
            value=22,
            step=1,
            help="Quantos dias por mês o processo é executado?"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        monthly_salary = st.number_input(
            "Custo médio por funcionário (R$) *",
            min_value=1000.0,
            max_value=100000.0,
            value=5000.0,
            step=100.0,
            help="Salário + encargos + benefícios (mensal)"
        )
    
    with col2:
        minutes_per_day = st.number_input(
            "Tempo gasto por dia (minutos) *",
            min_value=5,
            max_value=480,
            value=60,
            step=5,
            help="Quantos minutos cada funcionário dedica ao processo? (ex: 480 = 8 horas)"
        )
        # Convert minutes to hours
        hours_per_day = minutes_per_day / 60
    
    # Calculate hourly rate from monthly salary
    working_hours_per_month = days_per_month * 8  # Dinâmico baseado na entrada do usuário
    hourly_rate = monthly_salary / working_hours_per_month
    current_time_per_month = hours_per_day * days_per_month
    
    # Process Characteristics Section
    st.markdown("### Características do Processo")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        complexity = st.selectbox(
            "Complexidade da Automação *",
            options=["Baixa", "Média", "Alta"],
            help="Avalie a complexidade técnica do processo"
        )
        
        # Map complexity to automation percentage range
        complexity_map = {
            "Baixa": 0.85,
            "Média": 0.70,
            "Alta": 0.50
        }
        default_automation = complexity_map.get(complexity, 0.70)
    
    with col2:
        systems_quantity = st.number_input(
            "Quantidade de sistemas *",
            min_value=1,
            max_value=50,
            value=2,
            step=1,
            help="Quantos sistemas estão envolvidos neste processo?"
        )
    
    with col3:
        daily_transactions = st.number_input(
            "Volume de transações por dia *",
            min_value=1,
            max_value=10000,
            value=100,
            step=10,
            help="Quantas transações/tarefas são processadas diariamente?"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        error_rate = st.number_input(
            "Taxa de erro atual (%)",
            min_value=0,
            max_value=100,
            value=5,
            step=1,
            help="Qual a porcentagem de erros no processo manual?"
        )
    
    with col2:
        exception_rate = st.number_input(
            "Taxa de exceção (%)",
            min_value=0,
            max_value=100,
            value=10,
            step=1,
            help="Porcentagem que precisa de análise manual (Ex: de 100% transações, 10% precisa de análise)"
        )
    
    # Implementation Section - Development Costs
    st.markdown("### Custos de Implementação")
    
    st.markdown("#### Custos de Desenvolvimento")
    
    col1, col2 = st.columns(2)
    with col1:
        dev_hours = st.number_input(
            "Horas de desenvolvimento estimada *",
            min_value=1.0,
            max_value=10000.0,
            value=160.0,
            step=1.0,
            help="Horas totais estimadas para desenvolvimento e implantação"
        )
    
    with col2:
        dev_hourly_rate = st.number_input(
            "Valor hora médio desenvolvimento (R$) *",
            min_value=10.0,
            max_value=500.0,
            value=150.0,
            step=10.0,
            help="Valor médio hora de desenvolvimento"
        )
    
    # Calculate development cost
    dev_total_cost = dev_hours * dev_hourly_rate
    
    st.markdown("#### Custos Operacionais")
    
    col1, col2 = st.columns(2)
    with col1:
        # Maintenance cost as percentage of dev cost
        maintenance_percentage = st.number_input(
            "Percentual anual de manutenção (% do desenvolvimento)",
            min_value=0,
            max_value=100,
            value=10,
            step=1,
            help="Percentual ANUAL do custo de desenvolvimento destinado à manutenção. Será convertido para custo mensal automaticamente (ex: 12% anual => 1% ao mês)."
        )
        # The maintenance percentage is provided as a percentage of the development cost (annual %).
        # Convert to a monthly cost by dividing the annual amount by 12.
        monthly_cost = (dev_total_cost * maintenance_percentage) / 100 / 12
    
    with col2:
        # Additional infrastructure and license costs
        infra_license_cost = st.number_input(
            "Custo com infra, licenças e outros (R$) - Mensal",
            min_value=0.0,
            max_value=100000.0,
            value=500.0,
            step=100.0,
            help="Custos mensais com infraestrutura, licenças de software, etc"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        other_costs = st.number_input(
            "Outros custos (R$) - Uma vez",
            min_value=0.0,
            max_value=100000.0,
            value=0.0,
            step=100.0,
            help="Outros custos únicos de implementação"
        )
    
    with col2:
        st.empty()
    
    # Calculate total implementation cost
    impl_cost = dev_total_cost + other_costs
    total_monthly_cost = monthly_cost + infra_license_cost
    
    # Calculate automation percentage based on exception rate
    # If 10% needs manual review, 90% can be automated
    automation_pct = 100 - exception_rate
    
    # Additional Benefits Section
    st.markdown("### Outros Benefícios")
    
    col1, col2 = st.columns(2)
    with col1:
        fines_avoided = st.number_input(
            "Multas Evitadas (R$) - Mensal",
            min_value=0.0,
            max_value=1000000.0,
            value=0.0,
            step=100.0,
            help="Multas que serão evitadas com a automação (valor mensal)"
        )
    
    with col2:
        sql_savings = st.number_input(
            "SLA Reduzida (R$) - Mensal",
            min_value=0.0,
            max_value=1000000.0,
            value=0.0,
            step=100.0,
            help="Economia com melhoria de SLA (valor mensal)"
        )
    
    # Button row
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        calculate_btn = st.form_submit_button("Calcular Economia RPA", width="stretch", type="primary")
    
    with col2:
        clear_btn = st.form_submit_button("Limpar Dados", width="content")
    
    # Handle clear button
    if clear_btn:
        st.session_state.show_results = False
        st.session_state.calculator_results = None
        st.rerun()
    
    # Handle calculate button
    if calculate_btn:
        # Validate inputs
        if not process_name.strip():
            st.error("❌ Por favor, insira o nome do processo")
        elif not department.strip():
            st.error("❌ Por favor, insira a área/departamento")
        else:
            # Create input object and calculate
            input_dict = {
                "process_name": process_name,
                "current_time_per_month": current_time_per_month,
                "people_involved": people_involved,
                "hourly_rate": hourly_rate,
                "rpa_implementation_cost": impl_cost,
                "rpa_monthly_cost": total_monthly_cost,
                "expected_automation_percentage": automation_pct,
            }
            
            is_valid, error_msg = validate_input(input_dict)
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                roi_input = ROIInput(**input_dict)
                result = calculator.calculate(roi_input)
                
                # Store in session state with additional data
                st.session_state.calculator_results = {
                    "input": roi_input,
                    "result": result,
                    "timestamp": datetime.datetime.now(),
                    "department": department,
                    "complexity": complexity,
                    "systems_quantity": systems_quantity,
                    "daily_transactions": daily_transactions,
                    "error_rate": error_rate,
                    "exception_rate": exception_rate,
                    "fines_avoided": fines_avoided,
                    "sql_savings": sql_savings,
                    "dev_hours": dev_hours,
                    "dev_hourly_rate": dev_hourly_rate,
                    "dev_total_cost": dev_total_cost,
                    "other_costs": other_costs,
                    "monthly_cost": monthly_cost,
                    "infra_license_cost": infra_license_cost,
                    "total_monthly_cost": total_monthly_cost,
                    "maintenance_percentage": maintenance_percentage,
                }
                
                st.session_state.show_results = True
                st.rerun()

# Display results if calculated
if st.session_state.show_results and st.session_state.calculator_results:
    st.divider()
    
    # Results header with styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;
                color: white;">
        <h2 style="margin: 0; color: white; text-align: center;">✓ Análise de ROI Concluída</h2>
    </div>
    """, unsafe_allow_html=True)
    
    result = st.session_state.calculator_results["result"]
    roi_input = st.session_state.calculator_results["input"]
    fines_avoided = st.session_state.calculator_results.get("fines_avoided", 0)
    sql_savings = st.session_state.calculator_results.get("sql_savings", 0)
    
    # Calculate totals with additional benefits
    total_monthly_savings = result.monthly_savings + fines_avoided + sql_savings
    
    # Calculate ROI and Economia for 1, 2, and 5 years
    roi_1year = ((total_monthly_savings * 12 - roi_input.rpa_implementation_cost) / roi_input.rpa_implementation_cost * 100)
    roi_2years = ((total_monthly_savings * 24 - roi_input.rpa_implementation_cost) / roi_input.rpa_implementation_cost * 100)
    roi_5years = ((total_monthly_savings * 60 - roi_input.rpa_implementation_cost) / roi_input.rpa_implementation_cost * 100)
    
    economia_1year = total_monthly_savings * 12 - roi_input.rpa_implementation_cost
    economia_2years = total_monthly_savings * 24 - roi_input.rpa_implementation_cost
    economia_5years = total_monthly_savings * 60 - roi_input.rpa_implementation_cost
    
    # Dashboard Container
    st.markdown("""
    <style>
    .dashboard-container {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 2px solid #E2E8F0;
    }
    .dashboard-title {
        text-align: center;
        color: #1F2937;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 30px;
    }
    .dashboard-section {
        margin-top: 0;
        padding-top: 0;
        border-top: none;
    }
    .kpi-card {
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        color: white;
        font-weight: bold;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-label {
        font-size: 11px;
        opacity: 0.92;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 28px;
        margin: 8px 0;
        font-weight: 900;
    }
    .kpi-indicator {
        font-size: 24px;
        margin-top: 5px;
    }
    .kpi-green { background: linear-gradient(135deg, #10B981 0%, #059669 100%); }
    .kpi-blue { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); }
    .kpi-red { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); }
    .kpi-purple { background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%); }
    .kpi-orange { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); }
    .kpi-cyan { background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%); }
    .kpi-pink { background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%); }
    .section-title {
        color: #1F2937;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        padding-left: 12px;
        border-left: 4px solid #3B82F6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Start Dashboard
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="dashboard-title">📊 Dashboard de ROI - {roi_input.process_name}</div>', unsafe_allow_html=True)
    
    # KPIs Section
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader("Economia (Benefício Financeiro)")
        eco_col1, eco_col2, eco_col3 = st.columns(3, gap="small")
        
        with eco_col1:
            eco_indicator = "✅" if economia_1year > 0 else "⚠️"
            st.markdown(f"""
            <div class="kpi-card kpi-blue">
                <div class="kpi-label">1 Ano</div>
                <div class="kpi-value">{format_currency(economia_1year)}</div>
                <div class="kpi-indicator">{eco_indicator}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with eco_col2:
            eco2_indicator = "✅" if economia_2years > 0 else "⚠️"
            st.markdown(f"""
            <div class="kpi-card kpi-green">
                <div class="kpi-label">2 Anos</div>
                <div class="kpi-value">{format_currency(economia_2years)}</div>
                <div class="kpi-indicator">{eco2_indicator}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with eco_col3:
            eco5_indicator = "✅" if economia_5years > 0 else "⚠️"
            st.markdown(f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-label">5 Anos</div>
                <div class="kpi-value">{format_currency(economia_5years)}</div>
                <div class="kpi-indicator">{eco5_indicator}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Retorno sobre Investimento (ROI %)")
        roi_col1, roi_col2, roi_col3 = st.columns(3, gap="small")
        
        with roi_col1:
            roi_color_1 = "kpi-green" if roi_1year > 0 else "kpi-red"
            roi_indicator_1 = "✅" if roi_1year > 100 else "⚠️" if roi_1year > 0 else "❌"
            st.markdown(f"""
            <div class="kpi-card {roi_color_1}">
                <div class="kpi-label">1 Ano</div>
                <div class="kpi-value">{roi_1year:.1f}%</div>
                <div class="kpi-indicator">{roi_indicator_1}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with roi_col2:
            roi_color_2 = "kpi-green" if roi_2years > 0 else "kpi-red"
            roi_indicator_2 = "✅" if roi_2years > 100 else "⚠️" if roi_2years > 0 else "❌"
            st.markdown(f"""
            <div class="kpi-card {roi_color_2}">
                <div class="kpi-label">2 Anos</div>
                <div class="kpi-value">{roi_2years:.1f}%</div>
                <div class="kpi-indicator">{roi_indicator_2}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with roi_col3:
            roi_color_5 = "kpi-green" if roi_5years > 0 else "kpi-red"
            roi_indicator_5 = "✅" if roi_5years > 100 else "⚠️" if roi_5years > 0 else "❌"
            st.markdown(f"""
            <div class="kpi-card {roi_color_5}">
                <div class="kpi-label">5 Anos</div>
                <div class="kpi-value">{roi_5years:.1f}%</div>
                <div class="kpi-indicator">{roi_indicator_5}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Payback and Key Metrics

    
    payback_col1, payback_col2, payback_col3 = st.columns(3, gap="small")
    
    with payback_col1:
        payback_indicator = "✅" if result.payback_period_months < 12 else "⚠️"
        st.markdown(f"""
        <div class="kpi-card kpi-orange">
            <div class="kpi-label">Payback</div>
            <div class="kpi-value">{result.payback_period_months:.1f}m ({result.payback_period_months/12:.1f}a)</div>
            <div class="kpi-indicator">{payback_indicator}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with payback_col2:
        monthly_indicator = "✅" if total_monthly_savings > 0 else "❌"
        st.markdown(f"""
        <div class="kpi-card kpi-cyan">
            <div class="kpi-label">Economia Mensal</div>
            <div class="kpi-value">{format_currency(total_monthly_savings)}</div>
            <div class="kpi-indicator">{monthly_indicator}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with payback_col3:
        capacity_hours = result.automation_capacity
        capacity_indicator = "✅" if capacity_hours > 0 else "❌"
        st.markdown(f"""
        <div class="kpi-card kpi-pink">
            <div class="kpi-label">Capacidade Liberada</div>
            <div class="kpi-value">{capacity_hours:.0f}h/mês</div>
            <div class="kpi-indicator">{capacity_indicator}</div>
        </div>
        """, unsafe_allow_html=True)
    

    
    st.divider()
    
    # Detailed Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); padding: 15px; border-left: 4px solid #3B82F6; border-radius: 5px; margin-bottom: 15px;">
            <h3 style="margin-top: 0; color: #3B82F6;">💳 Análise Financeira</h3>
        </div>
        """, unsafe_allow_html=True)
        
        current_monthly_cost = (
            roi_input.current_time_per_month * 
            roi_input.people_involved * 
            roi_input.hourly_rate
        )
        
        rpa_monthly_cost_total = (
            (roi_input.current_time_per_month * 
             roi_input.people_involved * 
             roi_input.hourly_rate * 
             (1 - roi_input.expected_automation_percentage/100)) + 
            roi_input.rpa_monthly_cost
        )
        
        fines_avoided = st.session_state.calculator_results.get("fines_avoided", 0)
        sql_savings = st.session_state.calculator_results.get("sql_savings", 0)
        
        # Total savings including additional benefits
        total_monthly_savings = result.monthly_savings + fines_avoided + sql_savings
        total_annual_savings = total_monthly_savings * 12
        
        financial_data = {
            "Custo Atual (Mensal)": format_currency(current_monthly_cost),
            "Custo com RPA (Mensal)": format_currency(rpa_monthly_cost_total),
            "Economia de Mão de Obra": format_currency(result.monthly_savings),
            "Multas Evitadas": format_currency(fines_avoided),
            "SLA Reduzida": format_currency(sql_savings),
            "Economia Total (Mensal)": format_currency(total_monthly_savings),
            "Economia Anual Total": format_currency(total_annual_savings),
            "Custo de Implementação": format_currency(roi_input.rpa_implementation_cost),
        }
        
        for label, value in financial_data.items():
            st.write(f"**{label}:** {value}")
    
    with col2:
        st.markdown("""
        <div style="background: rgba(168, 85, 247, 0.1); padding: 15px; border-left: 4px solid #A855F7; border-radius: 5px; margin-bottom: 15px;">
            <h3 style="margin-top: 0; color: #A855F7;">📊 Indicadores de ROI</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Recalculate payback with additional benefits
        total_monthly_savings = result.monthly_savings + fines_avoided + sql_savings
        if total_monthly_savings > 0:
            adjusted_payback = roi_input.rpa_implementation_cost / total_monthly_savings
        else:
            adjusted_payback = 0
        
        adjusted_roi_percentage = ((total_monthly_savings * 12 - roi_input.rpa_implementation_cost) / 
                                   roi_input.rpa_implementation_cost * 100)
        adjusted_roi_value = total_monthly_savings * 12 - roi_input.rpa_implementation_cost
        
        roi_data = {
            "Payback (Meses)": f"{adjusted_payback:.1f}",
            "Payback (Anos)": f"{adjusted_payback/12:.2f}",
            "ROI 1º Ano (%)": format_percentage(adjusted_roi_percentage),
            "Retorno Financeiro": format_currency(adjusted_roi_value),
            "Capacidade Liberada": f"{result.automation_capacity:.0f} horas/mês",
        }
        
        for label, value in roi_data.items():
            st.write(f"**{label}:** {value}")
    
    st.divider()
    
    # Process Details
    st.markdown("""
    <div style="background: rgba(34, 197, 94, 0.1); padding: 15px; border-left: 4px solid #22C55E; border-radius: 5px; margin-bottom: 15px;">
        <h3 style="margin-top: 0; color: #22C55E;">🔧 Detalhes do Processo</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Departamento", st.session_state.calculator_results.get("department", "N/A"))
    
    with col2:
        st.metric("Complexidade", st.session_state.calculator_results.get("complexity", "N/A"))
    
    with col3:
        st.metric("Quantidade de Sistemas", f"{st.session_state.calculator_results.get('systems_quantity', 0)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Transações/Dia", f"{st.session_state.calculator_results.get('daily_transactions', 0):,.0f}")
    
    with col2:
        st.metric("Taxa de Erro", f"{st.session_state.calculator_results.get('error_rate', 0):.0f}%")
    
    with col3:
        st.metric("Taxa de Exceção", f"{st.session_state.calculator_results.get('exception_rate', 0):.0f}%")
    
    
    st.divider()
    
    # Implementation Details
    st.markdown("""
    <div style="background: rgba(249, 115, 22, 0.1); padding: 15px; border-left: 4px solid #F97316; border-radius: 5px; margin-bottom: 15px;">
        <h3 style="margin-top: 0; color: #F97316;">⚙️ Detalhes de Implementação</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Horas de Desenvolvimento:** {st.session_state.calculator_results.get('dev_hours', 0):.0f}h")
        st.write(f"**Valor Hora Dev:** {format_currency(st.session_state.calculator_results.get('dev_hourly_rate', 0))}")
        st.write(f"**Custo de Desenvolvimento:** {format_currency(st.session_state.calculator_results.get('dev_total_cost', 0))}")
        st.write(f"**Outros Custos:** {format_currency(st.session_state.calculator_results.get('other_costs', 0))}")
    
    with col2:
        st.write(f"**Manutenção Mensal:** {format_currency(st.session_state.calculator_results.get('monthly_cost', 0))}")
        st.write(f"**Infra/Licenças:** {format_currency(st.session_state.calculator_results.get('infra_license_cost', 0))}")
        st.write(f"**Custo Mensal Total:** {format_currency(st.session_state.calculator_results.get('total_monthly_cost', 0))}")
        st.write(f"**Percentual Manutenção:** {st.session_state.calculator_results.get('maintenance_percentage', 0):.0f}%")
    
    # Save to database
    st.divider()
    st.markdown("""
    <div style="padding: 20px 0;">
        <p style="text-align: center; color: #666; font-size: 14px;">💾 <strong>Salvar este cálculo na base de dados</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Salvar Cálculo", width="stretch"):
            try:
                fines_avoided = st.session_state.calculator_results.get("fines_avoided", 0)
                sql_savings = st.session_state.calculator_results.get("sql_savings", 0)
                total_monthly_savings = result.monthly_savings + fines_avoided + sql_savings
                
                calculation_data = {
                    "process_name": roi_input.process_name,
                    "current_time_per_month": roi_input.current_time_per_month,
                    "people_involved": roi_input.people_involved,
                    "hourly_rate": roi_input.hourly_rate,
                    "rpa_implementation_cost": roi_input.rpa_implementation_cost,
                    "rpa_monthly_cost": roi_input.rpa_monthly_cost,
                    "expected_automation_percentage": roi_input.expected_automation_percentage,
                    "monthly_savings": total_monthly_savings,
                    "annual_savings": total_monthly_savings * 12,
                    "payback_period_months": roi_input.rpa_implementation_cost / total_monthly_savings if total_monthly_savings > 0 else 0,
                    "roi_first_year": (total_monthly_savings * 12 - roi_input.rpa_implementation_cost),
                    "roi_percentage_first_year": ((total_monthly_savings * 12 - roi_input.rpa_implementation_cost) / roi_input.rpa_implementation_cost * 100),
                }
                
                db_manager.save_calculation(calculation_data)
                st.success("✅ Cálculo salvo com sucesso! Veja o histórico na aba 'Histórico de Resultados'")
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {str(e)}")
    
    with col2:
        if st.button("Novo Cálculo", width="content"):
            st.session_state.show_results = False
            st.session_state.calculator_results = None
            st.rerun()