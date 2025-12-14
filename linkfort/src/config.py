import os

# --- CONIFIGURATION ---
THEME = {
    'bg': '#0f172a',        # Slate 900
    'card': '#1e293b',      # Slate 800
    'text': '#f8fafc',      # Slate 50
    'accent': '#38bdf8',    # Sky 400
    'success': '#4ade80',   # Green 400
    'danger': '#f87171',    # Red 400
    'border': '#334155',    # Slate 700
    'subtle': '#64748b'     # Slate 500
}

# Calculated from the parent directory of this file (src/config.py -> Linkfort root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(PROJECT_ROOT, "dados_dns_linkfort.csv")
JSON_OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'dados.json')
