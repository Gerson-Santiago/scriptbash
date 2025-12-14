from src.data import load_data
from src.analytics import calculate_metrics, calculate_domain_winners, calculate_global_stats
from src.charts import generate_charts
from src.exporter import export_to_json

def main():
    # 1. Load Data
    df = load_data()
    if df.empty:
        # Generate Skeleton JSON to prevent 404 on frontend
        empty_stats = {'total_requests': 0, 'success_rate': 0, 'avg_latency': 0}
        export_to_json(df, df, empty_stats, {}, None)
        print("⚠️  Nenhum dado ainda. JSON de esqueleto criado.")
        return

    # 2. Analytics
    metrics = calculate_metrics(df)
    domain_winners = calculate_domain_winners(df)
    global_stats = calculate_global_stats(df)
    
    # 3. Charts
    charts = generate_charts(metrics, df)
    
    # 4. Export
    export_to_json(metrics, df, global_stats, charts, domain_winners)

if __name__ == "__main__":
    main()
