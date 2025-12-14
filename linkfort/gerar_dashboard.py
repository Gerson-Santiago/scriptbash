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
    # Gráfico 1: Linha do Tempo (Separada por Domínio para clareza)
    # A bagunça anterior era misturar todos os domínios numa linha só.
    # Agora vamos usar 'facet_col' para separar os gráficos lado a lado.
    fig_timeline = px.line(df, x="data_hora", y="tempo_ms", color="dns", 
                           title="Latência por Domínio ao Longo do Tempo",
                           facet_col="dominio", facet_col_wrap=2, # Quebra linha a cada 2
                           labels={"tempo_ms": "Latência (ms)", "data_hora": "Horário"},
                           template="plotly_dark",
                           height=600) # Aumentar altura
    
    fig_timeline.update_layout(
        hovermode="x unified", 
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=50, b=50)
    )
    # Melhorar visualização do eixo Y (se tiver outlier gigante, limitar ou usar log)
    # Vamos manter linear por enquanto, mas permitir zoom dinâmico

    # Gráfico 2: Boxplot de Estabilidade (Também separado ou agrupado melhor)
    # Vamos ordenar os DNSs pelo KPI de Mediana para o gráfico ficar ordenado
    dns_order = df.groupby("dns")["tempo_ms"].median().sort_values().index.tolist()
    
    fig_boxplot = px.box(df, x="dns", y="tempo_ms", color="dns",
                         title="Distribuição de Latência (Ordenado por Performance)",
                         labels={"tempo_ms": "Latência (ms)", "dns": "Servidor DNS"},
                         category_orders={"dns": dns_order},
                         template="plotly_dark")
    fig_boxplot.update_layout(showlegend=False)
    
    # Gráfico Extra: Taxa de "Linkfort" vs Outros (Para ver se é o melhor no geral)
    # Vamos criar um gráfico de barras com a média por domínio
    fig_bar = px.bar(df.groupby(["dns", "dominio"])["tempo_ms"].median().reset_index(),
                     x="dns", y="tempo_ms", color="dominio", barmode="group",
                     title="Mediana de Latência por Domínio (Menor é Melhor)",
                     template="plotly_dark")
    fig_bar.update_layout(xaxis={'categoryorder':'total ascending'})

    return fig_timeline.to_html(full_html=False, include_plotlyjs='cdn'), \
           fig_boxplot.to_html(full_html=False, include_plotlyjs=False), \
           fig_bar.to_html(full_html=False, include_plotlyjs=False)


def calcular_metricas_avancadas(df):
    # Agrupar por DNS para calcular estatísticas
    stats = df.groupby("dns")["tempo_ms"].agg(["mean", "median", "std", "count", "min", "max"]).reset_index()
    
    # Calcular confiabilidade (Sucesso vs Timeout não capturado aqui pois já filtramos, 
    # mas poderíamos inferir se tivéssemos o total esperado. Vamos focar na estabilidade).
    

    # Score Algoritmo (Ajustado para Subhost/VM):
    # Base: MEDIANA (ignora outliers/jitter da VM)
    # Desempate: Estabilidade (Std Dev)
    
    # Inverter valores (quanto menor melhor) para ranking
    # Usando MEDIANA no lugar da MÉDIA para o score
    stats["score_latencia"] = 1 / stats["median"]
    stats["score_estabilidade"] = 1 / (stats["std"] + 1) # evitar div por zero
    
    # Normalizar
    stats["score_latencia"] = stats["score_latencia"] / stats["score_latencia"].max()
    stats["score_estabilidade"] = stats["score_estabilidade"] / stats["score_estabilidade"].max()
    
    # Score Final (Peso: 70% Latência(Mediana), 30% Estabilidade)
    # Aumentei peso da latência pois mediana já é estável
    stats["score_final"] = (stats["score_latencia"] * 0.7 + stats["score_estabilidade"] * 0.3) * 100
    
    # Ordenar por Score Final
    ranking = stats.sort_values("score_final", ascending=False).reset_index(drop=True)
    
    top3 = ranking.head(3).to_dict('records')
    
    kpis = {
        "melhor_dns_nome": top3[0]["dns"],
        "melhor_dns_valor": f"{top3[0]['median']:.1f}", # Exibindo Mediana no KPI principal
        "total_reqs": len(df),
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "top3": top3
    }
    return kpis, ranking


