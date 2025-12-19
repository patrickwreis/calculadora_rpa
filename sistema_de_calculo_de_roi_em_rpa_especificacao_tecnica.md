# PROMPT TÉCNICO — Sistema de Cálculo de ROI em RPA

## CONTEXTO GERAL
Você é um **engenheiro de software sênior / arquiteto full-stack** responsável por projetar e implementar um **sistema web** para cálculo de **ROI de automações RPA**.

O sistema **NÃO é SaaS**, **NÃO é multi-tenant** e **NÃO possui conceito de empresa**. Todo o escopo é baseado apenas em **usuários individuais autenticados**.

Este documento deve ser usado **diretamente como prompt para o Lovable**, portanto:
- Seja **determinístico**
- Assuma **boas práticas de engenharia**
- Gere código, arquitetura e fluxos completos
- **Escolha livremente a stack tecnológica**

---

## OBJETIVO DO SISTEMA

Construir uma aplicação que:
- Calcule ROI, payback e economia de automações RPA
- Armazene histórico de análises por usuário
- Gere ranking de processos automatizáveis
- Sirva como ferramenta de decisão técnica e financeira

---

## REQUISITOS FUNCIONAIS

### AUTENTICAÇÃO E USUÁRIOS

- Login com e-mail e senha
- Cadastro de usuário
- Recuperação de senha
- Hash de senha seguro (bcrypt ou equivalente)
- Autenticação baseada em token ou sessão

Perfis de acesso:
- USER: acesso completo às próprias análises
- ADMIN: acesso a todos os registros e parâmetros globais

---

## TELAS OBRIGATÓRIAS

### 1. LOGIN / CADASTRO

Campos:
- Email
- Senha

Ações:
- Login
- Criar conta
- Recuperar senha

---

### 2. DASHBOARD PRINCIPAL

KPIs do usuário:
- Total de processos analisados
- Economia anual potencial total
- ROI médio
- Payback médio

Visualizações:
- Gráfico de ROI por processo
- Gráfico de economia anual por processo
- Distribuição por complexidade

---

### 3. CRIAÇÃO / EDIÇÃO DE ANÁLISE (PÁGINA ÚNICA)

Todos os campos abaixo devem estar **em uma única página**, organizados por seções visuais.

#### DADOS BÁSICOS
- Nome do processo
- Área / categoria
- Número de funcionários
- Custo médio mensal por funcionário
- Horas por dia dedicadas ao processo
- Dias trabalhados no mês

---

#### CARACTERÍSTICAS DO PROCESSO
- Complexidade da automação (BAIXA | MÉDIA | ALTA)
- Número de sistemas envolvidos
- Volume de transações por dia
- Taxa de erro atual (%)
- Taxa de exceção (%)

---

#### CUSTOS DE AUTOMAÇÃO
- Custo de licença RPA (mensal)
- Custo de infraestrutura (mensal)
- Horas estimadas de desenvolvimento
- Horas estimadas de testes
- Valor hora RPA

---

#### BENEFÍCIOS ADICIONAIS
- Multas evitadas (anual)
- Ganho de SLA (horas/mês)

---

## MODELO DE CÁLCULO (OBRIGATÓRIO)

### 1. CUSTO ATUAL DO PROCESSO

```
custo_mensal_atual = funcionarios * custo_funcionario * (horas_dia / 8)
custo_anual_atual = custo_mensal_atual * 12
```

---

### 2. ECONOMIA POTENCIAL

A economia humana considera que **a automação elimina o trabalho manual exceto pelas exceções**.

```
percentual_automatizado = 1 - taxa_excecao

economia_humana = custo_anual_atual * percentual_automatizado
economia_erros = custo_anual_atual * (taxa_erro * fator_impacto_erro)
```

---

### 3. CUSTO DE IMPLEMENTAÇÃO RPA

Multiplicadores de complexidade:
- BAIXA = 1.0
- MÉDIA = 1.6
- ALTA = 2.5

```
custo_base = (horas_dev + horas_testes) * valor_hora
custo_impl = custo_base * multiplicador_complexidade
custo_impl *= (1 + sistemas * 0.1)
```

---

### 4. CUSTOS RECORRENTES

```
custo_recorrente_anual = (licenca_mensal + infraestrutura_mensal) * 12
custo_recorrente_anual += custo_impl * 0.15
```

---

### 5. GANHO TOTAL

```
ganho_total = economia_humana + economia_erros + multas_evitadas
```

---

### 6. ROI E PAYBACK

```
ROI = (ganho_total - custo_impl) / custo_impl
payback_meses = custo_impl / (ganho_total / 12)
```

---

## RANKING DE PROCESSOS

O sistema deve gerar rankings **por usuário**, ordenáveis por:
- Maior ROI
- Menor Payback
- Maior economia anual

Classificações automáticas:
- QUICK WIN: ROI > 50% e Payback < 12 meses
- MÉDIO PRAZO: ROI positivo e Payback < 24 meses
- BAIXA PRIORIDADE: ROI negativo

---

## HISTÓRICO E VERSIONAMENTO

- Cada análise pertence a um único usuário
- Permitir edição e reavaliação
- Manter histórico de cálculos

---

## RELATÓRIOS

- Visualização detalhada da análise
- Exportação PDF
- Exportação Excel

---

## MODELO DE DADOS (RELACIONAL)

### USERS
- id
- name
- email
- password_hash
- role

### PROCESSES
- id
- user_id
- name
- area
- complexity
- created_at
- updated_at

### PROCESS_INPUTS
- process_id
- funcionarios
- custo_funcionario
- horas_dia
- dias_mes
- volume
- taxa_erro
- taxa_excecao

### PROCESS_COSTS
- process_id
- licenca
- infraestrutura
- horas_dev
- horas_testes
- valor_hora

### PROCESS_RESULTS
- process_id
- custo_anual
- custo_impl
- ganho_total
- roi
- payback

---

## REGRAS DE QUALIDADE

- Engine de cálculo desacoplada da UI
- Validação de inputs
- Código modular e legível
- Persistência confiável

---

## RESULTADO ESPERADO

Gerar uma aplicação funcional com:
- Autenticação de usuários
- Criação de análises em página única
- Cálculo financeiro consistente
- Ranking automático por usuário
- Histórico persistente

Este documento deve ser tratado como **prompt final e fonte única de verdade para implementação**.

