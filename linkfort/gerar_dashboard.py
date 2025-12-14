#!/usr/bin/env python3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

# Configurações de Caminho
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "dados_dns_linkfort.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_HTML = OUTPUT_DIR / "dashboard.html"
OUTPUT_DIR.mkdir(exist_ok=True)

def carregar_dados():
    if not CSV_FILE.exists():
        print(f"ERRO: Arquivo {CSV_FILE} não encontrado.")
        return None
    df = pd.read_csv(CSV_FILE)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    # Remover timeouts ou converter 'timeout' para Nan e depois tratar se necessário
    # Para simplificar, vamos filtrar onde tempo_ms é numérico
    df = df[pd.to_numeric(df['tempo_ms'], errors='coerce').notnull()]
    df['tempo_ms'] = df['tempo_ms'].astype(float)
    return df

def gerar_graficos(df):
    # Gráfico 1: Linha do Tempo (Média por DNS ao longo do tempo)
    # Agrupar por hora ou manter todos os pontos se não forem muitos
    fig_timeline = px.line(df, x="data_hora", y="tempo_ms", color="dns", 
                           title="Latência ao Longo do Tempo (ms)",
                           labels={"tempo_ms": "Tempo (ms)", "data_hora": "Horário"},
                           template="plotly_dark")
    fig_timeline.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))

    # Gráfico 2: Boxplot de Estabilidade (Distribuição)
    fig_boxplot = px.box(df, x="dns", y="tempo_ms", color="dns",
                         title="Estabilidade e Distribuição de Latência",
                         labels={"tempo_ms": "Tempo (ms)", "dns": "Servidor DNS"},
                         template="plotly_dark")
    fig_boxplot.update_layout(showlegend=False)

    return fig_timeline.to_html(full_html=False, include_plotlyjs='cdn'), \
           fig_boxplot.to_html(full_html=False, include_plotlyjs=False)

def calcular_kpis(df):
    # Melhor DNS (Menor Média Geral)
    stats = df.groupby("dns")["tempo_ms"].agg(["mean", "std", "count"]).reset_index()
    melhor_dns = stats.sort_values("mean").iloc[0]
    
    # DNS Mais Estável (Menor Desvio Padrão)
    mais_estavel = stats.sort_values("std").iloc[0]
    
    total_reqs = len(df)
    
    return {
        "melhor_dns_nome": melhor_dns["dns"],
        "melhor_dns_valor": f"{melhor_dns['mean']:.1f}",
        "estavel_dns_nome": mais_estavel["dns"],
        "estavel_dns_valor": f"±{mais_estavel['std']:.1f}",
        "total_reqs": total_reqs,
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

def gerar_html_completo(kpis, plot1, plot2):
    css = """
    :root {
        --bg-color: #0d1117;
        --card-bg: #161b22;
        --text-msg: #c9d1d9;
        --text-title: #f0f6fc;
        --accent: #58a6ff;
        --success: #2ea043;
        --border: #30363d;
    }
    body {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-msg);
        margin: 0;
        padding: 20px;
    }
    .container {
        max_width: 1200px;
        margin: 0 auto;
    }
    header {
        text-align: center;
        margin-bottom: 40px;
        padding-bottom: 20px;
        border-bottom: 1px solid var(--border);
    }
    h1 { color: var(--text-title); margin: 0; font-size: 2.5rem; }
    .subtitle { color: var(--accent); font-size: 1.1rem; }
    
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }
    .card {
        background-color: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-5px); border-color: var(--accent); }
    .card h3 { margin: 0 0 10px 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; }
    .card .value { font-size: 2rem; font-weight: bold; color: var(--text-title); }
    .card .sub { font-size: 0.9rem; color: var(--success); }
    
    .charts-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 40px;
    }
    .chart-box {
        background-color: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 10px;
    }
    footer {
        text-align: center;
        margin-top: 50px;
        font-size: 0.8rem;
        color: #484f58;
    }
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Linkfort DNS Dashboard</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Linkfort Analytics</h1>
                <p class="subtitle">Monitoramento de Performance DNS</p>
                <p>Atualizado em: {kpis['atualizado_em']}</p>
            </header>
            
            <div class="kpi-grid">
                <div class="card">
                    <h3>DNS Mais Rápido</h3>
                    <div class="value">{kpis['melhor_dns_nome']}</div>
                    <div class="sub">{kpis['melhor_dns_valor']} ms (média)</div>
                </div>
                <div class="card">
                    <h3>Mais Estável</h3>
                    <div class="value">{kpis['estavel_dns_nome']}</div>
                    <div class="sub">±{kpis['estavel_dns_valor']} ms (desvio)</div>
                </div>
                <div class="card">
                    <h3>Amostras Coletadas</h3>
                    <div class="value">{kpis['total_reqs']}</div>
                    <div class="sub">Requisições totais</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-box">
                    {plot1}
                </div>
                <div class="chart-box">
                    {plot2}
                </div>
            </div>
            
            <footer>
                Gerado automaticamente pelo Linkfort Analytics
            </footer>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print(">>> Carregando dados...")
    df = carregar_dados()
    if df is None or df.empty:
        print("Sem dados para gerar dashboard.")
        return

    print(">>> Gerando gráficos e KPIs...")
    plot1, plot2 = gerar_graficos(df)
    kpis = calcular_kpis(df)
    
    print(">>> Montando HTML...")
    html_content = gerar_html_completo(kpis, plot1, plot2)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ Dashboard gerado com sucesso em: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
