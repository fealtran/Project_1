
import streamlit as st; import pandas as pd; import yfinance as yf
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
    except Exception as e:
        st.error(f"Erro ao buscar dados de mercado: {e}")
        return None
