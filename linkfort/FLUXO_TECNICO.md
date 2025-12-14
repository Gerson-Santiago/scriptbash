# Fluxo do Projeto Linkfort e Análise Técnica

## Resumo do Fluxo
O projeto consiste em um ciclo de coleta de dados de rede (DNS Benchmarking) seguido de processamento estatístico e visualização.

## Diagrama de Fluxo (Mermaid)

```mermaid
graph TD
    subgraph Coleta [Camada de Coleta (Bash)]
        A[Início: monitor_dados.sh] -->|Loop| B{Iterar Domínios}
        B -->|Para cada DNS| C[Comando: dig]
        C -->|Consulta A| D{Sucesso?}
        D -- Sim --> E[Extrair Query Time]
        D -- Não --> F[Registrar Timeout]
        E --> G[Append: dados_dns_linkfort.csv]
        F --> G
        G --> H[Sleep Intervalo]
        H --> A
    end

    subgraph Processamento [Camada de Análise (Python)]
        I[dados_dns_linkfort.csv] -->|Input| J[Script: gerar_dashboard.py]
        J --> K[Limpeza de Dados]
        K --> L{Cálculo de Métricas}
        L --> M[Média Simples]
        L --> N[Estabilidade (Std Dev)]
        L --> O[Score Algoritmo]
        O --> P[Ranking Top 3]
    end

    subgraph Visualizacao [Front-end Estático]
        P --> Q[Gerar HTML + CSS]
        L --> R[Gerar Gráficos Plotly]
        Q --> S[Output: dashboard.html]
        R --> S
    end

    G -.->|Gatilho Opcional| J
```

## Análise de Limitações Técnicas ("Subhost")

Como o ambiente é um "Subhost" (Crostini/VM/Container), temos considerações estatísticas importantes:

1.  **Overhead de Virtualização**:
    *   Toda requisição passa por NAT/Bridge do Host físico.
    *   **Impacto**: Latências muito baixas (< 5ms) podem ser mascaradas pelo *overhead* do sistema operacional.
    *   **Solução**: Ignorar diferenças menores que 5ms entre DNSs; considerar empate técnico.

2.  **Jitter (Variabilidade)**:
    *   VMs sofrem "roubo de CPU" momentâneo pelo Host.
    *   **Impacto**: Picos de latência (outliers) que não são culpa do DNS, mas da VM travando por milissegundos.
    *   **Solução Avaliada**: Usar Média simples foi descartado. Usar apenas Mediana foi o passo 2.
    *   **Solução Final (v3.0)**: Usar **P95 (Percentil 95)** e **CV (Coeficiente de Variação)** para ignorar outliers mas penalizar instabilidade real.

3.  **Concorrência de Rede**:
    *   O "Subhost" compartilha a placa de rede com o Host e outras VMs.
    *   **Impacto**: Se o Host estiver fazendo download, a medição do DNS na VM piora.

## Algoritmo de Ranking (Analytics 3.0)
O sistema evoluiu para um motor de decisão profissional ("SLA Grade").

### Métricas Principais
| Métrica | Peso no Score | Propósito |
| :--- | :--- | :--- |
| **P95 (Percentil 95)** | **50%** | **"O Pior Caso Típico"**. Garante que 95% das requisições são rápidas. Ignora os 5% piores (outliers extremos da VM). |
| **Mediana** | **50%** | **"O Caso Comum"**. Desempenho no dia a dia, ignorando totalmente ruídos. |
| **Taxa de Erro** | *Multiplicador* | **Disponibilidade**. Se Timeouts > 1%, o score cai pela metade. Se > 5%, o score zera. |
| **CV** | *Informativo* | **Estabilidade**. Diz se o DNS é consistente ou "bipolar". |

### Diagrama de Decisão 3.0
```mermaid
graph TD
    A[Dados Brutos] --> B{Timeout?}
    B -- Sim --> C[Contabilizar Taxa de Erro]
    B -- Não --> D[Calcular Mediana]
    B -- Não --> E[Calcular P95]
    
    C --> F{Erro > 5%?}
    F -- Sim --> G[Score = 0]
    F -- Não --> H[Fator Disponibilidade]
    
    D --> I[Score Mediana (0-100)]
    E --> J[Score P95 (0-100)]
    
    H --> K[Score Final]
    I --> K
    J --> K
    
    K --> L[Ranking Top 3]
```
