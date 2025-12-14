import csv
from collections import defaultdict
import os
import statistics

# --- CONFIGURAÇÕES VISUAIS ---
ARQUIVO = "dados_dns_linkfort.csv"

# Cores ANSI
R = "\033[0m"       # Reset
BD = "\033[1m"      # Negrito
GR = "\033[92m"     # Verde
YL = "\033[93m"     # Amarelo
RD = "\033[91m"     # Vermelho
CY = "\033[96m"     # Ciano
DIM = "\033[2m"     # Escuro (para bordas)

# --- CONFIGURAÇÕES DE ALGORITMO ---
PESO_JITTER = 1.5   # 1ms Jitter = 1.5ms latência no score
PENALIDADE_PERDA = 1000 # Penalidade severa para perda de pacotes

def carregar_dados():
    if not os.path.exists(ARQUIVO):
        print(f"{RD}Arquivo {ARQUIVO} não encontrado.{R}")
        return None

    stats = defaultdict(list)
    falhas = defaultdict(int)

    with open(ARQUIVO, 'r') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            ip = linha['ip']
            latencia = linha['latencia_media']
            if latencia == 'TIMEOUT':
                falhas[ip] += 1
            else:
                try:
                    stats[ip].append(float(latencia))
                except ValueError: pass
    return stats, falhas

def calcular_score(media, jitter, perda_percentual):
    """
    Calcula o índice de qualidade. Menor é melhor.
    Score = Media + (Jitter * Peso) + (Perda * Penalidade)
    """
    return media + (jitter * PESO_JITTER) + (perda_percentual * PENALIDADE_PERDA)

def print_row(c1, c2, c3, c4, c5, c6, c7, c8):
    # Imprime a linha da tabela com larguras ajustadas para < 83 colunas
    b = f"{DIM}│{R}" # Border
    # Montagem da string formatada
    line = (f"{b}{c1}{b}{c2}{b}{c3}{b}{c4}{b}{c5}{b}{c6}{b}{c7}{b}{c8}{b}")
    print(line)

def print_conclusion_line(label, ip, ip_color, info_text, target_width):
    border = f"{DIM}│{R}"
    # Raw text para cálculo de padding (sem códigos de cor)
    raw_text = f" ✅ {label}: {ip} ({info_text})"
    
    # Ajuste: emoji vale 1 no len() mas ocupa 2 espaços visuais
    visual_correction = 1 
    padding = target_width - len(raw_text) - visual_correction
    if padding < 0: padding = 0
    
    line = (f"{border} ✅ {label}: {ip_color}{ip}{R} "
            f"({info_text}){' ' * padding}{border}")
    print(line)

