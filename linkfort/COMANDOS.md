# 📟 Comandos do Linkfort (CLI)

Este documento lista os comandos oficiais para operar o Linkfort no terminal.

## 🚀 Comandos Principais

### **Modo Live (Monitoramento Contínuo)**
O modo principal. Coleta dados, gera dashboard e serve na web continuamente.
```bash
./linkfort --live
```
**O que faz:**
1. Inicia monitoramento em background.
2. Gera `dashboard.html` e `dados.json` a cada rodada.
3. Inicia servidor web em `http://localhost:7777`.
4. **Ctrl+C** encerra tudo com segurança.

### **Resetar Tudo**
Limpa todos os dados antigos e **encerra processos travados** na porta 7777.
```bash
./linkfort --reset
# ou
./linkfort -r
```
**O que faz:**
1. Mata processos usando a porta 7777 (força bruta segura).
2. Remove `dados_dns_linkfort.csv`, `dashboard.html` e `dados.json`.
3. Deixa o ambiente limpo para um novo teste.

---

## 🧪 Comandos de Teste e Coleta

### **Teste Rápido**
Executa apenas **uma rodada** para verificar se tudo está funcionando.
```bash
./linkfort --test
```

### **Coleta Determinada (N Rodadas)**
Coleta um número específico de rodadas e depois abre o servidor.
```bash
./linkfort 50
```
*Exemplo acima: Coleta 50 rodadas (aprox. 60 min) e depois abre o dashboard.*

---

## 📂 Arquivos Gerados

*   **`dashboard.html`**: O painel visual. **(Frontend Estático - Tracked)**.
*   **`dados.json`**: Dados brutos e gráficos Plotly. **(Volátil - Ignored)**.
*   **`dados_dns_linkfort.csv`**: Histórico completo de latências. **(Ignorado no git)**.

## 🛠️ Solução de Problemas

**Erro: "Porta 7777 em uso"**
Execute o comando de reset para liberar a porta:
```bash
./linkfort -r
```

---

## 🔄 Ciclo de Vida dos Dados

Entenda como os arquivos são gerados e atualizados:

1.  **Monitoramento (`monitor_dados.sh`)**:
    *   Executa o comando `dig` para cada DNS.
    *   **Gera**: `dados_dns_linkfort.csv` (Adiciona novas linhas).

2.  **Processamento (`gerar_dashboard.py`)**:
    *   Lê o CSV acumulado.
    *   Calcula métricas e gera gráficos Plotly.
    *   **Gera**: `dados.json` (Sobrescreve com dados + gráficos).
    *   **Dashboard**: O arquivo `dashboard.html` é **ESTÁTICO** e não é modificado.

3.  **Visualização (Browser)**:
    *   O navegador carrega `dashboard.html`.
    *   O Javascript busca `dados.json` e renderiza a tela.

> **💡 Dica Git**:
> *   `dashboard.html`: **TRACKED**. É o código frontend, versionado no git.
> *   `dados.json`: **IGNORED**. Dados voláteis ignorados no `.gitignore`.
