# 🧩 Arquitetura do Linkfort DNS (V3.5 - Clean Architecture)

Este documento reflete a estrutura de código limpa e os componentes de software em produção, incluindo a camada de apresentação visual.

## 🗺️ Mapa de Dependências

```mermaid
graph TD
    %% Nós de Entrada e Configuração
    User((Usuário))
    CLI[linkfort]
    
    %% Camada de Coleta
    Monitor[monitor_dados.sh]
    RawData[(dados_dns_linkfort.csv)]
    
    %% Camada de Processamento
    Analyzer[gerar_dashboard.py]
    Venv[.venv/ Libs]
    JsonData[(dados.json)]
    
    %% Camada de Servidor
    Server[serve.py]
    Browser[Web Browser]
    DashboardFile[dashboard.html <br> (Static Template)]
    
    %% Fluxo
    User -->|Executa| CLI
    
    CLI -->|--live| Parallel{Modo Paralelo}
    Parallel -->|Start BG| Monitor
    Parallel -->|Start FG| Server
    
    Monitor -->|Write| RawData
    
    RawData -->|Read| Analyzer
    Venv -.->|Import| Analyzer
    
    Analyzer -->|Export Data + Charts| JsonData
    
    Server -->|Serve :7777| Browser
    Server -.->|Serve File| DashboardFile
    Server -.->|Serve API| JsonData
    
    Browser -->|Load HTML| DashboardFile
    Browser -->|Fetch JS| JsonData
    JsonData -->|Render| Browser
```

## 📂 Componentes Principais

### 🚀 Orquestração (`linkfort`)
O ponto de entrada único do sistema (antigo `run_all.sh`).
- **Função**: CLI Unificada.
- **Responsabilidades**:
    - **Diagnóstico**: Verifica versões de Python/Pip e integridade do venv na inicialização.
    - **Gestão**: Controla processos (Monitor+Server), estima tempo de coleta e realiza Reset de dados.

### 📡 Coleta (`monitor_dados.sh`)
O worker de I/O.
- **Tecnologia**: Bash + `dig`.
- **Estratégia**: Execução sequencial com throttling (0.5s) e detecção automática de ambiente Python.

### 🧠 Análise & Visualização (`src/` Package)
A lógica de negócio foi refatorada em uma arquitetura modular limpa:
- **Orquestrador**: `gerar_dashboard.py` (Main entry point).
- **Módulos (`src/*.py`)**:
    - `data.py`: Carregamento e sanitização de CSV.
    - `analytics.py`: Algoritmos de Score V3.0 e estatísticas.
    - `charts.py`: Fábrica de gráficos Plotly (Dark Mode).
    - `exporter.py`: Serialização para `dados.json`.

### 🌐 Visualização Client-Side (`dashboard.html`)
O frontend estático.
- **Arquitetura**: Single Page Application (Simples) que consome `dados.json`.
- **Tecnologia**: HTML5 + Vanilla JS + Plotly.js.
- **Vantagem**: Pode ser versionado no Git pois não muda a cada execução.

### 🌐 Servidor (`serve.py`)
O entregador de experiência.
- **Tecnologia**: Python `http.server`.
- **Porta**: 7777.
- **UX**: Banner ASCII e suporte a CORS implícito para recursos locais.
    
### 🛡️ Resiliência e Auto-Healing
O sistema é projetado para ser **Stateless** na inicialização:
- Se `dados.json` não existir, o frontend exibe estado de "Carregando" até a primeira geração.
- **Conclusão:** O comando `--reset` é seguro pois o sistema recria os dados na próxima rodada.

## 💾 Fluxo de Dados Final (V3.5)

1.  **Coleta**: `monitor_dados.sh` apenda dados ao CSV.
2.  **Processamento**: Python lê CSV, calcula métricas e exporta `dados.json`.
3.  **Persistência**: `dados.json` é sobrescrito (Ignorado pelo Git).
4.  **Entrega**: Servidor disponibiliza estáticos (`html`) e dados (`json`).
5.  **Renderização**: Navegador baixa HTML, depois busca JSON e renderiza gráficos via JS.
6.  **Manutenção**: `dashboard.html` é editado apenas para melhorias visuais/layout, nunca por dados.
