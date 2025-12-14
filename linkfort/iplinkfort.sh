echo "--- Super Benchmark de DNS (Linkfort vs Google vs Cloudflare) ---"
echo "Aguarde, calculando médias..."

# Lista com: Oficiais Linkfort + Descobertos no Nmap + Públicos
for ip in 138.97.220.58 138.97.220.62 138.97.220.57 138.97.220.60 138.97.220.65 138.97.220.66 138.97.220.69 138.97.220.70 8.8.8.8 1.1.1.1; do
    # Pega o tempo médio de 5 pings
    media=$(ping -c 5 -i 0.2 $ip | tail -1 | awk -F '/' '{print $5}')
    
    # Exibe o resultado organizado
    echo -e "IP: $ip \t| Média: ${media} ms"
done | sort -k 4 -n 
# O comando 'sort' no final já vai ordenar do mais rápido para o mais lento
