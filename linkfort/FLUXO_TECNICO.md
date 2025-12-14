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
    *   **Solução Atual**: O cálculo de `std` (Desvio Padrão) penaliza instabilidade.
    *   **Melhoria Proposta**: Usar **Mediana** em vez de Média para o ranking principal, pois a Mediana ignora esses picos artificiais da VM.

3.  **Concorrência de Rede**:
    *   O "Subhost" compartilha a placa de rede com o Host e outras VMs.
    *   **Impacto**: Se o Host estiver fazendo download, a medição do DNS na VM piora.

## Proposta de Novo Algoritmo de Ranking
Dado o ambiente, o algoritmo atual (Média) pode ser injusto.
**Novo Score Sugerido:**
- Base: **Mediana** (mais robusta contra lags da VM).
- Desempate: **Desvio Padrão**.
- *Penalidade Severa*: Timeouts (confiabilidade).
