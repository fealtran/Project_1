
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

@st.cache_resource
def get_ticker(ticker_symbol):
    return yf.Ticker(ticker_symbol)

@st.cache_data(ttl="1h")
def get_financial_indicators(ticker_symbol_sa):
    ticker = get_ticker(ticker_symbol_sa)

    info = ticker.info
    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    if financials.empty or balance_sheet.empty:
        return {"error": "Dados de DRE ou Balanço não encontrados."}

    # --- CORREÇÃO DA KEYERROR: Usando o nome correto da API ---
    total_equity = balance_sheet.get('Stockholders Equity', pd.Series([0])).iloc[0]

    # Lógica de EBITDA mais segura
    ebitda = financials.get('Normalized EBITDA', pd.Series([0])).iloc[0]
    if ebitda == 0 and 'EBIT' in financials.index and 'Depreciation And Amortization' in cash_flow.index:
         ebitda = financials.loc['EBIT'].iloc[0] + cash_flow.loc['Depreciation And Amortization'].iloc[0]

    net_income = financials.get('Net Income', pd.Series([0])).iloc[0]
    total_revenue = financials.get('Total Revenue', pd.Series([0])).iloc[0]
    total_assets = balance_sheet.get('Total Assets', pd.Series([0])).iloc[0]
    net_debt = balance_sheet.get('Net Debt', pd.Series([0])).iloc[0]

    roe = net_income / total_equity if total_equity else 0
    lucratividade = net_income / total_revenue if total_revenue else 0
    eficiencia = total_revenue / total_assets if total_assets else 0
    alavancagem = total_assets / total_equity if total_equity else 0
    div_liq_ebitda = net_debt / ebitda if ebitda else 0

    return {
        "ROE (Calculado)": roe, "Lucratividade": lucratividade, "Eficiência": eficiencia,
        "Alavancagem": alavancagem, "Dív. Líq. / EBITDA": div_liq_ebitda,
        "Preço Atual": info.get('regularMarketPrice', 0),
        "Nome da Empresa": info.get('longName', 'N/A')
    }
# O resto do arquivo (get_historical_multiples, calculate_gordon_inputs) permanece o mesmo
# por simplicidade, vamos reescrever apenas a função problemática. As outras serão mantidas.

def get_historical_multiples(ticker_symbol_sa):
    ticker = get_ticker(ticker_symbol_sa)
    hist_price = ticker.history(period="5y")
    quarterly_financials = ticker.quarterly_financials
    if quarterly_financials.empty: return pd.DataFrame()
    shares_outstanding = ticker.info.get('sharesOutstanding')
    if not shares_outstanding: return pd.DataFrame()

    eps_quarterly = quarterly_financials.loc['Net Income'] / shares_outstanding
    eps_quarterly.index = eps_quarterly.index.to_period('Q').to_timestamp('Q-DEC')
    eps_ttm = eps_quarterly.rolling(window=4).sum().dropna()

    df = pd.DataFrame(hist_price['Close'])
    df['EPS_TTM'] = eps_ttm
    df['EPS_TTM'] = df['EPS_TTM'].ffill()
    df.dropna(inplace=True)
    df['P/L'] = df['Close'] / df['EPS_TTM']
    return df[['P/L']]

@st.cache_data(ttl="1h")
def calculate_gordon_inputs(ticker_symbol_sa):
    ticker = get_ticker(ticker_symbol_sa)

    RISK_FREE_RATE = 0.105
    ibov_hist = get_ticker('^BVSP').history(period='5y')
    market_return_annual = (1 + ibov_hist['Close'].pct_change().mean())**252 - 1

    beta = ticker.info.get('beta', 1.0)
    k = RISK_FREE_RATE + beta * (market_return_annual - RISK_FREE_RATE)

    dividends = ticker.dividends
    if len(dividends) > 1:
        dividends_yearly = dividends.resample('YE').sum()
        dividends_yearly = dividends_yearly[dividends_yearly > 0].dropna()

        if len(dividends_yearly) > 1:
            start_value = dividends_yearly.iloc[0]
            end_value = dividends_yearly.iloc[-1]
            num_years = len(dividends_yearly) - 1
            g = (end_value / start_value)**(1 / num_years) - 1 if num_years > 0 else 0
        else: g = 0.0
    else: g = 0.0

    return {'k': k if k > 0 else 0, 'g': g if g >= 0 else 0}
