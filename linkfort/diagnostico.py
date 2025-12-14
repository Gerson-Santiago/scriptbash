
import pandas as pd
from pathlib import Path

CSV_FILE = Path("dados_dns_linkfort.csv")

def diagnosticar():
    if not CSV_FILE.exists():
        print("CSV não encontrado.")
        return

    print(">>> Carregando CSV...")
    # Ler tudo como string primeiro para ver o que tem de sujeira
    df_raw = pd.read_csv(CSV_FILE)
    
    print(f"Total de linhas: {len(df_raw)}")
    
    # 1. Checar Timeouts ou Erros de Leitura
    # Converter tempo_ms para numérico, erros viram NaN
    df_raw['tempo_numerico'] = pd.to_numeric(df_raw['tempo_ms'], errors='coerce')
    
    falhas = df_raw[df_raw['tempo_numerico'].isna()]
    taxa_falha = len(falhas) / len(df_raw) * 100
    
    print(f"\n[INTEGRIDADE]")
    print(f"Timeouts/Erros de Parse: {len(falhas)} ({taxa_falha:.2f}%)")
    if len(falhas) > 0:
        print("Exemplos de falha:")
        print(falhas['tempo_ms'].unique()[:5])
        
        # Quem falha mais?
        piores = falhas['dns'].value_counts().head(3)
        print("\nDNS com mais falhas:")
        print(piores)

    # 2. Analisar Dados Válidos
    df = df_raw.dropna(subset=['tempo_numerico']).copy()
    
    print(f"\n[ESTATÍSTICAS POR DNS]")
    stats = df.groupby('dns')['tempo_numerico'].agg(['count', 'min', 'mean', 'median', 'std', 'max'])
    print(stats.round(1))
    
    # 3. Detectar "Cache Local" (Tempos suspeitosamente baixos, ex: 0ms ou 1ms constatemente)
    print("\n[SUSPEITA DE CACHE (Respostas < 2ms)]")
    suspeitos = df[df['tempo_numerico'] < 2]
    if not suspeitos.empty:
        print(f"Total de respostas < 2ms: {len(suspeitos)}")
        print(suspeitos.groupby('dns').size())
    else:
        print("Nenhuma resposta < 2ms detectada (Indica que o dig está indo para a rede real).")

    # 4. Análise Específica Linkfort
    print("\n[DIAGNÓSTICO LINKFORT (138.97...)]")
    linkfort = df[df['dns'].str.contains("138.97")]
    if linkfort.empty:
        print("Nenhum DNS Linkfort encontrado nos dados.")
    else:
        print(f"Amostras Linkfort: {len(linkfort)}")
        print(f"Média: {linkfort['tempo_numerico'].mean():.1f}ms")
        print(f"Mediana: {linkfort['tempo_numerico'].median():.1f}ms")
        print(f"Desvio Padrão: {linkfort['tempo_numerico'].std():.1f}ms")
        print("Distribuição (Describe):")
        print(linkfort['tempo_numerico'].describe().round(1))

if __name__ == "__main__":
    diagnosticar()
