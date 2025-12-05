#!/bin/bash

# --- CONFIGURAÇÕES ---
DIR_DESTINO="/home/sant/scriptbash"
ARQUIVO_CSV="${DIR_DESTINO}/dados_dns_linkfort.csv"
HORAS_DURACAO=8
MINUTOS_INTERVALO=15

# --- INICIALIZAÇÃO ---

# 1. Garante que a pasta existe (se não existir, cria)
if [ ! -d "$DIR_DESTINO" ]; then
    echo "Pasta $DIR_DESTINO não encontrada. Criando..."
    mkdir -p "$DIR_DESTINO"
fi

# 2. Cria o cabeçalho do CSV se o arquivo não existir
if [ ! -f "$ARQUIVO_CSV" ]; then
    echo "Arquivo CSV não encontrado. Gerando novo em: $ARQUIVO_CSV"
    echo "data,hora,ip,latencia_media" > "$ARQUIVO_CSV"
fi

# Converte tempo para segundos
DURACAO_LIMITE=$((HORAS_DURACAO * 3600))
INTERVALO_SEG=$((MINUTOS_INTERVALO * 60))
TEMPO_INICIO=$(date +%s)

# Lista de IPs
IPS=("138.97.220.58" "138.97.220.62" "138.97.220.57" "138.97.220.60" "138.97.220.65" "138.97.220.66" "138.97.220.69" "138.97.220.70" "8.8.8.8" "1.1.1.1")

echo "=== Iniciando Coleta de Dados DNS ==="
echo "Modo: Execução por $HORAS_DURACAO horas (Intervalo: $MINUTOS_INTERVALO min)"
echo "Salvando dados em: $ARQUIVO_CSV"

# --- LOOP PRINCIPAL ---
while true; do
    AGORA_SEG=$(date +%s)
    TEMPO_DECORRIDO=$((AGORA_SEG - TEMPO_INICIO))

    # Regra de Parada
    if [ "$TEMPO_DECORRIDO" -ge "$DURACAO_LIMITE" ]; then
        echo "Tempo limite atingido."
        # Tenta rodar o analisador usando o caminho completo também (caso esteja lá)
        if [ -f "${DIR_DESTINO}/analisar.py" ]; then
            echo "Gerando relatório final..."
            # Precisamos entrar na pasta ou passar o caminho para o python, 
            # mas seu script python espera o CSV na mesma pasta.
            cd "$DIR_DESTINO" && python3 analisar.py
        fi
        break
    fi

    # Coleta
    HORA_ATUAL=$(date +%H)
    DATA_HOJE=$(date +%Y-%m-%d)
    HORARIO_COMPLETO=$(date +%H:%M)

    echo "--- Teste às $HORARIO_COMPLETO ---"

    for ip in "${IPS[@]}"; do
        MEDIA=$(ping -c 5 -W 1 $ip | tail -1 | awk -F '/' '{print $5}')
        
        if [ ! -z "$MEDIA" ]; then
            echo "$DATA_HOJE,$HORA_ATUAL,$ip,$MEDIA" >> "$ARQUIVO_CSV"
            echo "   IP: $ip | $MEDIA ms"
        else
            echo "$DATA_HOJE,$HORA_ATUAL,$ip,TIMEOUT" >> "$ARQUIVO_CSV"
        fi
    done

    echo "Dados salvos. Próximo teste em $MINUTOS_INTERVALO minutos."
    sleep $INTERVALO_SEG
done
