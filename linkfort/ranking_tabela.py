#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
SUMMARY_CSV = BASE_DIR / "output" / "resumo_dns.csv"

# Ler CSV resumido
df = pd.read_csv(SUMMARY_CSV)

# Ordenar por média (menor é melhor)
df_sorted = df.sort_values("media").reset_index(drop=True)

# Adicionar coluna de ranking
df_sorted["ranking"] = df_sorted["media"].rank(method="min").astype(int)

# Selecionar colunas para a tabela
tabela = df_sorted[["ranking", "dns", "dominio", "media", "delta"]]

# Mostrar tabela
print("\n[Tabela de ranking de DNS por tempo médio]")
print(tabela)

# Salvar tabela como CSV
tabela.to_csv(BASE_DIR / "output" / "ranking_dns.csv", index=False)
print("\n[Tabela salva em output/ranking_dns.csv]")
