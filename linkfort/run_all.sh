#!/usr/bin/env bash
set -e

# Caminhos
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/.venv"
VENV_ACTIVATE="$VENV_DIR/bin/activate"

echo "========================================="
echo "   LINKFORT - FLUXO AUTOMÁTICO v3.0"
echo "========================================="

# 1. Setup Ambiente
echo "[1/3] Verificando ambiente..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_ACTIVATE"
    pip install -r "$BASE_DIR/requirements.txt"
else
    source "$VENV_ACTIVATE"
fi

# 2. Coleta de Dados
# Default: não coleta, apenas processa.
# --collect N: roda N rodadas
# --test: roda 1 rodada
RODADAS=0

if [[ "$*" == *"--test"* ]]; then
    RODADAS=1
elif [[ "$1" == "--collect" && -n "$2" ]]; then
    RODADAS=$2
fi

if [ "$RODADAS" -gt 0 ]; then
    echo "[2/3] Iniciando coleta de dados ($RODADAS rodadas)..."
    chmod +x "$BASE_DIR/monitor_dados.sh"
    "$BASE_DIR/monitor_dados.sh" --count "$RODADAS"
else
    echo "[2/3] Usando dados existentes (Use --test ou --collect N para atualizar)"
fi

# 3. Gerar Dashboard
echo "[3/3] Gerando Analytics..."
python3 "$BASE_DIR/gerar_dashboard.py"

echo "========================================="
echo "✅ Processo concluído com sucesso!"
echo "📄 Dashboard: file://$BASE_DIR/dashboard.html"
echo "========================================="
