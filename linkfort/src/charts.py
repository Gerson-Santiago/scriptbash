import plotly.express as px
import plotly.io as pio
import json

# Configure Plotly for Dark Mode by default
pio.templates.default = "plotly_dark"

def generate_charts(metrics_df, raw_df):
    # 1. Bar Chart - Ranking
    fig_bar = px.bar(metrics_df, x='DNS Name', y='Score', color='Score', 
                     title="Ranking de Performance (Score V3.0)", text='Score',
                     color_continuous_scale='Viridis')
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Inter")
    
    # 2. Box Plot - Latency Stability
    fig_box = px.box(raw_df[raw_df['status']=='OK'], x='dns_name', y='latency_ms', 
                     title="Estabilidade de Latência (Menor é melhor)", points="all",
                     color='dns_name')
    fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Inter", showlegend=False)

    # 3. Scatter Plot - Timeline
    fig_scatter = px.scatter(raw_df[raw_df['status']=='OK'], x='timestamp', y='latency_ms', color='dns_name',
                             title="Latência ao Longo do Tempo (Timeline)",
                             labels={'timestamp': 'Tempo', 'latency_ms': 'Latência (ms)'})
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Inter")

    return {
        'bar': json.loads(fig_bar.to_json()),
        'box': json.loads(fig_box.to_json()),
        'scatter': json.loads(fig_scatter.to_json())
    }
