#!/usr/bin/env python3
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime

# ==========================================================
# CONFIGURAÇÕES & CONSTANTES
# ==========================================================
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "dados_dns_linkfort.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_HTML = OUTPUT_DIR / "dashboard.html"
OUTPUT_DIR.mkdir(exist_ok=True)

# Cores para gráficos
TEMPLATE_THEME = "plotly_dark"

# ==========================================================
# CAMADA DE DADOS & PERFORMANCE (Analytics 3.0)
# ==========================================================
def carregar_dados():
    if not CSV_FILE.exists():
        print(f"⚠️ AVISO: {CSV_FILE} não encontrado. Aguardando coleta.")
        return None

    try:
        # Otimização 1: Ler 'timeout' como NaN logo na leitura
        df = pd.read_csv(CSV_FILE, na_values=['timeout'])
        
        # Otimização 2: Tipagem eficiente
        df["data_hora"] = pd.to_datetime(df["data_hora"])
        df["tempo_ms"] = pd.to_numeric(df["tempo_ms"], errors='coerce')
        
        # Otimização 3: Variáveis categóricas (Economia de RAM para Big Data)
        df["dns"] = df["dns"].astype("category")
        df["dominio"] = df["dominio"].astype("category")
        df["req"] = df["req"].astype("category")

        return df
    except Exception as e:
        print(f"❌ ERRO GRAVE ao ler CSV: {e}")
        return None

# ==========================================================
# CAMADA DE CIÊNCIA DE DADOS (KPIs Avançados)
# ==========================================================
def calcular_percentil95(x):
    return np.percentile(x.dropna(), 95)

def calcular_cv(x):
    # Coeficiente de Variação = (Desvio Padrão / Média)
    media = x.mean()
    if media == 0: return 0
    return (x.std() / media)

def calcular_metricas_avancadas(df):
    # 1. Disponibilidade (Antes de dropar NaNs)
    # Total de requisições por DNS
    total_reqs = df.groupby("dns", observed=True)["tempo_ms"].size()
    # Total de sucessos (não nulos)
    sucessos = df.groupby("dns", observed=True)["tempo_ms"].count()
    # Taxa de Erro (%)
    taxa_erro = (1 - (sucessos / total_reqs)) * 100
    
    # 2. Filtrar apenas sucessos para latência
    df_clean = df.dropna(subset=["tempo_ms"])
    
    # 3. Calcular Estatísticas Robustas
    stats = df_clean.groupby("dns", observed=True)["tempo_ms"].agg([
        "mean",     # Média (Tradicional)
        "median",   # Mediana (Anti-Jitter)
        "std",      # Desvio Padrão
        "min", 
        "max",
        calcular_percentil95 # P95 (SLA - 95% das reqs foram abaixo disso)
    ]).rename(columns={"calcular_percentil95": "p95"})
    
    # Adicionar taxa de erro ao dataframe de stats
    stats["taxa_erro"] = taxa_erro
    
    # Calcular CV (Coeficiente de Variação) - Estabilidade Relativa
    # CV = Desvio / Média. Quanto menor, mais consistente.
    stats["cv"] = stats["std"] / stats["mean"]
    
    # -------------------------------------------------------
    # ALGORITMO DE SCORING FINAL (Analytics 3.0)
    # -------------------------------------------------------
    # Critérios:
    # 1. Disponibilidade é VITAL (Penalidade brutal por timeout)
    # 2. P95 é rei (Garante consistência mesmo nos piores 5%)
    # 3. Mediana é rainha (Performance típica)
    
    # Inverter latências (menor é melhor)
    score_p95 = 1 / (stats["p95"] + 1)
    score_mediana = 1 / (stats["median"] + 1)
    
    # Penalidade de disponibilidade (Taxa de Erro > 1% destrói o score)
    # Fator de viabilidade: Se erro > 5%, score cai pra zero
    fator_disponibilidade = np.where(stats["taxa_erro"] > 5, 0.1, 
                                     np.where(stats["taxa_erro"] > 1, 0.5, 1.0))

    # Normalizar scores base (0 a 100)
    score_p95_norm = (score_p95 / score_p95.max()) * 100
    score_mediana_norm = (score_mediana / score_mediana.max()) * 100
    
    # Score Composto: 50% P95 + 50% Mediana (ponderado pela disponibilidade)
    # Garantir que NaN scores virem 0
    stats["score_final"] = ((score_p95_norm * 0.5 + score_mediana_norm * 0.5) * fator_disponibilidade).fillna(0)
    
    # Ordenar
    ranking = stats.sort_values("score_final", ascending=False).reset_index()
    
    top3 = ranking.head(3).to_dict('records')
    
    kpis = {
        "campeao_nome": top3[0]["dns"] if top3 else "N/A",
        "campeao_p95": f"{top3[0]['p95']:.1f}" if top3 else "0.0",
        "campeao_erro": f"{top3[0]['taxa_erro']:.1f}%" if top3 else "0%",
        "total_amostras": len(df),
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "top3": top3
    }
    
    return kpis, ranking

