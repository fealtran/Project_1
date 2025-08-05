
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta
import numbers
import os

# --- INÍCIO DO CÓDIGO DE DESIGN (CSS E COMPONENTES) ---
def apply_global_style():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    body { background-color: #0d1117 !important; background-image: radial-gradient(circle at 1px 1px, #1c1f2b 1px, transparent 0); background-size: 25px 25px !important; color: #ffffff !important; }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-weight: 700; color: #ffffff; }
    h3 { border-bottom: 2px solid #00BFFF; padding-bottom: 8px; margin-top: 20px;}
    [data-testid="stSidebar"] { background-color: rgba(13, 17, 23, 0.8); backdrop-filter: blur(5px); border-right: 1px solid #00BFFF; }
    .metric-card { background: rgba(28, 31, 43, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 12px; padding: 15px; border: 1px solid rgba(0, 191, 255, 0.3); transition: all 0.3s ease; }
    .metric-card:hover { transform: translateY(-3px); border-color: #FF00FF; box-shadow: 0 8px 40px rgba(255, 0, 255, 0.2); }
    .metric-card h5 { margin: 0 0 8px 0; color: #a1a1a1; font-size: 14px; font-weight: 500;}
    .metric-card .value { font-size: 24px; font-weight: 700; color: #ffffff; line-height: 1.2; }
    .metric-card .caption { font-size: 12px; color: #808080; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { padding: 12px; background-color: transparent; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #FF00FF; }
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# --- INÍCIO DOS FORNECEDORES DE DADOS (DATA PROVIDERS) ---
@st.cache_data(ttl=3600)
def get_sgs_data(code, days_ago=730):
    end_date = datetime.now(); start_date = end_date - timedelta(days=days_ago)
    url = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={start_date.strftime("%d/%m/%Y")}&dataFinal={end_date.strftime("%d/%m/%Y")}'
    try:
        df = pd.read_json(url); df['data'] = pd.to_datetime(df['data'], dayfirst=True); df.set_index('data', inplace=True)
        if df.empty: return None
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').dropna(); return df
    except: return None

TICKERS = {
    'Índices':{'^BVSP':'Ibovespa','^GSPC':'S&P 500','^IXIC':'Nasdaq','^VIX':'VIX (Volatilidade)', 'EWZ': 'Risco-País (EWZ)'}, 
    'Moedas':{'USDBRL=X':'Dólar (USD/BRL)', 'EURUSD=X':'Euro (EUR/USD)', 'GBPUSD=X':'Libra (GBP/USD)'}, 
    'Commodities':{'BZ=F':'Petróleo Brent', 'GC=F':'Ouro', 'SI=F':'Prata'}
}
@st.cache_data(ttl=900)
def get_market_data(category, period="3mo"):
    t_list = list(TICKERS[category].keys())
    try:
        data = yf.download(t_list, period=period, progress=False)
        if data.empty: return None
        close_data = data.get('Close') if isinstance(data.columns, pd.MultiIndex) else data[['Close']].rename(columns={'Close':t_list[0]})
        return close_data.dropna(how='all')
    except: return None

# --- INÍCIO DA LÓGICA DA PÁGINA ---
st.set_page_config(layout="wide"); apply_global_style()
st.title("Quantum Cockpit 퀀텀")

# ... (O resto da lógica da página permanece aqui)
