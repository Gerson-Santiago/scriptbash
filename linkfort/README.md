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
- **🔴 Botão Ao Vivo**: Controle interativo de **Play/Pause** para atualização automática (Auto-Refresh) via UI.

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

O comando `linkfort` cuida de tudo: cria o ambiente virtual, instala libs, roda os testes e abre o navegador.

### Rodar um Teste Rápido
Executa 1 rodada de testes e abre o dashboard.
```bash
./linkfort --test
```

### Rodar uma Coleta Estendida
### Rodar uma Coleta Estendida
Executa `N` rodadas para maior precisão estatística.
```bash
./linkfort 100        # Exemplo: roda 100 vezes
# ou
./linkfort --collect 100
```
> **⏳ Estimativa de Tempo:** O script calculará e avisará o tempo previsto. O servidor web abre automaticamente ao final.

### Apenas Visualizar (Sem Coletar)
Regenera o gráfico com os dados atuais e inicia o servidor.
```bash
./linkfort
```

### 🧹 Limpar Dados
Apaga todo o histórico de testes e o dashboard, permitindo começar do zero.
> **Nota de Segurança:** Não se preocupe em recriar arquivos. O próximo comando de coleta (ex: `./linkfort 50`) reconstruirá automaticamente tudo o que for necessário.

```bash
./linkfort --reset
```

### 🔴 Modo Ao Vivo (Recomendado)
Executa a coleta em background e inicia o servidor web automaticamente em um único terminal.

```bash
./linkfort --live
# Acesse http://localhost:7777 e ative o botão "AO VIVO" no topo.
# Pressione Ctrl+C para encerrar tudo.
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