# ==========================================================
# CAMADA DE VISUALIZAÇÃO (Gráficos Profissionais)
# ==========================================================
def gerar_graficos(df):
    df_clean = df.dropna(subset=["tempo_ms"])
    
    if df_clean.empty:
        return "<div>Sem dados</div>", "<div>Sem dados</div>", "<div>Sem dados</div>"
    
    # Ordem inteligente dos DNS (do melhor para pior mediana geral)
    ordem_dns = df_clean.groupby("dns", observed=True)["tempo_ms"].median().sort_values().index.tolist()

    # Gráfico 1: Timeline Faceteada (Visão Detalhada por Domínio)
    fig_timeline = px.line(df_clean, x="data_hora", y="tempo_ms", color="dns", 
                           title="Latência ao Longo do Tempo (Por Domínio)",
                           facet_col="dominio", facet_col_wrap=2,
                           labels={"tempo_ms": "Latência (ms)", "data_hora": "Horário"},
                           category_orders={"dns": ordem_dns},
                           template=TEMPLATE_THEME, height=600)
    fig_timeline.update_layout(hovermode="x unified", margin=dict(t=60, b=60))

    # Gráfico 2: Boxplot com Pontos (Mostra a verdade nua e crua)
    fig_hist = px.box(df_clean, x="dns", y="tempo_ms", color="dns",
                      title="Distribuição Real de Performance (Boxplot)",
                      labels={"tempo_ms": "Latência (ms)", "dns": "DNS"},
                      category_orders={"dns": ordem_dns},
                      template=TEMPLATE_THEME)
    fig_hist.update_layout(showlegend=False)

    # Gráfico 3: Comparativo de P95 (O "Pior Caso" Típico)
    # Precisamos recalcular P95 por dominio e dns para plotar
    p95_por_dominio = df_clean.groupby(["dns", "dominio"], observed=True)["tempo_ms"].agg(
        p95=lambda x: np.percentile(x, 95)
    ).reset_index()
    
    fig_bar = px.bar(p95_por_dominio, x="dns", y="p95", color="dominio", barmode="group",
                     title="P95: O 'Pior Caso Típico' (Menor é Melhor - SLA)",
                     labels={"p95": "Latência P95 (ms)", "dns": "DNS"},
                     category_orders={"dns": ordem_dns},
                     template=TEMPLATE_THEME)

    return fig_timeline.to_html(full_html=False, include_plotlyjs='cdn'), \
           fig_hist.to_html(full_html=False, include_plotlyjs=False), \
           fig_bar.to_html(full_html=False, include_plotlyjs=False)

