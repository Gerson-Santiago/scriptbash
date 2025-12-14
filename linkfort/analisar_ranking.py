#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
SUMMARY_CSV = BASE_DIR / "output" / "resumo_dns.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Ler CSV resumido
df = pd.read_csv(SUMMARY_CSV)

# Ranking por menor média de tempo
ranking_media = df.sort_values("media").reset_index(drop=True)

print("\n[Ranking por menor média de tempo]")
print(ranking_media[["dns", "dominio", "media", "delta"]].head(10))

# Ranking por maior delta (variação)
ranking_delta = df.sort_values("delta", ascending=False).reset_index(drop=True)

print("\n[Ranking por maior delta]")
print(ranking_delta[["dns", "dominio", "delta", "media"]].head(10))

# Gráfico: média de tempo por DNS
plt.figure(figsize=(10,6))
for dominio in df["dominio"].unique():
    subset = df[df["dominio"] == dominio]
    plt.bar(subset["dns"], subset["media"], label=dominio)

plt.xlabel("DNS")
plt.ylabel("Tempo médio (ms)")
plt.title("Média de tempo por DNS")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "grafico_media_dns.png")
plt.show()
