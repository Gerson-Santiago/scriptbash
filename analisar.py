import csv
from collections import defaultdict
import os

ARQUIVO = "dados_dns_linkfort.csv"

def analisar_dados():
    if not os.path.exists(ARQUIVO):
        print(f"Arquivo {ARQUIVO} não encontrado. Rode o monitor primeiro.")
        return

    # Nova Estrutura: dados[DATA][HORA][IP] = [lista de latencias]
    # Isso garante que não misturemos dias diferentes
    dados_gerais = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(ARQUIVO, 'r') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            data = linha['data'] # Agora lemos a coluna data
            hora = linha['hora']
            ip = linha['ip']
            latencia = linha['latencia_media']

            if latencia and latencia != 'TIMEOUT':
                try:
                    # Agrupa primeiro pelo dia, depois pela hora
                    dados_gerais[data][hora][ip].append(float(latencia))
                except ValueError:
                    pass

    # Ordena as datas (para mostrar o histórico cronológico: ontem -> hoje)
    datas_ordenadas = sorted(dados_gerais.keys())

    for dia in datas_ordenadas:
        print(f"\n{'='*60}")
        print(f" RELATÓRIO DO DIA: {dia}")
        print(f"{'='*60}")
        print(f"{'HORA':<10} | {'MELHOR IP (VENCEDOR)':<20} | {'MÉDIA (ms)':<10}")
        print("-" * 60)

        # Dentro do dia, ordena as horas (06, 07, 08...)
        horas_do_dia = sorted(dados_gerais[dia].keys())

        for h in horas_do_dia:
            medias_ips = []
            for ip, latencias in dados_gerais[dia][h].items():
                media_geral = sum(latencias) / len(latencias)
                medias_ips.append((ip, media_geral))
            
            # Ordena do menor para o maior (mais rápido vence)
            medias_ips.sort(key=lambda x: x[1])

            if medias_ips:
                vencedor_ip = medias_ips[0][0]
                vencedor_ms = medias_ips[0][1]
                print(f"{h+':00':<10} | {vencedor_ip:<20} | {vencedor_ms:.3f} ms")
                
                # Mostra o segundo lugar
                if len(medias_ips) > 1:
                    vice_ip = medias_ips[1][0]
                    vice_ms = medias_ips[1][1]
                    print(f"{'':<10} | {'(2º: '+vice_ip+')':<20} | {vice_ms:.3f} ms")
                print("-" * 60)
        print("\n")

if __name__ == "__main__":
    analisar_dados()
