import sqlite3, json, os, pandas as pd, numpy as np
from datetime import datetime, timedelta
from config import DB_PATH

def _init_db():
    try:
        db_dir = os.path.dirname(DB_PATH); os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS dados_ativos (ticker TEXT PRIMARY KEY, dados TEXT, last_updated TIMESTAMP)')
        cursor.execute('CREATE TABLE IF NOT EXISTS watchlist (ticker TEXT PRIMARY KEY)')
        conn.commit(); conn.close()
    except Exception as e: print(f"[DB Manager] Erro CRÍTICO ao inicializar o DB: {e}")

def add_to_watchlist(ticker):
    _init_db(); conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO watchlist (ticker) VALUES (?)", (ticker,))
    conn.commit(); conn.close()

def remove_from_watchlist(ticker):
    _init_db(); conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
    conn.commit(); conn.close()

def get_watchlist():
    _init_db(); conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM watchlist")
    watchlist = [item[0] for item in cursor.fetchall()]
    conn.close(); return watchlist

def to_numeric_safe(value):
    try: return float(str(value).replace('.', '').replace(',', '.').replace('%', ''))
    except (ValueError, TypeError): return np.nan

def load_all_data_as_dataframe():
    _init_db(); conn = sqlite3.connect(DB_PATH)
    try:
        df_json = pd.read_sql_query("SELECT ticker, dados FROM dados_ativos", conn)
        if df_json.empty: return pd.DataFrame()
        data_list = [json.loads(d) for d in df_json['dados']]
        df = pd.DataFrame(data_list)
        essential_cols = ['Papel', 'Setor', 'Cotação', 'P/L', 'P/VP', 'ROE', 'Div.Yield', 'Dív.Líq/EBITDA', 'Marg. Líquida']
        for col in essential_cols:
            if col not in df.columns: df[col] = np.nan
        cols_to_convert = ['Cotação', 'P/L', 'P/VP', 'ROE', 'Div.Yield', 'Dív.Líq/EBITDA', 'Marg. Líquida']
        for col in cols_to_convert:
            df[col] = df[col].apply(to_numeric_safe)
            if 'ROE' in col or 'Yield' in col or 'Marg' in col: df[col] /= 100
        return df
    finally: conn.close()

def salvar_dados_ativo(ticker, data):
    _init_db()
    try:
        conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
        dados_json = json.dumps(data)
        cursor.execute('INSERT OR REPLACE INTO dados_ativos (ticker, dados, last_updated) VALUES (?, ?, ?)', (ticker, dados_json, datetime.now()))
        conn.commit(); conn.close()
    except Exception as e: print(f"[DB Manager] Erro CRÍTICO ao salvar dados para {ticker}: {e}")

def carregar_dados_ativo(ticker, max_age_hours=24):
    _init_db()
    try:
        conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
        cursor.execute("SELECT dados, last_updated FROM dados_ativos WHERE ticker = ?", (ticker,))
        result = cursor.fetchone()
        conn.close()
        if result:
            dados_json, last_updated_str = result
            if datetime.now() - datetime.fromisoformat(last_updated_str) < timedelta(hours=max_age_hours):
                return json.loads(dados_json)
        return None
    except Exception as e:
        print(f"[DB Manager] Erro CRÍTICO ao carregar dados para {ticker}: {e}")
        return None