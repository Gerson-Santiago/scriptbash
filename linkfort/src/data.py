import pandas as pd
import sys
from .config import INPUT_FILE

def load_data():
    try:
        df = pd.read_csv(INPUT_FILE, header=None, names=["timestamp","dns_name","dns_ip","domain","latency_ms","status"])
        df = df[df['timestamp'] != 'timestamp'] # Remove duplicate header if exists
        df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce')
        df = df.dropna(subset=['latency_ms'])
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo '{INPUT_FILE}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler dados: {e}")
        sys.exit(1)
