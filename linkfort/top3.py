#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
SUMMARY_CSV = BASE_DIR / "output" / "resumo_dns.csv"

# Ler CSV resumido
df = pd.read_csv(SUMMARY_CSV)

# Calcular ranking baseado em média + delta
# Menor média e menor delta é melhor
df["score"] = df["media"] + df["delta"]

# Ordenar pelo score
df_sorted = df.sort_values("score").reset_index(drop=True)

# Selecionar colunas úteis
top_dns = df_sorted[["dns", "media", "delta"]].head(3)

print("\n[Top 3 DNS recomendados para o roteador]")
print(top_dns)
