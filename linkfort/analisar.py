import csv
from collections import defaultdict
import os

ARQUIVO = "dados_dns_linkfort.csv"

def analisar_dados():
    if not os.path.exists(ARQUIVO):
        print(f"Arquivo {ARQUIVO} não encontrado. Rode o monitor primeiro.")
        return

    # Estrutura: dados[DATA][HORARIO][IP] = [lista de latencias]
    dados_gerais = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(ARQUIVO, 'r') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            data = linha['data']
            hora = linha['hora'] # Agora isso conterá "HH:MM"
            ip = linha['ip']
            latencia = linha['latencia_media']

            if latencia and latencia != 'TIMEOUT':
                try:
                    dados_gerais[data][hora][ip].append(float(latencia))
                except ValueError:
                    pass

    datas_ordenadas = sorted(dados_gerais.keys())

    for dia in datas_ordenadas:
        print(f"\n{'='*65}")
        print(f" RELATÓRIO DO DIA: {dia}")
        print(f"{'='*65}")
        # Ajustei o cabeçalho para 'HORÁRIO' pois agora inclui minutos
        print(f"{'HORÁRIO':<10} | {'MELHOR IP (VENCEDOR)':<20} | {'MÉDIA (ms)':<10}")
        print("-" * 65)

        # Ordena os horários (08:01, 08:02...)
        horas_do_dia = sorted(dados_gerais[dia].keys())

        for h in horas_do_dia:
            medias_ips = []
            for ip, latencias in dados_gerais[dia][h].items():
                media_geral = sum(latencias) / len(latencias)
                medias_ips.append((ip, media_geral))
            
            # Ordena do mais rápido para o mais lento
            medias_ips.sort(key=lambda x: x[1])

            if medias_ips:
                vencedor_ip = medias_ips[0][0]
                vencedor_ms = medias_ips[0][1]
                
                # Formatação visual ajustada
                print(f"{h:<10} | {vencedor_ip:<20} | {vencedor_ms:.3f} ms")
                
                if len(medias_ips) > 1:
                    vice_ip = medias_ips[1][0]
                    vice_ms = medias_ips[1][1]
                    print(f"{'':<10} | {'(2º: '+vice_ip+')':<20} | {vice_ms:.3f} ms")
                print("-" * 65)
        print("\n")

if __name__ == "__main__":
    analisar_dados()
