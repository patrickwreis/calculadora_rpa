# -*- coding: utf-8 -*-
"""About Page"""
import streamlit as st

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION

# Page config
st.set_page_config(
    page_title=f"{APP_NAME} - Sobre",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="collapsed"
)



# Page header
st.title("ℹ️ Sobre a Aplicação")

st.markdown(f"""
## {APP_NAME} v{APP_VERSION}

### 📝 Descrição
{APP_DESCRIPTION}

### 🎯 Objetivos
- ✅ Calcular o retorno real de investimentos em automação RPA
- ✅ Fornecer análise financeira detalhada
- ✅ Apoiar tomadas de decisão baseadas em dados
- ✅ Armazenar histórico de projetos

### 💡 Como Usar
1. Acesse a página **Calculadora**
2. Preencha os dados do processo atual
3. Informe os custos de implementação
4. Visualize os resultados
5. Salve o cálculo para referência futura

### 📊 Métricas Calculadas
- **Economia Mensal:** Diferença entre custo atual e custo com RPA
- **Economia Anual:** Projeção anual da economia
- **Payback Period:** Tempo para recuperar o investimento
- **ROI:** Retorno sobre investimento no primeiro ano

### 🔒 Privacidade
Todos os dados são armazenados localmente no seu banco de dados.

### 📧 Suporte
Para dúvidas ou sugestões, entre em contato com o desenvolvedor.
""")

st.divider()

st.markdown("""
---
*Desenvolvido com ❤️ usando Streamlit e Python*
""")
