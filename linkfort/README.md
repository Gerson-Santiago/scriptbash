# 📡 Linkfort DNS Benchmark (v3.0)

> **Ferramenta profissional de análise de DNS desenvolvida para ambientes "Subhost" (Containers/WSL/VMs).**

Este projeto realiza testes de latência DNS precisos utilizando `dig` e gera um dashboard analítico completo com métricas estatísticas robustas (P95, Mediana) para ignorar ruídos de virtualização.

---

## 🚀 Início Rápido

O projeto conta com um orquestrador inteligente que configura tudo para você (Ambiente Virtual Python + Dependências).

### Rodar um Teste Rápido
Executa 1 rodada de testes e gera o dashboard.
```bash
./run_all.sh --test
```

### Rodar uma Coleta Estendida
Executa 50 rodadas de testes (mais dados = maior precisão) e gera o dashboard.
```bash
./run_all.sh --collect 50
```

### Apenas Gerar Dashboard (Sem Coleta)
Processa os dados já existentes no CSV.
```bash
./run_all.sh
```

---

## 📊 Como Funciona o Ranking (SLA Grade)

Diferente de benchmarks comuns que usam Média (facilmente contaminada por picos de CPU), o Linkfort v3 utiliza um **Algoritmo de Score Ponderado**:

1.  **P95 (Percentil 95)** [`50%`]: Penaliza servidores que têm picos de lentidão eventuais.
2.  **Mediana** [`50%`]: Mede o desempenho típico "no dia a dia".
3.  **Disponibilidade** [`Critical`]:
    *   Falhas > 1%: Score reduzido em **50%**.
    *   Falhas > 5%: Score **ZERADO** (Desqualificado).

---

## 🛠️ Arquitetura Técnica

| Componente | Função | Detalhes Cativantes |
| :--- | :--- | :--- |
| **`monitor_dados.sh`** | Coletor | Usa `dig` nativo para contornar cache de OS. Implementa *throttling* (0.2s sleep) para não saturar NAT. |
| **`gerar_dashboard.py`** | Analisador | Python + Pandas. Robusto a falhas de CSV. Calcula Score V3.0 e exporta HTML standalone. |
| **`run_all.sh`** | Orquestrador | "Infrastructure-as-Code" leve. Cria `.venv` automaticamente e gerencia o fluxo. |

---

## 📂 Estrutura de Dados
Os dados brutos são salvos atomicamente em `dados_dns_linkfort.csv`:
```csv
timestamp,dns_name,dns_ip,domain,latency_ms,status
2025-12-14 12:30:29,Google_Sec,8.8.4.4,google.com,7,OK
```

---

## 📋 Requisitos
- Linux (Debian/Ubuntu/ChromeOS)
- Python 3.x
- `dig` (dnsutils)
- `venv` (python3-venv)
