import csv
from collections import defaultdict
import os

ARQUIVO = "dados_dns_linkfort.csv"

def analisar_dados():
    if not os.path.exists(ARQUIVO):
        print(f"Arquivo {ARQUIVO} não encontrado. Rode o monitor primeiro.")
        return

    # Estrutura: dados[hora][ip] = [latencia1, latencia2, ...]
    dados_por_hora = defaultdict(lambda: defaultdict(list))

    with open(ARQUIVO, 'r') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            hora = linha['hora']
            ip = linha['ip']
            latencia = linha['latencia_media']

            if latencia and latencia != 'TIMEOUT':
                try:
                    dados_por_hora[hora][ip].append(float(latencia))
                except ValueError:
                    pass

    print("\n" + "="*50)
    print(f"{'HORA':<10} | {'MELHOR IP (VENCEDOR)':<20} | {'MÉDIA (ms)':<10}")
    print("="*50)

    # Ordena as horas (08, 09, 10...)
    horas_ordenadas = sorted(dados_por_hora.keys())

    for h in horas_ordenadas:
        medias_ips = []
        for ip, latencias in dados_por_hora[h].items():
            media_geral = sum(latencias) / len(latencias)
            medias_ips.append((ip, media_geral))
        
        # Ordena do menor para o maior (mais rápido primeiro)
        medias_ips.sort(key=lambda x: x[1])

        if medias_ips:
            vencedor_ip = medias_ips[0][0]
            vencedor_ms = medias_ips[0][1]
            print(f"{h+':00':<10} | {vencedor_ip:<20} | {vencedor_ms:.3f} ms")
            
            # Mostra o segundo lugar só para comparar
            if len(medias_ips) > 1:
                vice_ip = medias_ips[1][0]
                vice_ms = medias_ips[1][1]
                print(f"{'':<10} | {'(2º: '+vice_ip+')':<20} | {vice_ms:.3f} ms")
            print("-" * 50)

if __name__ == "__main__":
    analisar_dados()

