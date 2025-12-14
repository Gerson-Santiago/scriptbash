#!/bin/bash
# monitor_dados.sh
# Coletor de métricas DNS para o Projeto Linkfort v3.0
# Arquitetura: Coleta (Bash) -> CSV -> Análise (Python)

OUTPUT_FILE="dados_dns_linkfort.csv"
BASE_DIR=$(dirname "$(readlink -f "$0")")
DOMAINS=("google.com" "amazon.com" "facebook.com" "uol.com.br" "netflix.com" "chatgpt.com" "gemini.google.com" "canva.com" "sei.univesp.br" "bertioga.sp.gov.br" "youtube.com")

# Mapa de DNS (Array associativo requer Bash 4+)
declare -A DNS_MAP
DNS_MAP["138.97.220.58"]="Linkfort_1"
DNS_MAP["138.97.220.62"]="Linkfort_2"
DNS_MAP["138.97.220.57"]="Linkfort_3"
DNS_MAP["138.97.220.60"]="Linkfort_4"
DNS_MAP["138.97.220.65"]="Linkfort_5"
DNS_MAP["138.97.220.66"]="Linkfort_6"
DNS_MAP["138.97.220.69"]="Linkfort_7"
DNS_MAP["138.97.220.70"]="Linkfort_8"
DNS_MAP["8.8.8.8"]="Google_Pri"
DNS_MAP["8.8.4.4"]="Google_Sec"
DNS_MAP["1.1.1.1"]="Cloudflare_Pri"
DNS_MAP["1.0.0.1"]="Cloudflare_Sec"

# Inicializa CSV se não existir
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "timestamp,dns_name,dns_ip,domain,latency_ms,status" > "$OUTPUT_FILE"
fi

# Função de help
if [[ "$1" == "--help" ]]; then
    echo "Uso: $0 [--count N]"
    echo "  --count N : Executa N rodadas de testes e para (padrão: loop infinito)"
    exit 0
fi

# Configuração de repetição
# Default: 1 (Para evitar loop infinito acidental se não passar nada)
COUNT=1 
if [[ "$1" == "--count" && -n "$2" ]]; then
    COUNT=$2
fi

echo "--- Iniciando Coletor Linkfort v3.0 ---"
echo "Saída: $OUTPUT_FILE"
echo "DNSs: ${!DNS_MAP[@]}"
echo "Domains: ${DOMAINS[@]}"
echo "---------------------------------------"

ITERATION=0
while [ "$COUNT" -eq -1 ] || [ "$ITERATION" -lt "$COUNT" ]; do
    ((ITERATION++))
    echo "[$(date '+%H:%M:%S')] Rodada $ITERATION..."

    for ip in "${!DNS_MAP[@]}"; do
        name="${DNS_MAP[$ip]}"
        
        for domain in "${DOMAINS[@]}"; do
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            
            # Executa dig
            # +noall deve vir antes de +stats
            # TRIES=3 e TIMEOUT=2 para lidar com UDP loss ocasional
            output=$(dig "@$ip" "$domain" +noall +stats +tries=3 +timeout=2 2>&1)
            
            # Extrai tempo
            latency=$(echo "$output" | grep "Query time:" | awk '{print $4}')
            
            status="OK"
            if [[ -z "$latency" ]]; then
                latency="0" # Ou valor alto indicando erro
                status="TIMEOUT"
            fi
            
            # Escreve no CSV
            echo "$timestamp,$name,$ip,$domain,$latency,$status" >> "$OUTPUT_FILE"
            
            # Sleep moderado para não saturar buffer (Subhost mitigation)
            sleep 0.5
        done
    done
    
    echo "   -> Rodada concluída. Atualizando Dashboard..."
    
    # V3.4: Auto-Update do Dashboard
    # Executa o gerador silenciosamente para atualizar o HTML
    python3 "$BASE_DIR/gerar_dashboard.py" > /dev/null 2>&1 &
    
    sleep 0.5
done

echo "Coleta finalizada ($ITERATION rodadas)."
