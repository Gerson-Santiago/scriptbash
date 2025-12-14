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
    end

    subgraph Visualizacao [🎨 Camada de Apresentação (HTML/CSS)]
        style Visualizacao fill:#fff3e0,stroke:#e65100
        L --> R[Gráficos Plotly Dark]
        P --> Q[Geração de HTML V3.1]
        Q --> S[Injection: CSS Premium]
        R --> S
        S --> T[Output: dashboard.html]
        T --> U[Disponibilizar via server :7777]
        U --> V[🔴 Botão Live Mode: JS Toggle]
    end
```

---

## 🔬 Componentes do Sistema

| Componente | Arquivo | Tecnologia | Responsabilidade |
| :--- | :--- | :--- | :--- |
| **Coleta** | [`monitor_dados.sh`](file:///home/sant/scriptbash/linkfort/monitor_dados.sh) | Bash, Dig | Executar milhões de consultas com baixo overhead. Prioriza I/O e precisão de timestamp. |
| **Storage** | [`dados_dns_linkfort.csv`](file:///home/sant/scriptbash/linkfort/dados_dns_linkfort.csv) | CSV | Armazenamento de séries temporais brutas. Schema: `timestamp,dns_name,ip,domain,latency,status` |
| **Analytics** | [`gerar_dashboard.py`](file:///home/sant/scriptbash/linkfort/gerar_dashboard.py) | Python, Pandas | Processamento estatístico pesado, rejeição de outliers e cálculo de Score. |
| **View** | `dashboard.html` | HTML, CSS, Plotly | **Engine Visual V3.1**. Renderiza Dark Mode, Glassmorphism e interatividade vetorial. |

---

## 🧠 Algoritmo de Ranking (SLA Grade)

Para combater as limitações de um ambiente "Subhost" (Virtualizado), o algoritmo de ranking ignora a média simples e foca na consistência e estabilidade.

### 📊 Tabela de Pesos e Métricas

| Métrica | Peso | Descrição Técnica | Por que usar? |
| :--- | :---: | :--- | :--- |
| **P95 (Percentil 95)** | **50%** | Latência máxima experimentada por 95% das requisições. | Ignora os 5% de piores casos (outliers da VM) mas penaliza lentidão consistente. |
| **Mediana (P50)** | **50%** | O valor central da distribuição de latência. | Representa a experiência "típica" do usuário, imune a picos extremos isolados no desvio padrão. |

## ⚠️ Limitações Conhecidas & Mitigações (Código Fonte)

| Limitação | Impacto no Teste | Solução Implementada (`monitor_dados.sh`) |
| :--- | :--- | :--- |
| **NAT Overhead** | Adiciona ~2-5ms em toda requisição. | **Sleep 0.5s** (Ajuste V3.2) para "respiração" do link. |
| **DNS Hang** | Queries travadas bloqueiam o script. | Retentativa Inteligente: `+tries=3` com `+timeout=2s`. |
| **Packet Loss** | Falha completa na resolução. | Monitoramento de **Taxa de Erro** no Python. Fail-fast no Bash. |
| **Taxa de Erro** | **Critical** | Porcentagem de falhas (TIMEOUT/SERVFAIL). | **Regra Suavizada (V3.2)** para Redes Domésticas: <br>🚨 `> 10%`: Score reduzido em 50%. <br>☠️ `> 25%`: Score ZERADO. |

### 🧮 Fórmula do Score (V3.0 Implementada)

A implementação no `gerar_dashboard.py` utiliza a seguinte lógica exata:

#### 1. Normalização de Latência (`lat_to_score`)
Convertemos milissegundos em pontos (0-100), onde **cada 2ms de latência custa 1 ponto**.
$$ Score_{parcial} = \max(0, 100 - \frac{ms}{2}) $$
*Exemplo: 20ms = 90 pontos. 200ms+ = 0 pontos.*

#### 2. Composição Ponderada
$$ Score_{Base} = (Score(P95) \times 0.5) + (Score(Mediana) \times 0.5) $$

#### 3. Penalidade de Disponibilidade (Availability Check - V3.2)
O script aplica penalidades baseadas na estabilidade da conexão:

- **Taxa de Erro > 10%**: $$ Score_{Final} = Score_{Base} \times 0.5 $$
- **Taxa de Erro > 25%**: $$ Score_{Final} = 0 $$ (Desclassificação)

---


---

> *Documentação atualizada automaticamente pelo Agente Antigravity.*
