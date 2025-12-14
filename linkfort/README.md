# 📡 Linkfort DNS Benchmark (v3.5)

> **Ferramenta profissional de análise de DNS com Visual Premium.**
> Desenvolvida para ambientes "Subhost" (Containers/WSL/VMs) com foco em precisão e estética.

Este projeto realiza testes de latência DNS precisos utilizando `dig` e gera um **Dashboard Interativo (Dark Mode)** com métricas estatísticas robustas.

---

## ✨ Novidades da v3.5 (Clean Architecture)
- **🧱 Arquitetura Modular**: Código Python refatorado em pacote `src/` com separação de responsabilidades (Config, Data, Analytics).
- **⚡ Dashboard Estático**: `dashboard.html` agora é 100% Client-Side, consumindo JSON dinâmico.
- **🛡️ Git-Friendly**: Separação total entre Código (`.html`) e Dados (`.json`) para facilitar versionamento.
- **🚀 Servidor Integrado**: Exibe o relatório automaticamente em `http://localhost:7777`.
- **🏆 Ranking Inteligente**: Destaca os vencedores com medalhas e badges de score.

---

## 📥 Instalação

### 1. Pré-requisitos
Antes de tudo, garanta que você tenha o Python 3 e o utilitário `dig` instalados.
```bash
sudo apt update
sudo apt install python3 python3-venv dnsutils -y
```

### 2. Clonar o Repositório
Baixe o código fonte para sua máquina:
```bash
git clone https://github.com/Gerson-Santiago/scriptbash.git
cd scriptbash/linkfort
```
> **Nota:** O projeto LinkFort faz parte do repositório `scriptbash`.

### 3. Preparar o Ambiente
Dê permissão de execução para o script principal.

**Nota sobre Dependências Python:** Não é necessário instalar nada manualmente com `pip`. O LinkFort cria automaticamente um **Ambiente Virtual isolado** (`.venv`) e instala todas as bibliotecas necessárias (pandas, plotly, etc.) na primeira execução, mantendo seu sistema limpo.

```bash
chmod +x linkfort
```

---

## 🚀 Início Rápido

> **📘 Guia Completo:** Para detalhes de todos os comandos e fluxo de dados, consulte [COMANDOS.md](COMANDOS.md).

### Comandos Essenciais

| Ação | Comando |
| :--- | :--- |
| **Monitorar (Live)** | `./linkfort --live` |
| **Teste Rápido** | `./linkfort --test` |
| **Resetar Tudo** | `./linkfort -r` |
| **Coletar N vezes** | `./linkfort 50` |

### 🧹 Limpeza (Reset)
O comando `./linkfort -r` é vital para reiniciar testes. Ele:
1. Encerra processos travados na porta 7777 (Server).
2. Remove históricos (`csv`, `json`, `html`).

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
| **CLI** | `linkfort` | Orquestrador principal (CLI unificada). |
| **Worker** | `monitor_dados.sh` | (Interno) Coleta dados brutos via `dig`. |
| **Engine** | `gerar_dashboard.py` | (Interno) Processa estatísticas e gera HTML. |
| **Server** | `serve.py` | (Interno) Servidor HTTP leve. |

---

## 📋 Requisitos
- Linux (Debian/Ubuntu/ChromeOS/Zorin)
- Python 3.x (Testado com `v3.11.2`)
- Pip (Testado com `v23.0.1`)
- `dig` (dnsutils)
