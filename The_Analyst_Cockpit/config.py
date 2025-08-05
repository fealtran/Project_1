import os
# Define o diretório base do projeto de forma dinâmica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Caminhos Essenciais ---
# Garante que os caminhos funcionem em qualquer ambiente
DB_PATH = os.path.join(BASE_DIR, 'database', 'dados.db')
B3_TICKERS_PATH = os.path.join(BASE_DIR, 'data', 'b3_tickers.csv')

# --- Configurações da Aplicação ---
APP_TITLE = "Plataforma de Análise de Ativos"
APP_ICON = "📈"
DEFAULT_TICKER = 'PETR4.SA'