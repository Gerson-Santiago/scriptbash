#!/usr/bin/env bash
set -e

# Caminhos
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_ACTIVATE="$BASE_DIR/.venv/bin/activate"

echo "========================================="
echo "   LINKFORT - FLUXO AUTOMÁTICO v1.0"
echo "========================================="

# 1. Ativar Ambiente
echo "[1/3] Ativando ambiente virtual..."
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
else
    echo "ERRO: Ambiente virtual não encontrado em .venv"
    exit 1
fi

# 2. Coletar Dados (Opcional - via argumento)
# Se passar --collect, roda o monitor. Se não, apenas regenera o dashboard.
if [[ "$*" == *"--collect"* ]]; then
    echo "[2/3] Iniciando coleta de dados (monitor_dados.sh)..."
    # Vamos rodar o monitor por 1 minuto apenas para teste rápido, 
    # ou deixar o usuário interagir se o script for interativo.
    # O script monitor é desenhado pra rodar em loop, então vamos rodar 1 loop apenas.
    # Hack: exportar var de ambiente para controlar duração se o script permitir, 
    # mas o script hardcoded DURACAO_MINUTOS=60. 
    # Vamos apenas avisar o usuário para rodar separado ou modificar o monitor.sh no futuro.
    echo "Aviso: O monitor_dados.sh roda por 60 min. Rodando em background?"
    # Por segurança neste MVP, vamos apenas regenerar o dashboard.
    echo "PULADO: Para coletar, execute ./monitor_dados.sh"
else
    echo "[2/3] Usando dados existentes (Pule esta etapa com --collect)"
fi

# 3. Gerar Dashboard
echo "[3/3] Gerando Dashboard Analítico..."
python3 "$BASE_DIR/gerar_dashboard.py"

echo "========================================="
echo "✅ Concluído!"
echo "Acesse: http://localhost:7777/dashboard.html"
echo "========================================="
