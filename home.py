import streamlit as st

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="ROI RPA Analyzer | Calcule o Retorno Real",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CSS PERSONALIZADO ==========
st.markdown("""
<style>
    /* Reset e configurações gerais */
    :root {
        --primary: #42b885;
        --primary-dark: #2d9d6f;
        --secondary: #8b5cf6;
        --dark-bg: #0a0e27;
        --dark-light: #1a1f3a;
        --dark-lighter: #252d47;
        --text-primary: #e0e0e0;
        --text-secondary: #a0a8c0;
        --border: #323a52;
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
        --radius: 8px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Estilo geral */
    .stApp {
        background: var(--dark-bg);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        line-height: 1.6;
    }
    
    /* Esconder elementos padrão do Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Container principal personalizado */
    .main .block-container {
        padding-top: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 3.5rem !important;
        line-height: 1.2 !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.75rem !important;
    }
    
    p {
        font-size: 1.125rem !important;
        color: var(--text-secondary) !important;
        line-height: 1.7 !important;
    }
    
    .highlight {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    /* Seções */
    section {
        padding: 1rem 0 !important; /* reduced further to tighten vertical spacing */
        position: relative !important;
    }
    
    /* Header fixo */
    .stHeader {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        z-index: 1000 !important;
        background: rgba(10, 14, 39, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid var(--border) !important;
        padding: 1.25rem 0 !important;
    }
    
    /* Botões personalizados */
    .stButton > button {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 12px 28px !important;
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        cursor: pointer !important;
        transition: var(--transition) !important;
        font-family: inherit !important;
        text-decoration: none !important;
        min-height: 44px !important;
    }
    
    .btn {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 12px 28px !important;
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        cursor: pointer !important;
        transition: var(--transition) !important;
        font-family: inherit !important;
        text-decoration: none !important;
    }

    .btn-primary {
        background-color: var(--primary) !important;
        color: #000 !important;
    }
    
    .btn-primary:hover {
        background-color: var(--primary-dark) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 24px rgba(66, 184, 133, 0.3) !important;
    }
    
    .btn-secondary {
        background-color: transparent !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
    }
    
    .btn-secondary:hover {
        background-color: rgba(66, 184, 133, 0.1) !important;
    }
    
    .btn-large {
        padding: 14px 36px !important;
        font-size: 1.125rem !important;
    }
    
    /* Cards */
    .feature-card, .metric-card, .usecase-card {
        background: rgba(37, 45, 71, 0.5) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 2.5rem 2rem !important;
        transition: var(--transition) !important;
        height: 100% !important;
    }
    
    .feature-card:hover {
        background: rgba(37, 45, 71, 0.8) !important;
        border-color: var(--primary) !important;
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(66, 184, 133, 0.1) !important;
    }
    
    .metric-card {
        padding: 2rem !important;
        text-align: center !important;
    }
    
    .metric-card:hover {
        border-color: var(--primary) !important;
        background: rgba(66, 184, 133, 0.05) !important;
    }
    
    .usecase-card {
        border-left: 4px solid var(--primary) !important;
        padding: 2rem !important;
    }
    
    .usecase-card:hover {
        background: rgba(37, 45, 71, 0.8) !important;
        border-left-color: var(--secondary) !important;
    }
    
    /* Ícones */
    .feature-icon {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 60px !important;
        height: 60px !important;
        background: rgba(66, 184, 133, 0.1) !important;
        border-radius: var(--radius) !important;
        color: var(--primary) !important;
        font-size: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-label {
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
    }
    
    /* Badges */
    .badge {
        display: inline-flex !important;
        align-items: center !important;
        padding: 8px 16px !important;
        background-color: rgba(66, 184, 133, 0.1) !important;
        border: 1px solid rgba(66, 184, 133, 0.3) !important;
        border-radius: 50px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: var(--primary) !important;
        gap: 6px !important;
    }
    
    /* Steps */
    .step-number {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 80px !important;
        height: 80px !important;
        background: rgba(66, 184, 133, 0.1) !important;
        border: 2px solid var(--primary) !important;
        border-radius: 50% !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Steps layout (horizontal timeline) */
    .steps {
        display: flex !important;
        gap: 30px !important;
        margin-top: 50px !important;
        position: relative !important;
        align-items: flex-start !important;
    }

    .steps::before {
        content: '' !important;
        position: absolute !important;
        top: 40px !important;
        left: 40px !important;
        right: 40px !important;
        height: 2px !important;
        background: linear-gradient(90deg, var(--primary) 0%, transparent 100%) !important;
        z-index: 0 !important;
    }

    .step {
        flex: 1 !important;
        text-align: center !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Hero */
    .hero {
        padding-top: 110px !important;
        padding-bottom: 40px !important; /* reduced to eliminate large gap under hero */
        background: linear-gradient(135deg, rgba(10, 14, 39, 1) 0%, rgba(37, 45, 71, 0.2) 100%) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .hero::before {
        content: "" !important;
        position: absolute !important;
        top: -50% !important;
        right: -20% !important;
        width: 600px !important;
        height: 600px !important;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%) !important;
        border-radius: 50% !important;
        z-index: 0 !important;
    }

    .hero::after {
        content: "" !important;
        position: absolute !important;
        bottom: -20% !important;
        left: -10% !important;
        width: 400px !important;
        height: 400px !important;
        background: radial-gradient(circle, rgba(66, 184, 133, 0.1) 0%, transparent 70%) !important;
        border-radius: 50% !important;
        z-index: 0 !important;
    }

    .hero-content {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 24px !important;
        position: relative !important;
        z-index: 1 !important;
        text-align: center !important;
    }

    .hero-text {
        flex: 1 !important;
    }

    .hero-text h1 {
        margin-bottom: 24px !important;
    }

    .hero-buttons {
        display: flex !important;
        gap: 16px !important;
        margin: 40px 0 !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
    }

    .hero-badges {
        display: flex !important;
        gap: 12px !important;
        flex-wrap: wrap !important;
        margin-top: 32px !important;
        justify-content: center !important;
    }

    .hero-image {
        flex: 1 !important;
        text-align: center !important;
    }

    .hero-image img {
        max-width: 100% !important;
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 20px 40px rgba(66, 184, 133, 0.15) !important;
    }
    
    .dark-section {
        background-color: var(--dark-light) !important;
        /* Ajuste: remover padding-top para evitar faixa vazia entre seções */
        padding-top: 0 !important;
        padding-bottom: 2rem !important;
    }

    /* Ensure gradient sections have no extra top gap */
    .gradient-section {
        padding-top: 0 !important;
        padding-bottom: 2rem !important;
    }

    .section-header {
        margin-top: 0 !important; /* avoid extra top gap */
        margin-bottom: 2rem !important;
    }

    .grid-3, .grid-4 {
        margin-top: 0 !important;
    }
    
    .gradient-section {
        background: linear-gradient(135deg, var(--dark-bg) 0%, var(--dark-light) 100%) !important;
    }
    
    .cta-section {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        text-align: center !important;
        color: #000 !important;
        padding: 6rem 0 !important; /* larger, like original */
    }

    .cta-section h2 {
        color: #000 !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
        font-weight: 700 !important;
    }

    .cta-section p {
        color: rgba(0,0,0,0.85) !important;
        max-width: 700px !important;
        margin: 0 auto 2rem !important;
        font-size: 1.125rem !important;
    }
    
    .section-header {
        text-align: center !important;
        max-width: 700px !important;
        margin: 0 auto 3.75rem !important;
    }
    
    .section-subtitle {
        font-size: 1.125rem !important;
        color: var(--text-secondary) !important;
    }
    
    /* Grid */
    .grid-3 {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important;
        gap: 30px !important;
    }
    
    .grid-4 {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
        gap: 24px !important;
        margin-bottom: 2.5rem !important;
    }
    
    .grid-2 {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 24px !important;
    }
    
    /* Links de navegação */
    .nav-link {
        color: var(--text-secondary) !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
    }
    
    .nav-link:hover {
        color: var(--primary) !important;
        background: rgba(66, 184, 133, 0.05) !important;
    }
    
    /* Responsividade */
    @media (max-width: 992px) {
        h1 {
            font-size: 2.75rem !important;
        }
        
        h2 {
            font-size: 2rem !important;
        }
        
        .hero-content {
            flex-direction: column !important;
        }
    }
    
    @media (max-width: 768px) {
        section {
            padding: 3.75rem 0 !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .grid-3, .grid-4, .grid-2 {
            grid-template-columns: 1fr !important;
        }
        
        .hero-section {
            padding-top: 6rem !important;
        }
    }
    
    /* Classes utilitárias */
    .text-center { text-align: center !important; }
    .flex { display: flex !important; }
    .flex-col { flex-direction: column !important; }
    .items-center { align-items: center !important; }
    .justify-between { justify-content: space-between !important; }
    .justify-center { justify-content: center !important; }
    .gap-2 { gap: 0.5rem !important; }
    .gap-4 { gap: 1rem !important; }
    .gap-6 { gap: 1.5rem !important; }
    .gap-8 { gap: 2rem !important; }
    .w-full { width: 100% !important; }
    .mx-auto { margin-left: auto !important; margin-right: auto !important; }
    .my-4 { margin-top: 1rem !important; margin-bottom: 1rem !important; }
    .mt-2 { margin-top: 0.5rem !important; }
    .mt-4 { margin-top: 1rem !important; }
    .mt-6 { margin-top: 1.5rem !important; }
    .mt-8 { margin-top: 2rem !important; }
    .mb-2 { margin-bottom: 0.5rem !important; }
    .mb-4 { margin-bottom: 1rem !important; }
    .mb-6 { margin-bottom: 1.5rem !important; }
    .mb-8 { margin-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ========== HEADER FIXO ==========
st.markdown("""
<div class="stHeader">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="logo" style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">
                <span style="color: var(--primary);">📈</span>
                ROI RPA Analyzer
            </div>
            <div style="display: flex; gap: 32px; align-items: center;">
                <a href="#features" class="nav-link">Funcionalidades</a>
                <a href="#how-it-works" class="nav-link">Como Funciona</a>
                <a href="#use-cases" class="nav-link">Para Quem</a>
                <a href="#cta" style="text-decoration: none;">
                    <button class="btn-primary btn-large" style="margin: 0; padding: 14px 36px; border-radius: 12px;">Começar Agora</button>
                </a>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========== HERO SECTION ==========
st.markdown("""
<section class="hero">
    <div class="container">
        <div class="hero-content">
            <div class="hero-text">
                <h1>Calcule o <span class="highlight">ROI Real</span> de suas Automações RPA</h1>
                <p>Ferramenta profissional para análise financeira. Justifique investimentos com dados concretos e tome decisões baseadas em números.</p>
                <div class="hero-buttons">
                    <a href="#calculator" class="btn btn-primary btn-large">Calcular Agora</a>
                    <a href="#features" class="btn btn-secondary btn-large">Saiba Mais</a>
                </div>
                <div class="hero-badges">
                    <div class="badge">
                        <i class="fas fa-check-circle"></i> 100% Gratuito
                    </div>
                    <div class="badge">
                        <i class="fas fa-lock"></i> Cadastro Simples
                    </div>
                    <div class="badge">
                        <i class="fas fa-lightning-bolt"></i> Cálculos Imediatos
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# ========== FEATURES SECTION ==========
st.markdown("""
<section class="dark-section" id="features">
  <div class="container">
    <div class="section-header">
        <h2>Funcionalidades Principais</h2>
        <p class="section-subtitle">Tudo que você precisa para analisar o retorno de suas automações</p>
    </div>
    <div class="grid-3">
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-calculator"></i></div>
            <h3>Calculadora ROI em Tempo Real</h3>
            <p>Calcula automaticamente ROI, Payback e economia anual. Preview gratuito sem necessidade de login.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
            <h3>Análise Profunda de Processos</h3>
            <p>Coleta dados detalhados, avalia complexidade, considera custos reais e analisa riscos da automação.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-chart-bar"></i></div>
            <h3>Dashboard Executivo</h3>
            <p>Visualiza KPIs principais, economia total potencial e projeções em tempo real com cards coloridos.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-trophy"></i></div>
            <h3>Ranking Inteligente</h3>
            <p>Ordena processos por ROI, Payback ou Economia. Prioriza automaticamente as melhores oportunidades.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-file-excel"></i></div>
            <h3>Relatórios em Excel</h3>
            <p>Exporta análises profissionais com tabelas de cálculos, gráficos, visualizações e recomendações.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-cogs"></i></div>
            <h3>Gerenciamento Completo</h3>
            <p>Salva múltiplas análises, edita existentes, compara cenários e mantém histórico completo de projetos.</p>
        </div>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# ========== MÉTRICAS SECTION ==========
# ========== MÉTRICAS SECTION ==========
st.markdown("""
<section class="gradient-section">
  <div class="container">
    <div class="section-header">
        <h2>O que Calculamos</h2>
        <p class="section-subtitle">Métricas financeiras essenciais para sua decisão</p>
    </div>
    <div class="grid-4">
        <div class="metric-card">
            <div class="metric-value">ROI %</div>
            <div class="metric-label">Return on Investment no Ano 1</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">Payback</div>
            <div class="metric-label">Meses para Recuperar Investimento</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">Economia</div>
            <div class="metric-label">Bruta e Líquida Anual</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">Horas</div>
            <div class="metric-label">Liberadas para Tarefas de Valor</div>
        </div>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# ========== HOW IT WORKS SECTION ==========
st.markdown("""
<section class="dark-section" id="how-it-works">
    <div class="container">
        <div class="section-header">
                <h2>Como Funciona</h2>
                <p class="section-subtitle">Três passos simples para análise completa</p>
        </div>
        <div class="steps">
            <div class="step">
                <div class="step-number">1</div>
                <h3>Insira Dados</h3>
                <p>Forneça informações do seu processo: tempo, pessoas, custo horário e complexidade.</p>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <h3>Análise Automática</h3>
                <p>Nossa ferramenta calcula ROI, Payback e economia com base em algoritmos validados.</p>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <h3>Decisões Informadas</h3>
                <p>Receba relatórios detalhados para justificar investimentos à diretoria.</p>
            </div>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# ========== USE CASES SECTION ==========
# ========== USE CASES SECTION ==========
st.markdown("""
<section class="dark-section" id="use-cases">
  <div class="container">
    <div class="section-header">
        <h2>Para Quem É Ideal</h2>
        <p class="section-subtitle">A ferramenta serve para diferentes perfis e necessidades</p>
    </div>
    <div class="grid-2">
        <div class="usecase-card">
            <h4>🏢 Gestores e Diretores</h4>
            <p>Justifique investimento em RPA com números concretos. Priorize quais processos automatizar primeiro. Acompanhe retorno esperado vs realizado.</p>
        </div>
        <div class="usecase-card">
            <h4>🎓 Consultores RPA</h4>
            <p>Demonstre valor para clientes. Use como lead magnet gratuito. Faça propostas baseadas em dados. Compare cenários com clientes.</p>
        </div>
        <div class="usecase-card">
            <h4>💰 CFO/Financeiro</h4>
            <p>Análise detalhada de ROI. Planilhas com todas as variáveis. Projeções de fluxo de caixa. Comparação entre diferentes cenários.</p>
        </div>
        <div class="usecase-card">
            <h4>💻 Times de RPA</h4>
            <p>Valide complexidade de projetos. Estime horas de desenvolvimento. Acompanhe economias realizadas. Base histórica de projetos.</p>
        </div>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# ========== CTA SECTION ==========
st.markdown("""
<section class="cta-section" id="cta">
  <div class="container">
    <div class="section-header">
        <h2 style="color: #000;">Comece a Analisar Seus Processos Agora</h2>
    </div>
    <div style="display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin-top:1.5rem;">
        <a href="#features" style="text-decoration:none;">
            <button class="btn-primary btn-large" style="min-width:250px; padding:14px 36px; border-radius:12px;">
                Calcular ROI Agora
            </button>
        </a>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# ========== FONT AWESOME ICONS ==========
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)