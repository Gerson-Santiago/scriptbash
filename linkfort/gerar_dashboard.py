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
    'border': '#334155',    # Slate 700
    'subtle': '#64748b'     # Slate 500
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
        
        # Availability Penalty (V3.2 - Relaxed for Home Networks)
        # > 25% failures = Score 0 (Unusable)
        # > 10% failures = 50% Penalty
        if error_rate > 25:
            final_score = 0
        elif error_rate > 10:
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

def calculate_domain_winners(df):
    """
    Identifica o melhor DNS para cada domínio testado (baseado em mediana).
    """
    domain_winners = []
    
    # Filtra apenas sucessos
    success_df = df[df['status'] == 'OK']
    domains = success_df['domain'].unique()
    
    for domain in domains:
        domain_df = success_df[success_df['domain'] == domain]
        
        # Calcula mediana por DNS para este domínio
        grouped = domain_df.groupby(['dns_name', 'dns_ip'])['latency_ms'].median().reset_index()
        grouped = grouped.sort_values(by='latency_ms')
        
        if not grouped.empty:
            winner = grouped.iloc[0]
            domain_winners.append({
                'Domain': domain,
                'Best DNS': winner['dns_name'],
                'IP': winner['dns_ip'],
                'Median Latency': f"{winner['latency_ms']:.1f} ms"
            })
            
    return pd.DataFrame(domain_winners)

def build_html_template(metrics_html, domain_html, chart1_html, chart2_html, top_dns, all_domains):
    """
    Constrói um HTML moderno e responsivo com CSS injetado.
    """
    
    generated_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    domains_str = ", ".join(all_domains)
    
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
            --subtle-color: {THEME['subtle']};
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
        
        .live-indicator {{
            display: inline-block;
            background-color: rgba(220, 38, 38, 0.2);
            color: #ef4444;
            font-weight: bold;
            font-size: 0.8rem;
            padding: 4px 12px;
            border-radius: 999px;
            border: 1px solid #ef4444;
            margin-bottom: 10px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }}
            70% {{ opacity: 0.7; box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
            100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
        }}

        .subtitle {{
            color: var(--subtle-color);
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        
        .domains-list {{
            margin-top: 15px;
            font-size: 0.8rem;
            color: var(--accent-color);
            background: rgba(56, 189, 248, 0.1);
            padding: 8px 16px;
            border-radius: 999px;
            display: inline-block;
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
        
        .ip {{ font-family: 'JetBrains Mono', monospace; color: var(--subtle-color); background: #0f172a; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
        
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
        
        /* Section Titles */
        h2 {{
            border-left: 4px solid var(--accent-color);
            padding-left: 15px;
            margin-bottom: 20px;
            color: var(--text-color);
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
            color: var(--subtle-color);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
        }}
        
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: rgba(56, 189, 248, 0.05); }}
        
        /* Domain Grid */
        .domain-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 40px;
        }}
        
        .domain-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .domain-name {{ font-weight: bold; font-size: 1.1rem; color: var(--accent-color); }}
        .winner-name {{ font-size: 0.9rem; color: var(--text-color); margin-top: 4px; }}
        .winner-lat {{ font-size: 0.85rem; color: var(--success); font-family: 'JetBrains Mono', monospace; }}
        
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
            color: var(--subtle-color);
            font-size: 0.8rem;
            margin-top: 60px;
            padding-bottom: 20px;
        }}
    </style>
    """
    
    # Gerar HTML dos cards de domínio (alternativa à tabela)
    # Mas como o usuário pediu "listagem", também podemos usar a tabela.
    # Vamos usar tabela para manter consistência com o pedido.
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Linkfort DNS Intelligence</title>
        {css}
        <style>
            .live-controls {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .btn-live {{
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid var(--border-color);
                background: var(--card-bg);
                color: var(--text-color);
                font-family: inherit;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s;
            }}
            
            .btn-live:hover {{
                background: var(--border-color);
            }}
            
            .btn-live.active {{
                border-color: #ef4444;
                color: #ef4444;
                background: rgba(239, 68, 68, 0.1);
            }}

            .indicator-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #64748b;
            }}
            
            .btn-live.active .indicator-dot {{
                background-color: #ef4444;
                box-shadow: 0 0 10px #ef4444;
                animation: blink 1.5s infinite;
            }}
            
            @keyframes blink {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.4; }}
                100% {{ opacity: 1; }}
            }}
        </style>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                const toggleBtn = document.getElementById("liveToggle");
                const indicatorText = document.getElementById("statusText");
                const REFRESH_INTERVAL = 5000;
                let timer = null;
                
                // Verifica estado salvo
                let isLive = localStorage.getItem("linkfort_live_mode") === "true";
                
                function updateState() {{
                    if (isLive) {{
                        toggleBtn.classList.add("active");
                        indicatorText.textContent = "AO VIVO";
                        if (!timer) {{
                            timer = setInterval(() => window.location.reload(), REFRESH_INTERVAL);
                        }}
                    }} else {{
                        toggleBtn.classList.remove("active");
                        indicatorText.textContent = "PAUSADO";
                        if (timer) {{
                            clearInterval(timer);
                            timer = null;
                        }}
                    }}
                    localStorage.setItem("linkfort_live_mode", isLive);
                }}
                
                toggleBtn.addEventListener("click", () => {{
                    isLive = !isLive;
                    updateState();
                }});
                
                // Inicializa
                updateState();
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="live-controls">
                    <button id="liveToggle" class="btn-live">
                        <span class="indicator-dot"></span>
                        <span id="statusText">PAUSADO</span>
                    </button>
                    <!-- <div class="live-indicator">🔴 AO VIVO</div> -->
                </div>
                <h1>Linkfort DNS Intelligence</h1>
                <div class="subtitle">Relatório de Performance de Rede • Gerado em {generated_at}</div>
                <div class="domains-list">🌐 Testados: {domains_str}</div>
            </header>
            
            <section class="winners-section">
                {ranking_cards}
            </section>
            
            <h2>🏆 Campeões por Site</h2>
            <section class="table-container">
                {domain_html}
            </section>
            
            <h2>📊 Ranking Geral</h2>
            <section class="table-container">
                {metrics_html}
            </section>
            
            <h2>📈 Análise Visual</h2>
            <section class="charts-grid">
                <div class="chart-container">
                    {chart1_html}
                </div>
                <div class="chart-container">
                    {chart2_html}
                </div>
            </section>
            
            <footer>
                Linkfort V3.4 • Powered by Python & Plotly • Developed by Antigravity
            </footer>
        </div>
    </body>
    </html>
    """
    return html

def generate_report(metrics_df, domain_df, raw_df):
    
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
    table_metrics_html = metrics_df.to_html(index=False, border=0, classes="")
    table_domain_html = domain_df.to_html(index=False, border=0, classes="")
    
    chart1 = fig_bar.to_html(full_html=False, include_plotlyjs='cdn')
    chart2 = fig_box.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Lista de domínios
    all_domains = raw_df['domain'].sort_values().unique()
    
    # 3. Montar página completa
    full_html = build_html_template(table_metrics_html, table_domain_html, chart1, chart2, metrics_df.head(3), all_domains)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print("\n" + "="*40)
    print(f"✨ Dashboard Premium V3.3 gerado: {OUTPUT_HTML}")
    print("="*40)

def main():
    df = load_data()
    if df.empty:
        print("Nenhum dado encontrado no CSV. Execute a coleta primeiro.")
        return

    metrics = calculate_metrics(df)
    domain_winners = calculate_domain_winners(df)
    
    generate_report(metrics, domain_winners, df)

if __name__ == "__main__":
    main()
