# 🌐 Fluxo Técnico do Projeto Linkfort (V3.0)

Este documento detalha a arquitetura de engenharia de dados utilizada para o benchmarking de DNS do projeto Linkfort. A solução evoluiu para uma **Arquitetura Híbrida (Bash + Python)** para garantir precisão milimétrica em ambiente virtualizado.

---

## 🏗️ Arquitetura da Solução

O sistema opera em um ciclo fechado de **Coleta Contínua** e **Análise Estatística**.

### Diagrama de Fluxo

```mermaid
graph TD
    subgraph Coleta [📡 Camada de Coleta (Bash)]
        style Coleta fill:#e1f5fe,stroke:#01579b
        A([Start: monitor_dados.sh]) -->|Loop Infinito| B{Iterar Lista DNS}
        B -->|Executar Query| C[fa:fa-terminal Dig]
        C -->|Raw Output| D[Normalizar Dados]
        D -->|Append| E[(dados_dns_linkfort.csv)]
    end

    subgraph Analise [📊 Camada de Analytics (Python)]
        style Analise fill:#e8f5e9,stroke:#1b5e20
        E -->|Leitura| F[gerar_dashboard.py]
        F --> G[Limpeza & Parsing]
        G --> H{Cálculo de Score V3.0}
        H -->|Calcula P95| I[Penalidade de Cauda]
        H -->|Calcula Mediana| J[Desempenho Típico]
        H -->|Verifica Erros| K[Fator de Disponibilidade]
        
        I & J & K --> L[🏆 Ranking Final]
        L --> M[Gerar dashboard.html]
    end
```

---

## 🔬 Componentes do Sistema

| Componente | Arquivo | Tecnologia | Responsabilidade |
| :--- | :--- | :--- | :--- |
| **Coleta** | [`monitor_dados.sh`](file:///home/sant/scriptbash/linkfort/monitor_dados.sh) | Bash, Dig | Executar milhões de consultas com baixo overhead. Prioriza I/O e precisão de timestamp. |
| **Storage** | [`dados_dns_linkfort.csv`](file:///home/sant/scriptbash/linkfort/dados_dns_linkfort.csv) | CSV | Armazenamento de séries temporais brutas. Schema: `timestamp,dns_name,ip,domain,latency,status` |
| **Analytics** | [`gerar_dashboard.py`](file:///home/sant/scriptbash/linkfort/gerar_dashboard.py) | Python, Pandas | Processamento estatístico pesado, rejeição de outliers e cálculo de Score. |
| **View** | `dashboard.html` | HTML, Plotly | Visualização interativa dos resultados para tomada de decisão humana. |

---

## 🧠 Algoritmo de Ranking (SLA Grade)

Para combater as limitações de um ambiente "Subhost" (Virtualizado), o algoritmo de ranking ignora a média simples e foca na consistência e estabilidade.

### 📊 Tabela de Pesos e Métricas

| Métrica | Peso | Descrição Técnica | Por que usar? |
| :--- | :---: | :--- | :--- |
| **P95 (Percentil 95)** | **50%** | Latência máxima experimentada por 95% das requisições. | Ignora os 5% de piores casos (outliers da VM) mas penaliza lentidão consistente. |
| **Mediana (P50)** | **50%** | O valor central da distribuição de latência. | Representa a experiência "típica" do usuário, imune a picos extremos isolados no desvio padrão. |
| **Taxa de Erro** | **Critical** | Porcentagem de falhas (TIMEOUT/SERVFAIL). | **Disponibilidade > Velocidade**. <br>🚨 `> 1%`: Score reduzido em 50%. <br>☠️ `> 5%`: Score ZERADO. |

### 🧮 Fórmula do Score

O Score final (0 a 100) é calculado normalizando as latências, onde **0ms = 100 pontos** e **200ms = 0 pontos**.

$$ Score_{final} = \left( Score(P95) \times 0.5 \right) + \left( Score(Mediana) \times 0.5 \right) \times Fator_{Disponibilidade} $$

---

## ⚠️ Limitações Conhecidas (Subhost Mitigation)

| Limitação | Impacto no Teste | Solução Implementada (V3.0) |
| :--- | :--- | :--- |
| **NAT Overhead** | Adiciona ~2-5ms em toda requisição. | Diferenças < 5ms são consideradas irrelevantes (Empate Técnico). |
| **CPU Steal** | Picos repentinos de latência (Ex: 500ms). | Uso de **P95** ao invés de Média. A média seria contaminada pelo pico, o P95 o ignora. |
| **Packet Loss** | Falha completa na resolução. | Monitoramento estrito de **Taxa de Erro**. |

---

> *Documentação atualizada automaticamente pelo Agente Antigravity.*