def gerar_html_completo(kpis, ranking_df, plot1, plot2, plot3):
    medalhas = ["🥇", "🥈", "🥉"]
    classes = ["gold", "silver", "bronze"]
    top3_html = ""
    
    if kpis['top3']:
        for i, row in enumerate(kpis['top3']):
            rank_class = classes[i] if i < 3 else ""
            medalha = medalhas[i] if i < 3 else ""
            
            err_style = "color: #ff5555" if row['taxa_erro'] > 0 else "color: #50fa7b"
            
            top3_html += f"""
            <div class="card rank-card {rank_class}">
                <div class="medal">{medalha}</div>
                <h3>{row['dns']}</h3>
                <div class="score-badge">Score: {row['score_final']:.0f}</div>
                
                <div class="main-stat">
                    <span class="label">P95 (SLA)</span>
                    <span class="value">{row['p95']:.1f}ms</span>
                </div>
                
                <div class="grid-stats">
                    <div>Mediana<br><strong>{row['median']:.1f}ms</strong></div>
                    <div>Estabilidade (CV)<br><strong>{row['cv']:.2f}</strong></div>
                    <div style="{err_style}">Falhas<br><strong>{row['taxa_erro']:.1f}%</strong></div>
                </div>
            </div>
            """
    else:
        top3_html = "<p>Sem dados suficientes para ranking.</p>"

    tabela_html = ranking_df[['dns', 'p95', 'median', 'mean', 'std', 'cv', 'taxa_erro', 'score_final']].round(2).to_html(classes="styled-table", index=False)
    
    # CSS Moderno Cyberpunk/Clean
    css = """
    :root { --bg: #0d1117; --card: #161b22; --text: #c9d1d9; --accent: #58a6ff; --border: #30363d; --gold: #ffd700; --silver: #c0c0c0; --bronze: #cd7f32; }
    body { font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
    .container { max_width: 1400px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 50px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
    h1 { font-size: 2.5rem; margin: 0; background: linear-gradient(90deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    .top3-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 50px; }
    .rank-card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; text-align: center; position: relative; transition: transform 0.2s; }
    .rank-card:hover { transform: translateY(-5px); }
    .rank-card.gold { border: 2px solid var(--gold); box-shadow: 0 0 20px rgba(255,215,0,0.1); }
    .rank-card.silver { border: 2px solid var(--silver); }
    .rank-card.bronze { border: 2px solid var(--bronze); }
    
    .medal { font-size: 3rem; margin-bottom: 10px; }
    h3 { font-size: 1.4rem; color: #fff; margin: 10px 0; }
    .score-badge { background: #21262d; padding: 4px 12px; border-radius: 12px; font-weight: bold; color: var(--accent); display: inline-block; margin-bottom: 15px; }
    
    .main-stat { font-size: 1.5rem; font-weight: bold; margin: 15px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 10px 0; }
    .main-stat .label { display: block; font-size: 0.8rem; text-transform: uppercase; color: #8b949e; letter-spacing: 1px; }
    
    .grid-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 0.9rem; color: #8b949e; }
    .grid-stats strong { color: var(--text); font-size: 1.1rem; display: block; margin-top: 4px; }
    
    .chart-box { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 15px; margin-bottom: 30px; }
    
    .table-container { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); }
    .styled-table { width: 100%; border-collapse: collapse; min-width: 800px; }
    .styled-table th { background: #21262d; padding: 15px; text-align: left; color: #fff; }
    .styled-table td { padding: 12px 15px; border-bottom: 1px solid var(--border); }
    .styled-table tr:last-child td { border-bottom: none; }
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Linkfort Analytics 3.0</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>LINKFORT ANALYTICS 3.0</h1>
                <p>Data Science & Network Intelligence</p>
                <small>Última atualização: {kpis['atualizado_em']} • {kpis['total_amostras']} amostras</small>
            </header>
            
            <h2 style="text-align:center; margin-bottom: 30px;">🏆 Performance Elite (Top 3)</h2>
            <div class="top3-grid">
                {top3_html}
            </div>
            
            <h2>🔬 Análise Profunda</h2>
            <div class="chart-box">{plot1}</div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                <div class="chart-box" style="margin:0">{plot3}</div>
                <div class="chart-box" style="margin:0">{plot2}</div>
            </div>
            <br><br>
            
            <h2>📋 Ranking Completo (Métricas Avançadas)</h2>
            <div class="table-container">
                {tabela_html}
            </div>
            
            <footer style="text-align: center; margin-top: 50px; color: #666;">
                Gerado pelo Linkfort Analytics Engine 3.0
            </footer>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print(">>> [Analytics 3.0] Carregando Dataframe...")
    df = carregar_dados()
    if df is None:
        return

    if df.empty:
        print(">>> AVISO: CSV vazio. Execute uma coleta primeiro.")
        return

    print(">>> [Analytics 3.0] Calculando KPIs Avançados (P95, CV, Availability)...")
    kpis, ranking = calcular_metricas_avancadas(df)
    
    print(">>> [Analytics 3.0] Renderizando Gráficos Plotly...")
    plot1, plot2, plot3 = gerar_graficos(df)
    
    print(">>> [Analytics 3.0] Compilando Dashboard HTML...")
    html_content = gerar_html_completo(kpis, ranking, plot1, plot2, plot3)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ Dashboard Analytics 3.0 gerado com sucesso: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
