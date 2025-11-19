#!/bin/bash

# Caminho do repositório
REPO_DIR=~/scriptbash
DATA=$(date "+%Y-%m-%d %H:%M:%S")

echo "🔄 Iniciando backup das configurações..."

# 1. Copia o .bashrc atual para o repositório (com nome de bashrc_copy)
cp ~/.bashrc $REPO_DIR/bashrc_copy

# 2. Entra na pasta
cd $REPO_DIR

# 3. Comandos do Git
git add bashrc_copy prompt-switcher.sh
git commit -m "Backup: Atualização do .bashrc e scripts em $DATA"
git push

echo "✅ Backup concluído com sucesso! Suas configs estão no GitHub."

