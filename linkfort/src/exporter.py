import json
import datetime
from .config import JSON_OUTPUT_FILE

def export_to_json(metrics_df, raw_df, global_stats, charts=None, domain_winners_df=None):
    """
    Exports processed data and chart configurations to dados.json.
    """
    ranking_data = metrics_df.to_dict(orient='records')
    
    # Simplified History
    history_df = raw_df[['timestamp', 'dns_name', 'latency_ms', 'status']].copy()
    history_df['timestamp'] = history_df['timestamp'].astype(str)
    history_data = history_df.to_dict(orient='records')
    
    # Domain Winners
    domain_winners_data = []
    if domain_winners_df is not None:
         domain_winners_data = domain_winners_df.to_dict(orient='records')

    data = {
        "metadata": {
            "generated_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_requests": global_stats['total_requests'],
            "success_rate": global_stats['success_rate'],
            "avg_latency": global_stats['avg_latency']
        },
        "ranking": ranking_data,
        "domain_winners": domain_winners_data,
        "charts": charts if charts else {},
        "history": history_data
    }
    
    try:
        with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✨ Dados atualizados em: {JSON_OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Erro ao exportar JSON: {e}")
