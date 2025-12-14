import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import sys
import datetime

# --- CONFIGURAÇÃO VISUAL ---
# Definindo cores e estilos globais
THEME = {
    'bg': '#0f172a',        # Slate 900
    'card': '#1e293b',      # Slate 800
    'text': '#f8fafc',      # Slate 50
    'accent': '#38bdf8',    # Sky 400
    'success': '#4ade80',   # Green 400
    'danger': '#f87171',    # Red 400
    'border': '#334155'     # Slate 700
}

INPUT_FILE = "dados_dns_linkfort.csv"
OUTPUT_HTML = "dashboard.html"

# Configurar Plotly para Dark Mode por padrão
pio.templates.default = "plotly_dark"

def load_data():
    try:
        df = pd.read_csv(INPUT_FILE, header=None, names=["timestamp","dns_name","dns_ip","domain","latency_ms","status"])
        df = df[df['timestamp'] != 'timestamp'] # Remove header duplicado se existir
        df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce')
        df = df.dropna(subset=['latency_ms'])
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo '{INPUT_FILE}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler dados: {e}")
        sys.exit(1)

def calculate_metrics(df):
    results = []
    # Agrupa por DNS
    grouped = df.groupby(['dns_name', 'dns_ip'])
    
    for (name, ip), group in grouped:
        total_reqs = len(group)
        success_df = group[group['status'] == 'OK']
        
        if len(success_df) == 0:
            p95, median, cv = 9999, 9999, 0
        else:
            latencies = success_df['latency_ms']
            p95 = np.percentile(latencies, 95)
            median = np.median(latencies)
            mean = np.mean(latencies)
            std = np.std(latencies)
            cv = (std / mean) * 100 if mean > 0 else 0
            
        failed = len(group[group['status'] != 'OK'])
        error_rate = (failed / total_reqs) * 100
        
        # Scoring V3.0
        def lat_to_score(ms):
            return max(0, 100 - (ms / 2))
            
        score_base = (lat_to_score(p95) * 0.5) + (lat_to_score(median) * 0.5)
        
        if error_rate > 5:
            final_score = 0
        elif error_rate > 1:
            final_score = score_base * 0.5
        else:
            final_score = score_base
            
        results.append({
            'DNS Name': name,
            'IP': ip,
            'P95 (ms)': round(p95, 2),
            'Median (ms)': round(median, 2),
            'CV (%)': round(cv, 1),
            'Error (%)': round(error_rate, 1),
            'Score': round(final_score, 1)
        })
        
    return pd.DataFrame(results).sort_values(by='Score', ascending=False)

def build_html_template(metrics_html, chart1_html, chart2_html, top_dns):
    """
    Constrói um HTML moderno e responsivo com CSS injetado.
    """
    
    generated_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    ranking_cards = ""
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (_, row) in enumerate(top_dns.iterrows()):
        if i >= 3: break
        medal = medals[i]
        score_color = THEME['success'] if row['Score'] > 80 else THEME['accent'] if row['Score'] > 50 else THEME['danger']
        
        ranking_cards += f"""
        <div class="card winner-card">
            <div class="medal">{medal}</div>
            <h3>{row['DNS Name']}</h3>
            <p class="ip">{row['IP']}</p>
            <div class="score-badge" style="background: {score_color}">Score: {row['Score']}</div>
            <div class="stats-grid">
                <div><span>Median</span><br><strong>{row['Median (ms)']}ms</strong></div>
                <div><span>P95</span><br><strong>{row['P95 (ms)']}ms</strong></div>
            </div>
        </div>
        """

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        :root {{
            --bg-color: {THEME['bg']};
            --card-bg: {THEME['card']};
            --text-color: {THEME['text']};
            --accent-color: {THEME['accent']};
            --border-color: {THEME['border']};
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max_width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 0;
            background: linear-gradient(180deg, rgba(30,41,59,0) 0%, rgba(30,41,59,0.5) 100%);
            border-bottom: 1px solid var(--border-color);
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin: 0;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .subtitle {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        
        /* Cards */
        .winners-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .card {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            border-color: var(--accent-color);
        }}
        
        .medal {{ font-size: 3rem; margin-bottom: 10px; }}
        
        h3 {{ margin: 10px 0; font-size: 1.5rem; }}
        
        .ip {{ font-family: 'JetBrains Mono', monospace; color: #94a3b8; background: #0f172a; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
        
        .score-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            font-weight: bold;
            color: #000;
            margin: 15px 0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
            border-top: 1px solid var(--border-color);
            padding-top: 15px;
            font-size: 0.9rem;
        }}
        
        /* Table */
        .table-container {{
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            margin-bottom: 40px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background: #0f172a;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
        }}
        
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: rgba(56, 189, 248, 0.05); }}
        
        /* Charts */
        .chart-container {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        footer {{
            text-align: center;
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 60px;
            padding-bottom: 20px;
        }}
    </style>
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Linkfort DNS Intelligence</title>
        {css}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Linkfort DNS Intelligence</h1>
                <div class="subtitle">Relatório de Performance de Rede • Gerado em {generated_at}</div>
            </header>
            
            <section class="winners-section">
                {ranking_cards}
            </section>
            
            <section class="table-container">
                {metrics_html}
            </section>
            
            <section class="charts-grid">
                <div class="chart-container">
                    {chart1_html}
                </div>
                <div class="chart-container">
                    {chart2_html}
                </div>
            </section>
            
            <footer>
                Linkfort V3.1 • Powered by Python & Plotly • Developed by Antigravity
            </footer>
        </div>
    </body>
    </html>
    """
    return html

def generate_report(metrics_df, raw_df):
    
    # 1. Gráficos Plotly customizados
    fig_bar = px.bar(metrics_df, x='DNS Name', y='Score', color='Score', 
                     title="Ranking de Performance (Score V3.0)", text='Score',
                     color_continuous_scale='Viridis')
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Inter")
    
    fig_box = px.box(raw_df[raw_df['status']=='OK'], x='dns_name', y='latency_ms', 
                     title="Estabilidade de Latência (Menor é melhor)", points="all",
                     color='dns_name')
    fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Inter", showlegend=False)

    # 2. Gerar HTML dos componentes
    # Tabela HTML limpa (sem classes do pandas)
    table_html = metrics_html = metrics_df.to_html(index=False, border=0, classes="")
    
    chart1 = fig_bar.to_html(full_html=False, include_plotlyjs='cdn')
    chart2 = fig_box.to_html(full_html=False, include_plotlyjs='cdn')
    
    # 3. Montar página completa
    full_html = build_html_template(table_html, chart1, chart2, metrics_df.head(3))
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print("\n" + "="*40)
    print(f"✨ Dashboard Premium gerado: {OUTPUT_HTML}")
    print("="*40)

def main():
    df = load_data()
    if df.empty:
        print("Nenhum dado encontrado no CSV. Execute a coleta primeiro.")
        return

    metrics = calculate_metrics(df)
    generate_report(metrics, df)

if __name__ == "__main__":
    main()