def gerar_html_completo(kpis, ranking_df, plot1, plot2, plot3):
    # Gerar linhas da tabela de Top 3
    top3_html = ""
    medalhas = ["🥇", "🥈", "🥉"]
    classes = ["gold", "silver", "bronze"]
    
    for i, row in enumerate(kpis['top3']):
        score = f"{row['score_final']:.1f}"
        top3_html += f"""
        <div class="card rank-card {classes[i]}">
            <div class="medal">{medalhas[i]}</div>
            <h3>{row['dns']}</h3>
            <div class="score-badge">Score: {score}</div>
            <div class="details">
                <div>Mediana: <strong>{row['median']:.1f}ms</strong></div>
                <div>Estabilidade: <strong>±{row['std']:.1f}ms</strong></div>
            </div>
            <div style="font-size: 0.8rem; color: #555; margin-top: 5px;">(Média: {row['mean']:.1f}ms)</div>
        </div>
        """

    # Gerar Tabela Completa
    tabela_html = ranking_df[['dns', 'median', 'mean', 'std', 'min', 'max', 'score_final']].round(2).to_html(classes="styled-table", index=False)
    
    css = """
    :root {
        --bg-color: #0d1117;
        --card-bg: #161b22;
        --text-msg: #c9d1d9;
        --text-title: #f0f6fc;
        --accent: #58a6ff;
        --border: #30363d;
        --gold: #ffd700;
        --silver: #c0c0c0;
        --bronze: #cd7f32;
    }
    body {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-msg);
        margin: 0;
        padding: 20px;
    }
    .container { max_width: 1400px; margin: 0 auto; } /* Aumentei largura para caber graficos lado a lado */
    
    header { text-align: center; margin-bottom: 40px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
    h1 { color: var(--text-title); margin: 0; }
    h2 { color: var(--accent); margin-top: 40px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
    
    /* Top 3 Cards */
    .top3-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }
    .rank-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .rank-card.gold { border-color: var(--gold); box-shadow: 0 0 15px rgba(255, 215, 0, 0.1); }
    .rank-card.silver { border-color: var(--silver); }
    .rank-card.bronze { border-color: var(--bronze); }
    
    .medal { font-size: 3rem; margin-bottom: 10px; }
    .rank-card h3 { font-size: 1.5rem; color: var(--text-title); margin: 10px 0; }
    .score-badge { 
        background: rgba(88, 166, 255, 0.1); color: var(--accent); 
        padding: 5px 10px; border-radius: 20px; display: inline-block; font-weight: bold; margin-bottom: 15px;
    }
    .details { display: flex; justify-content: space-around; font-size: 0.9rem; color: #8b949e; }
    
    /* Charts */
    .chart-box { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 10px; margin-bottom: 20px; }
    
    /* Table */
    .table-container { overflow-x: auto; }
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem;
    }
    .styled-table thead tr { background-color: #21262d; color: var(--text-title); text-align: left; }
    .styled-table th, .styled-table td { padding: 12px 15px; border-bottom: 1px solid var(--border); }
    .styled-table tbody tr:hover { background-color: #21262d; }
    
    footer { text-align: center; margin-top: 50px; font-size: 0.8rem; color: #484f58; }
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Linkfort Analytics 2.0</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Linkfort Analytics</h1>
                <p>Monitoramento Inteligente de DNS</p>
                <small>Atualizado em: {kpis['atualizado_em']}</small>
            </header>
            
            <h2>🏆 Top 3 Melhores DNS (Por Mediana)</h2>
            <div class="top3-grid">
                {top3_html}
            </div>
            
            <h2>📈 Análise Temporal (Por Domínio)</h2>
            <div class="chart-box">{plot1}</div>
            
            <h2>📊 Comparativo de Performance</h2>
            <div class="top3-grid"> 
                 <div class="chart-box" style="margin:0;">{plot2}</div>
                 <div class="chart-box" style="margin:0;">{plot3}</div>
            </div>
            
            <h2>📋 Ranking Detalhado</h2>
            <div class="table-container">
                {tabela_html}
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

    print(">>> Calculando Score e Top 3...")
    kpis, ranking = calcular_metricas_avancadas(df)
    
    print(">>> Gerando gráficos...")
    plot1, plot2, plot3 = gerar_graficos(df)
    
    print(">>> Montando HTML...")
    html_content = gerar_html_completo(kpis, ranking, plot1, plot2, plot3)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ Dashboard gerado com sucesso em: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
