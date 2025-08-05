import pandas as pd
from config import B3_TICKERS_PATH
import os
import requests

def _fetch_and_save_full_ticker_list():
    print("[Tickers] A buscar lista completa de tickers da B3...")
    try:
        url = "https://www.fundamentus.com.br/resultado.php"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        df_list = pd.read_html(response.text, decimal=',', thousands='.')
        if not df_list: return None
        df = df_list[0]
        df['ticker'] = df['Papel'] + '.SA'
        os.makedirs(os.path.dirname(B3_TICKERS_PATH), exist_ok=True)
        df[['ticker']].to_csv(B3_TICKERS_PATH, index=False)
        print(f"-> Lista completa com {len(df)} tickers salva.")
        return df['ticker'].dropna().sort_values().tolist()
    except Exception as e:
        print(f"ERRO CRÍTICO ao buscar a lista de tickers: {e}")
        return None

def get_b3_tickers():
    try:
        if not os.path.exists(B3_TICKERS_PATH):
            print("AVISO: Ficheiro de tickers não encontrado. A iniciar busca online...")
            return _fetch_and_save_full_ticker_list()
        df = pd.read_csv(B3_TICKERS_PATH)
        return df['ticker'].dropna().sort_values().tolist()
    except Exception as e:
        print(f"ERRO ao carregar os tickers: {e}")
        return []