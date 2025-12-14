#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
INPUT_CSV = BASE_DIR / "dados_dns_linkfort.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_SUMMARY = OUTPUT_DIR / "resumo_dns.csv"

# Ler CSV
df = pd.read_csv(INPUT_CSV, parse_dates=["data_hora"])

# Função para calcular delta (diferença máximo - mínimo)
def calcular_delta(tempos):
    return tempos.max() - tempos.min()

# Agrupar por DNS e Domínio
grouped = df.groupby(["dns", "dominio"])

summary = grouped["tempo_ms"].agg(
    qtd_reqs="count",
    media="mean",
    mediana="median",
    minimo="min",
    maximo="max",
    delta=calcular_delta
).reset_index()

# Arredondar para 2 casas decimais
summary[["media", "mediana", "delta"]] = summary[["media", "mediana", "delta"]].round(2)

# Salvar CSV resumido
summary.to_csv(OUTPUT_SUMMARY, index=False)

print(f"[OK] Resumo gerado: {OUTPUT_SUMMARY}")
print(summary.head(10))
