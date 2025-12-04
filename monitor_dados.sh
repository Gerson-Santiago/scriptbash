#!/bin/bash

# Arquivo de dados (CSV)
ARQUIVO_CSV="dados_dns_linkfort.csv"

# Lista de IPs para testar (Linkfort Descobertos + Públicos)
# Inclui os oficiais (.58, .62) e os 'escondidos' rápidos que achamos (.66, .70, etc)
IPS=("138.97.220.58" "138.97.220.62" "138.97.220.57" "138.97.220.60" "138.97.220.65" "138.97.220.66" "138.97.220.69" "138.97.220.70" "8.8.8.8" "1.1.1.1")

# Cria o cabeçalho do CSV se não existir
if [ ! -f "$ARQUIVO_CSV" ]; then
    echo "data,hora,ip,latencia_media" > "$ARQUIVO_CSV"
fi

echo "=== Iniciando Coleta de Dados DNS ==="
echo "Salvando métricas em: $ARQUIVO_CSV"

while true; do
    HORA_ATUAL=$(date +%H)
    
    # 1. Regra de Parada (14h)
    if [ "$HORA_ATUAL" -ge 14 ]; then
        echo "Horário limite atingido (14h). Encerrando coleta."
        # Ao finalizar, roda a análise automaticamente
        echo "Gerando relatório final..."
        python3 analisar.py
        break
    fi

    # 2. Regra de Espera (Antes das 8h)
    if [ "$HORA_ATUAL" -lt 8 ]; then
        echo "Aguardando horário inicial (08:00)... Agora são $(date +%H:%M)"
        sleep 60
        continue
    fi

    # 3. Execução do Teste
    DATA_HOJE=$(date +%Y-%m-%d)
    echo "--- Rodando bateria de testes às $(date +%H:%M) ---"

    for ip in "${IPS[@]}"; do
        # Pega a média de 5 pings
        MEDIA=$(ping -c 5 -W 1 $ip | tail -1 | awk -F '/' '{print $5}')
        
        # Se o ping falhar, o awk retorna vazio, então verificamos
        if [ ! -z "$MEDIA" ]; then
            echo "$DATA_HOJE,$HORA_ATUAL,$ip,$MEDIA" >> "$ARQUIVO_CSV"
            echo "   IP: $ip | $MEDIA ms"
        else
            echo "$DATA_HOJE,$HORA_ATUAL,$ip,TIMEOUT" >> "$ARQUIVO_CSV"
        fi
    done

    echo "Dados salvos. Dormindo por 20 minutos..."
    sleep 1200 # 20 minutos
done
