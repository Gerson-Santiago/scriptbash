#!/usr/bin/env bash
# ==========================================================
# MONITOR DE PERFORMANCE DNS
# ==========================================================

set -euo pipefail

# -------------------------
# CONFIGURAÇÕES
# -------------------------
DURACAO_MINUTOS=60
INTERVALO_SEGUNDOS=60

BASE_DIR="/home/sant/scriptbash/linkfort"
CSV="$BASE_DIR/dados_dns_linkfort.csv"

DOMINIOS=(
  bertioga.sp.gov.br
  google.com
  linkfort.com.br
  sei.univesp.br
)

DNS_SERVERS=(
  138.97.220.57
  138.97.220.58
  138.97.220.60
  138.97.220.62
  138.97.220.65
  138.97.220.66
  138.97.220.69
  138.97.220.70
  8.8.8.8
  8.8.4.4
  1.1.1.1
  1.0.0.1
  208.67.222.222
  208.67.220.220
  9.9.9.9
  149.112.112.112
)

# -------------------------
# DEPENDÊNCIAS
# -------------------------
command -v dig >/dev/null || { echo "Erro: dig não encontrado"; exit 1; }
command -v awk >/dev/null || { echo "Erro: awk não encontrado"; exit 1; }

# -------------------------
# CABEÇALHO CSV
# -------------------------
if [ ! -f "$CSV" ]; then
  echo "data_hora,dns,dominio,req,tempo_ms" > "$CSV"
fi

# -------------------------
# FUNÇÕES
# -------------------------
resolver_dns() {
  local dns="$1"
  local dominio="$2"

  dig @"$dns" "$dominio" A \
    +tries=1 +timeout=1 +stats \
    2>/dev/null | awk '/Query time/ {print $4}'
}

registrar_csv() {
  local datahora="$1"
  local dns="$2"
  local dominio="$3"
  local req="$4"
  local tempo="$5"

  echo "$datahora,$dns,$dominio,$req,${tempo:-timeout}" >> "$CSV"
}

log_terminal() {
  local loop="$1"
  local dns="$2"
  local dominio="$3"
  local r1="$4"
  local r2="$5"

  echo "[loop $loop] DNS $dns | $dominio | req1: ${r1:-timeout} ms | req2: ${r2:-timeout} ms"
}

# -------------------------
# BANNER
# -------------------------
echo "=========================================="
echo "   BENCHMARK DNS – COLETA DE PERFORMANCE"
echo "=========================================="
echo "Diretório base    : $BASE_DIR"
echo "Arquivo CSV       : $CSV"
echo "Duração total     : $DURACAO_MINUTOS minuto(s)"
echo "Intervalo         : $INTERVALO_SEGUNDOS segundo(s)"
echo "Domínios          : ${#DOMINIOS[@]}"
echo "Servidores DNS    : ${#DNS_SERVERS[@]}"
echo

# -------------------------
# LOOP PRINCIPAL
# -------------------------
for ((loop=1; loop<=DURACAO_MINUTOS; loop++)); do
  DATA_HORA=$(date "+%Y-%m-%d %H:%M")
  echo "--- Loop $loop | $DATA_HORA ---"

  for dominio in "${DOMINIOS[@]}"; do
    for dns in "${DNS_SERVERS[@]}"; do

      req1=$(resolver_dns "$dns" "$dominio")
      sleep 1
      req2=$(resolver_dns "$dns" "$dominio")

      log_terminal "$loop" "$dns" "$dominio" "$req1" "$req2"

      registrar_csv "$DATA_HORA" "$dns" "$dominio" "req1" "$req1"
      registrar_csv "$DATA_HORA" "$dns" "$dominio" "req2" "$req2"

    done
  done

  [ "$loop" -lt "$DURACAO_MINUTOS" ] && sleep "$INTERVALO_SEGUNDOS"
done

echo
echo ">> Coleta finalizada."
