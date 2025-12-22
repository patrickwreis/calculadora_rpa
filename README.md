# -*- coding: utf-8 -*-
"""
ROI RPA Calculator - Project README
"""

# ROI RPA Calculator

Ferramenta profissional para análise de retorno de investimento (ROI) em automações RPA.

## 📋 Features

- ✅ Calculadora de ROI com análise financeira detalhada
- ✅ Histórico completo de cálculos
- ✅ Armazenamento em banco de dados
- ✅ Interface moderna e intuitiva
- ✅ Testes unitários inclusos

## 🚀 Como Começar

### Requisitos
- Python 3.8+
- pip

### Instalação

1. Clone o repositório
```bash
git clone <repo-url>
cd calculadora_rpa
```

2. Crie um ambiente virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Configure as credenciais de administrador
```bash
# Gere credenciais seguras
python scripts/generate_credentials.py

# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env com as credenciais geradas
# Adicione também as credenciais de email (opcional)
```

5. Execute a aplicação
```bash
streamlit run streamlit_app.py
```

A aplicação estará disponível em `http://localhost:8501`

### Verificar persistência no banco de dados

Há um pequeno script para testar a persistência de um cálculo no banco SQLite:

```bash
python scripts/verify_db.py
```

O script salva um cálculo de teste e imprime os últimos registros.

## 📁 Estrutura do Projeto

```
calculadora_rpa/
├── streamlit_app.py                # Entry point principal
├── config/
│   ├── __init__.py
│   └── settings.py                # Configurações da aplicação
├── src/
│   ├── calculator/
│   │   ├── roi_calculator.py       # Lógica de cálculo
│   │   └── utils.py                # Funções auxiliares
│   ├── models/
│   │   └── calculation.py          # Modelo de dados
│   ├── ui/
│   │   ├── components.py           # Componentes reutilizáveis
│   │   └── styles.py               # Estilos CSS
│   └── database/
│       └── db_manager.py           # Gerenciamento do banco
├── pages/
│   ├── 01_Novo_processo.py         # Página para criar novo processo
│   ├── 02_Processos.py             # Página de processos (histórico)
│   └── 03_About.py                 # Página sobre
├── tests/
│   └── test_calculator.py          # Testes unitários
├── data/                           # Diretório de dados
└── requirements.txt
```

## 🧮 Como Usar

1. **Abra Novo processo**: Acesse a página "Novo processo" no menu lateral
2. **Preencha os Dados**: Informe os detalhes do processo atual
3. **Configure RPA**: Insira custos de implementação e manutenção
4. **Calcule**: Clique em "Calcular ROI"
5. **Salve**: Armazene o cálculo para referência

## 📊 Métricas Calculadas

- **Economia Mensal**: Diferença entre custo atual e com RPA
- **Economia Anual**: Projeção anual da economia
- **Payback Period**: Tempo para recuperar o investimento
- **ROI**: Retorno sobre investimento no primeiro ano

## 🔧 Tecnologias

- **Streamlit**: Framework para web apps em Python
- **SQLModel**: ORM para banco de dados
- **Pandas**: Análise de dados
- **Pytest**: Testes unitários

## 📝 Licença

Este projeto é fornecido como está para fins educacionais e comerciais.

## 👨‍💻 Desenvolvimento

### Rodar Testes
```bash
pytest tests/
```

### Notas de uso
- O campo "Tempo gasto por dia" espera minutos (ex: `480` = `8` horas).
- O campo de manutenção é um percentual ANUAL sobre o custo de desenvolvimento — ele será convertido automaticamente para custo mensal.

### Estrutura de Código
- Separação clara de responsabilidades
- Componentes reutilizáveis
- Type hints em todo o código
- Documentação em docstrings

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato com o desenvolvedor.

---
Desenvolvido com ❤️ usando Streamlit e Python
