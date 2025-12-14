# 📡 Linkfort DNS Benchmark (v3.4)

> **Ferramenta profissional de análise de DNS com Visual Premium.**
> Desenvolvida para ambientes "Subhost" (Containers/WSL/VMs) com foco em precisão e estética.

Este projeto realiza testes de latência DNS precisos utilizando `dig` e gera um **Dashboard Interativo (Dark Mode)** com métricas estatísticas robustas.

---

## ✨ Novidades da v3.4
- **🛡️ Anti-Flood**: Sistema de coleta ajustado para não saturar roteadores domésticos.
- **🎨 Design Premium**: Interface Dark Mode com Glassmorphism e fontes Google.
- **🚀 Servidor Integrado**: Exibe o relatório automaticamente em `http://localhost:7777`.
- **🏆 Ranking Inteligente**: Destaca os vencedores com medalhas e badges de score.
- **🔴 Botão Ao Vivo (v3.4)**: Controle total sobre o auto-refresh do dashboard.

---

## 🚀 Início Rápido

O orquestrador `run_all.sh` cuida de tudo: cria o ambiente virtual, instala libs, roda os testes e abre o navegador.

### Rodar um Teste Rápido
Executa 1 rodada de testes e abre o dashboard.
```bash
./run_all.sh --test
```

### Rodar uma Coleta Estendida
Executa 50 rodadas para maior precisão estatística.
```bash
./run_all.sh --collect 50
```

### Apenas Visualizar (Sem Coletar)
Regenera o gráfico com os dados atuais e inicia o servidor.
```bash
./run_all.sh
```

---

## 📊 Como Funciona (SLA Grade)

O Linkfort v3 utiliza um **Algoritmo de Score Ponderado** para ignorar picos de CPU virtualizada:

1.  **P95 (Percentil 95)** [`50%`]: Penaliza a "pior" latência típica.
2.  **Mediana** [`50%`]: Mede o desempenho comum do dia a dia.
3.  **Disponibilidade** [`Crítico`]: Falhas > 5% desclassificam o DNS (Score 0).

---

## 🛠️ Arquitetura Técnica

| Componente | Script | Função |
| :--- | :--- | :--- |
| **Worker** | `monitor_dados.sh` | Coleta dados brutos via `dig` com throttling de 0.2s. |
| **Engine** | `gerar_dashboard.py` | Processa estatísticas com Pandas e injeta CSS/HTML moderno. |
| **Server** | `serve.py` | Servidor HTTP leve que serve a porta 7777 e abre o browser. |
| **Manager** | `run_all.sh` | Orquestra o fluxo fluxo completo (Setup -> Coleta -> Análise -> Server). |

---

## 📋 Requisitos
- Linux (Debian/Ubuntu/ChromeOS/Zorin)
- Python 3.x
- `dig` (dnsutils)
