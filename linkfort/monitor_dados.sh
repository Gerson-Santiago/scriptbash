#!/bin/bash
set -u

############################################
# CONFIGURAÇÕES
############################################

DOMINIO_TESTE="google.com"
INTERVALO=60            # segundos
DURACAO_TOTAL=3600      # 1 hora
AMOSTRAS=3

CSV="$HOME/scriptbash/dados_dns_linkfort.csv"

DNS_SERVERS=(
  "138.97.220.58"
  "138.97.220.62"
  "138.97.220.57"
  "138.97.220.60"
  "138.97.220.65"
  "138.97.220.66"
  "138.97.220.69"
  "138.97.220.70"
  "8.8.8.8"
  "8.8.4.4"
  "1.1.1.1"
  "1.0.0.1"
  "9.9.9.9"
  "149.112.112.112"
)

############################################
# FUNÇÕES DE DEPENDÊNCIA
############################################

verificar_comando() {
  command -v "$1" >/dev/null 2>&1
}

instalar_pacote() {
  local pacote="$1"

  echo ">> Instalando pacote necessário: $pacote"
  sudo apt update -y >/dev/null
  sudo apt install -y "$pacote"
}

verificar_dependencias() {
  echo ">> Verificando dependências..."

  if ! verificar_comando dig; then
    instalar_pacote dnsutils
  fi

  if ! verificar_comando bc; then
    instalar_pacote bc
  fi

  echo ">> Dependências OK"
}

############################################
# FUNÇÕES PRINCIPAIS
############################################

media_tempo_dns() {
  local dns="$1"
  local soma=0
  local sucesso=0

  for ((i=1; i<=AMOSTRAS; i++)); do
    local tempo
    tempo=$(dig @"$dns" "$DOMINIO_TESTE" +stats +time=2 +tries=1 \
      | awk '/Query time/ {print $4}')

    if [[ "$tempo" =~ ^[0-9]+$ ]]; then
      soma=$(echo "$soma + $tempo" | bc)
      sucesso=$((sucesso + 1))
    fi
  done

  if [[ $sucesso -gt 0 ]]; then
    echo "scale=2; $soma / $sucesso" | bc
  else
    echo ""
  fi
}

############################################
# EXECUÇÃO
############################################

verificar_dependencias

echo "=== Iniciando Coleta de Performance DNS ==="
echo "Duração: 1h | Intervalo: 1min"
echo "Amostras por DNS: $AMOSTRAS"
echo "Domínio de teste: $DOMINIO_TESTE"
echo "CSV: $CSV"
echo

if [[ ! -f "$CSV" ]]; then
  echo "timestamp,dns,tempo_ms" > "$CSV"
fi

INICIO=$(date +%s)

while true; do
  AGORA=$(date +%s)
  [[ $((AGORA - INICIO)) -ge $DURACAO_TOTAL ]] && break

  TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

  echo "--- Teste às $TIMESTAMP ---"

  for dns in "${DNS_SERVERS[@]}"; do
    media=$(media_tempo_dns "$dns")

    if [[ -n "$media" ]]; then
      echo "   $dns | ${media} ms ($AMOSTRAS/$AMOSTRAS)"
      echo "$TIMESTAMP,$dns,$media" >> "$CSV"
    else
      echo "   $dns | timeout"
      echo "$TIMESTAMP,$dns," >> "$CSV"
    fi
  done

  echo "Dados salvos. Próximo ciclo em $((INTERVALO / 60)) minuto(s)."
  echo
  sleep "$INTERVALO"
done
