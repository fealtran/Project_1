
import pandas as pd; import yfinance as yf; import streamlit as st
@st.cache_data(ttl=600)
def get_market_data(period="1y"):
    tickers = {"IBOV": "^BVSP", "SMLL": "SMLL.SA", "Dolar": "USDBRL=X", "VIX": "^VIX", "US 10Y": "^TNX",
               "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Petroleo": "CL=F", "Metais (XME)": "XME",
               "DXY": "DX-Y.NYB", "EEM": "EEM", "EFA": "EFA"}
    data, hist_data = {}, yf.download(list(tickers.values()), period=period, progress=False)
    for name, ticker in tickers.items():
        try:
            series = hist_data['Close'][ticker].dropna() if isinstance(hist_data.columns, pd.MultiIndex) else hist_data[ticker].dropna()
            if len(series) < 2: data[name] = None; continue
            last, prev = series.iloc[-1], series.iloc[-2]
            data[name] = {"value": last, "change": last - prev, "change_percent": ((last - prev) / prev) * 100, "ticker": ticker, "history": series}
        except Exception: data[name] = None
    return data