def gerar_relatorio():
    dados = carregar_dados()
    if not dados: return

    stats_ip, falhas_ip = dados
    ranking = []

    for ip, latencias in stats_ip.items():
        if latencias:
            media = statistics.mean(latencias)
            total_pcts = len(latencias) + falhas_ip[ip]
            if len(latencias) > 1:
                jitter = statistics.stdev(latencias)
            else:
                jitter = 0.0
            
            if total_pcts > 0:
                loss = (falhas_ip[ip] / total_pcts) * 100
            else:
                loss = 0
            
            # Cálculo do Score Inteligente
            score = calcular_score(media, jitter, loss)

            ranking.append({
                'ip': ip,
                'media': media,
                'min': min(latencias),
                'max': max(latencias),
                'jitter': jitter,
                'loss': loss,
                'score': score
            })

    # ORDENAÇÃO PELO SCORE (Qualidade Global)
    ranking.sort(key=lambda x: x['score'])

    print("\n")
    print(f" {BD}🏆 RELATÓRIO DE PERFORMANCE (Algoritmo: Estabilidade){R}")
    
    # --- TABELA PRINCIPAL (LARGURA TOTAL: 79 chars) ---
    # Cols: POS(4) IP(16) MED(10) JIT(10) MIN(7) MAX(7) LOS(7) SCR(9)
    
    top_border = (
        f"{DIM}┌────┬────────────────┬──────────┬──────────┬───────"
        f"┬───────┬───────┬─────────┐{R}"
    )
    
    mid_border = (
        f"{DIM}├────┼────────────────┼──────────┼──────────┼───────"
        f"┼───────┼───────┼─────────┤{R}"
    )
    
    bot_border = (
        f"{DIM}└────┴────────────────┴──────────┴──────────┴───────"
        f"┴───────┴───────┴─────────┘{R}"
    )

    h1 = f"{BD}{'POS':^4}{R}"
    h2 = f"{BD}{'SERVIDOR (IP)':^16}{R}"
    h3 = f"{BD}{'MEDIA(ms)':^10}{R}"
    h4 = f"{BD}{'JITTER':^10}{R}"
    h5 = f"{BD}{'MIN':^7}{R}"
    h6 = f"{BD}{'MAX':^7}{R}"
    h7 = f"{BD}{'PERDA':^7}{R}"
    h8 = f"{BD}{'SCORE':^9}{R}"
    
    print(top_border)
    print_row(h1, h2, h3, h4, h5, h6, h7, h8)
    print(mid_border)

    for i, item in enumerate(ranking, 1):
        pos_str = f"#{i:02d}"
        pos_fmt = f"{pos_str:^4}"
        
        cor_ip = R
        if i <= 3: cor_ip = BD

        ip_fmt = f"{cor_ip}{item['ip']:<16}{R}"
        media_fmt = f"{item['media']:>9.1f} "

        jit_val = item['jitter']
        jit_txt = f"±{jit_val:.1f}"
        jit_padded = f"{jit_txt:>9} " 
        if jit_val > 5.0:   jit_fmt = f"{RD}{jit_padded}{R}"
        elif jit_val > 2.0: jit_fmt = f"{YL}{jit_padded}{R}"
        else:               jit_fmt = jit_padded

        min_fmt = f"{item['min']:>6.0f} "
        max_fmt = f"{item['max']:>6.0f} "
        
        loss_val = item['loss']
        loss_txt = f"{loss_val:.0f}%"
        loss_padded = f"{loss_txt:>6} "
        if loss_val > 0: loss_fmt = f"{RD}{BD}{loss_padded}{R}"
        else:            loss_fmt = f"{GR}{loss_padded}{R}"

        score_val = item['score']
        score_padded = f"{score_val:>8.2f} "
        # O Campeão ganha destaque
        if i == 1: score_fmt = f"{GR}{BD}{score_padded}{R}" 
        else:      score_fmt = f"{score_padded}"

        print_row(pos_fmt, ip_fmt, media_fmt, jit_fmt, min_fmt, max_fmt,
                  loss_fmt, score_fmt)

    print(bot_border)

    # --- TABELA DE CONCLUSÃO ---
    melhor = ranking[0]
    segundo = ranking[1] if len(ranking) > 1 else None
    
    # Largura Interna ajustada (79 chars totais - 2 bordas = 77)
    INNER_WIDTH = 77

    print(f"\n{DIM}┌{'─' * INNER_WIDTH}┐{R}")
    
    title = "💡 CONCLUSÃO TÉCNICA:"
    visual_correction = 1 
    pad_len = INNER_WIDTH - len(title) - 1 - visual_correction
    
    print(f"{DIM}│{R} {BD}{title}{R}{' ' * pad_len}{DIM}│{R}")
    print(f"{DIM}├{'─' * INNER_WIDTH}┤{R}")
    
    info1 = (f"Score: {melhor['score']:.2f} | Med: {melhor['media']:.0f}ms "
             f"| Jit: ±{melhor['jitter']:.1f}")
    print_conclusion_line("DNS Primário  ", melhor['ip'], GR, info1, INNER_WIDTH)

    if segundo:
        diff_score = segundo['score'] - melhor['score']
        info2 = f"Diff Score: +{diff_score:.2f} (Backup)"
        print_conclusion_line("DNS Secundário", segundo['ip'], GR, info2,
                              INNER_WIDTH)

    print(f"{DIM}└{'─' * INNER_WIDTH}┘{R}\n")

if __name__ == "__main__":
    gerar_relatorio()
