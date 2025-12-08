#!/bin/bash

# Diretório onde os PDFs serão salvos
DESTINO="/home/sant/Downloads/SED_PDF"

# Lista de nomes de arquivos
LISTA="/home/sant/scriptbash/nomes_sed.txt"

# URL base da SED
URL_BASE="https://homologacaointegracaosed.educacao.sp.gov.br/documentacao/cadastrodealunos/REST"

# Criar pasta se não existir
mkdir -p "$DESTINO"

echo "--------------------------------------------------"
echo "INICIANDO DOWNLOAD DOS PDFs DA SED"
echo "Destino: $DESTINO"
echo "Lista:   $LISTA"
echo "--------------------------------------------------"

while IFS= read -r arquivo; do
    # Pula linhas vazias
    [[ -z "$arquivo" ]] && continue

    URL="$URL_BASE/$arquivo"
    DESTINO_ARQ="$DESTINO/$arquivo"

    echo ""
    echo "→ Arquivo: $arquivo"

    # Se já existe, pula
    if [[ -f "$DESTINO_ARQ" ]]; then
        echo "   ✔ Já existe — pulando"
        continue
    fi

    echo "   ↓ Baixando..."
    
    wget -q --show-progress -O "$DESTINO_ARQ" "$URL"

    if [[ $? -eq 0 ]]; then
        echo "   ✔ Download concluído"
    else
        echo "   ✖ ERRO ao baixar: $arquivo"
        rm -f "$DESTINO_ARQ"
    fi

done < "$LISTA"

echo ""
echo "--------------------------------------------------"
echo "PROCESSO FINALIZADO!"
echo "Os arquivos estão em: $DESTINO"
echo "--------------------------------------------------"
