# Roadmap (baby steps) — calculadora RPA

Roadmap enxuto para commits pequenos e branches por feature. Siga cada item em pequenas PRs/commits.

- Autenticação (feature/auth)
  - Criar branch `feature/auth` e commit inicial vazio
  - Implementar endpoint de cadastro (POST /register)
  - Implementar endpoint de login (POST /login)
  - Implementar recuperação de senha (POST /reset)
  - Adicionar hashing seguro (bcrypt) e testes mínimos

- Modelos e migrations (feature/process-model)
  - Criar models: `users`, `processes`, `process_inputs`, `process_costs`, `process_results`
  - Adicionar migrations iniciais
  - Commit com esquema de banco pronto

- CRUD de análises (feature/process-crud)
  - API: criar/analisar/editar/excluir/listar processos
  - Persistir inputs, custos e resultados
  - Testes de integração básicos

- Motor de cálculo (feature/calculation-engine)
  - Implementar engine desacoplada com as fórmulas do documento
  - Escrever testes unitários para cada fórmula
  - Commit com cobertura mínima das regras financeiras

- Dashboard e KPIs (feature/dashboard)
  - Endpoints para KPIs: total análises, economia anual, ROI médio, payback médio
  - Visualizações básicas (endpoint JSON) para frontend consumir

- Ranking e classificações (feature/ranking)
  - Implementar ranking por ROI/payback/economia
  - Classificações: QUICK WIN, MÉDIO PRAZO, BAIXA PRIORIDADE

- Histórico e versionamento (feature/history-versioning)
  - Salvar versões de análises ao editar
  - Endpoint para listar histórico de versões por análise

- Relatórios (feature/reports-export)
  - Exportar PDF com detalhes da análise
  - Exportar Excel/CSV com resultados

- Docs, ambiente e chores
  - `chore/docs-readme`: README com setup (virtualenv), uso e exemplos
  - `chore/requirements`: revisar e fixar versões em `requirements.txt`
  - `chore/gitignore`: garantir entradas para venv e caches
  - `chore/lint-format`: adicionar config e rodar `black`/`flake8`
  - `chore/ci-tests`: pipeline CI rodando testes

- Release
  - `release/changelog`: preparar changelog e commits pequenos por release

---

Sequência recomendada para primeiros commits:
1. `chore/docs-readme` (README mínimo)
2. `feature/process-model` (models + migrations)
3. `feature/calculation-engine` (engine + testes)
4. `feature/process-crud` (CRUD básico)

Cada item acima deve ser implementado em uma branch própria e com commits pequenos (1 alteração por commit quando possível).

--
Gerado para guiar desenvolvimento incremental baseado na especificação técnica.
