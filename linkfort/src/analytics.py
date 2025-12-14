import pandas as pd
import numpy as np

def calculate_metrics(df):
    results = []
    # Group by DNS
    grouped = df.groupby(['dns_name', 'dns_ip'])
    
    for (name, ip), group in grouped:
        total_reqs = len(group)
        success_df = group[group['status'] == 'OK']
        
        if len(success_df) == 0:
            p95, median, cv = 9999, 9999, 0
            mean = 9999
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
        if error_rate > 25:
            final_score = 0
        elif error_rate > 10:
            final_score = score_base * 0.5
        else:
            final_score = score_base
            
        results.append({
            'DNS Name': name,
            'IP': ip,
            'Requests': total_reqs,
            'P95 (ms)': round(p95, 2),
            'Mean (ms)': round(mean, 2),
            'Median (ms)': round(median, 2),
            'CV (%)': round(cv, 1),
            'Error (%)': round(error_rate, 1),
            'Score': round(final_score, 1)
        })
        
    return pd.DataFrame(results).sort_values(by='Score', ascending=False)

def calculate_domain_winners(df):
    """
    Identifies the best DNS for each tested domain (based on median).
    """
    domain_winners = []
    
    # Filter only successes
    success_df = df[df['status'] == 'OK']
    domains = success_df['domain'].unique()
    
    for domain in domains:
        domain_df = success_df[success_df['domain'] == domain]
        
        # Calculate median per DNS for this domain
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

def calculate_global_stats(raw_df):
    total_requests = len(raw_df)
    success_requests = len(raw_df[raw_df['status'] == 'OK'])
    success_rate = round((success_requests / total_requests) * 100, 1) if total_requests > 0 else 0
    avg_latency = round(raw_df[raw_df['status'] == 'OK']['latency_ms'].mean(), 1) if success_requests > 0 else 0
    
    return {
        'total_requests': total_requests,
        'success_rate': success_rate,
        'avg_latency': avg_latency
    }
