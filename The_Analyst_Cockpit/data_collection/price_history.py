import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data(ttl=3600)
def get_price_history(tickers, period="1y"):
    try:
        if not isinstance(tickers, list): tickers = [tickers]
        data = yf.download(tickers, period=period, progress=False)
        if data.empty: return None
        
        close_prices = data['Close']
        # Se for um único ticker, yfinance pode retornar uma Série, o que é bom.
        # Se forem múltiplos, retorna um DataFrame. Se for um só numa lista, pode retornar um DF com uma coluna.
        # Esta linha garante que, se houver apenas uma coluna, ela seja convertida numa Série.
        if isinstance(close_prices, pd.DataFrame) and len(close_prices.columns) == 1:
            return close_prices.iloc[:, 0]
        return close_prices
    except Exception as e:
        print(f"[Price History] Erro ao buscar preços para {tickers}: {e}")
        return None