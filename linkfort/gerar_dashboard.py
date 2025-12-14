import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys

INPUT_FILE = "dados_dns_linkfort.csv"
OUTPUT_HTML = "dashboard.html"

def load_data():
    try:
        # Lê o CSV. Assumindo que pode não ter header ou ter header misto.
        # Forçamos os nomes das colunas para evitar erros.
        df = pd.read_csv(INPUT_FILE, header=None, names=["timestamp","dns_name","dns_ip","domain","latency_ms","status"])
        
        # Se a primeira linha for o header duplicado, removemos
        df = df[df['timestamp'] != 'timestamp']
        
        # Converte latency_ms para numérico (erros viram NaN)
        df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce')
        
        # Remove linhas com falha de parse
        df = df.dropna(subset=['latency_ms'])
        
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo '{INPUT_FILE}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler dados: {e}")
        sys.exit(1)

def calculate_metrics(df):
    """
    Calcula P95, Mediana e Score conforme FLUXO_TECNICO.md
    """
    results = []
    
    # Agrupa por DNS
    grouped = df.groupby(['dns_name', 'dns_ip'])
    
    for (name, ip), group in grouped:
        total_reqs = len(group)
        # Consideramos ERRO se status != OK ou latency > 1000 (exemplo)
        # No script bash, TIMEOUT gera latency 0 ou vazio?
        # O script bash escreve "0" e status "TIMEOUT".
        
        # Filtrar sucessos para métricas de tempo
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
            
        # Taxa de Erro
        failed = len(group[group['status'] != 'OK'])
        error_rate = (failed / total_reqs) * 100
        
        # Score System v3.0 logic roughly:
        # Lower is better. We want a Score 0-100 where 100 is best.
        # But let's follow the implementation plan's "Ranking" logic.
        # Impl Plan says: P95 (50%), Median (50%), Penalty for Errors.
        
        # Normalization (heuristic):
        # 0ms = 100 pts
        # 100ms = 50 pts
        # 200ms+ = 0 pts
        
        def lat_to_score(ms):
            return max(0, 100 - (ms / 2)) # 1ms = 99.5, 20ms = 90
            
        score_p95 = lat_to_score(p95)
        score_median = lat_to_score(median)
        
        # Base Score
        final_score = (score_p95 * 0.5) + (score_median * 0.5)
        
        # Availability Penalty
        if error_rate > 5:
            final_score = 0
        elif error_rate > 1:
            final_score = final_score * 0.5
            
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

def generate_report(metrics_df, raw_df):
    print("\n--- RELATÓRIO DE ANÁLISE (Ranking V3.0) ---")
    print(metrics_df.to_string(index=False))
    
    top2 = metrics_df.head(2)
    print("\n[CONCLUSÃO] Os Top 2 DNS Recomendados:")
    for i, row in top2.iterrows():
        print(f"{i+1}. {row['DNS Name']} ({row['IP']}) - Score: {row['Score']}")

    # Plotly Charts
    fig_bar = px.bar(metrics_df, x='DNS Name', y='Score', color='Score', 
                     title="DNS Ranking Score (V3.0)", text='Score')
    
    fig_box = px.box(raw_df[raw_df['status']=='OK'], x='dns_name', y='latency_ms', 
                     title="Distribuição de Latência (Boxplot)", points="all")
    
    # Save HTML
    with open(OUTPUT_HTML, 'w') as f:
        f.write("<html><head><title>Linkfort DNS Dashboard</title></head><body>")
        f.write("<h1>Linkfort DNS Benchmark Results</h1>")
        f.write("<h2>Ranking Table</h2>")
        f.write(metrics_df.to_html())
        f.write("<h2>Graphs</h2>")
        f.write(fig_bar.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig_box.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("</body></html>")
    
    print(f"\nDashboard salvo em: {OUTPUT_HTML}")

def main():
    df = load_data()
    if df.empty:
        print("Nenhum dado encontrado no CSV.")
        return

    metrics = calculate_metrics(df)
    generate_report(metrics, df)

if __name__ == "__main__":
    main()
