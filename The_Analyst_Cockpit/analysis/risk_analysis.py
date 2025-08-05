import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from data_collection.price_history import get_price_history

@st.cache_data(ttl=3600)
def calculate_risk_metrics(ticker, ibov_ticker='^BVSP'):
    """
    Busca dados históricos e calcula VaR e Beta.
    """
    try:
        # Pega 5 anos de dados para ter uma amostra robusta
        prices = get_price_history([ticker, ibov_ticker], period="5y")
        if prices is None or prices.empty or ticker not in prices.columns:
            return None, None, None

        returns = prices[ticker].pct_change().dropna()
        
        # 1. Cálculo do VaR Histórico
        var_95 = returns.quantile(0.05)
        var_99 = returns.quantile(0.01)
        
        # 2. Cálculo do Beta
        ibov_returns = prices[ibov_ticker].pct_change().dropna()
        aligned_returns, aligned_ibov = returns.align(ibov_returns, join='inner')
        
        covariance = aligned_returns.cov(aligned_ibov)
        variance_ibov = aligned_ibov.var()
        beta = covariance / variance_ibov if variance_ibov != 0 else np.nan
        
        return returns, {'var_95': var_95, 'var_99': var_99}, beta
    except Exception as e:
        print(f"[Análise de Risco] Erro ao calcular métricas para {ticker}: {e}")
        return None, None, None

@st.cache_data(ttl=86400)
def run_stress_test(beta):
    """
    Simula o impacto de crises históricas no ativo com base no seu Beta.
    """
    if beta is None or pd.isna(beta):
        return None
        
    # Períodos das crises (datas aproximadas do pico ao fundo)
    crises = {
        "Crise Financeira 2008": ('2008-05-20', '2008-10-27'),
        "Crise da COVID-19": ('2020-01-24', '2020-03-23')
    }
    
    ibov_prices = get_price_history('^BVSP', period="20y")
    if ibov_prices is None:
        return None

    results = {}
    for nome, (start, end) in crises.items():
        try:
            crisis_period = ibov_prices.loc[start:end]
            peak = crisis_period.max()
            trough = crisis_period.min()
            ibov_drawdown = (trough - peak) / peak
            asset_stress = ibov_drawdown * beta
            results[nome] = {'ibov_drawdown': ibov_drawdown, 'asset_stress': asset_stress}
        except Exception:
            continue
            
    return results

def run_risk_analysis(ticker, last_price):
    st.subheader("Análise de Risco de Mercado")
    
    returns, var_metrics, beta = calculate_risk_metrics(ticker)
    
    if returns is None:
        st.warning(f"Não foi possível calcular as métricas de risco para {ticker}. Dados históricos insuficientes.")
        return

    # Seção de Value at Risk (VaR)
    st.markdown("##### Value at Risk (VaR) Histórico - 1 Dia")
    col1, col2 = st.columns(2)
    col1.metric("VaR 95%", f"{var_metrics['var_95']:.2%}", help="Com 95% de confiança, a perda máxima esperada em 1 dia não deve exceder este valor.")
    col2.metric("VaR 99%", f"{var_metrics['var_99']:.2%}", help="Com 99% de confiança, a perda máxima esperada em 1 dia não deve exceder este valor.")

    # Histograma de Retornos
    fig = px.histogram(returns, x=returns.name, nbins=100, title="Distribuição dos Retornos Diários")
    fig.add_vline(x=var_metrics['var_95'], line_color="orange", line_dash="dash", annotation_text="VaR 95%")
    fig.add_vline(x=var_metrics['var_99'], line_color="red", line_dash="dash", annotation_text="VaR 99%")
    st.plotly_chart(fig, use_container_width=True)

    # Seção de Stress Test
    st.markdown("---")
    st.markdown("##### Simulação de Stress Test")
    stress_results = run_stress_test(beta)
    
    if stress_results:
        stress_df = pd.DataFrame(stress_results).T.rename(columns={'ibov_drawdown': 'Queda do Ibovespa', 'asset_stress': 'Queda Estimada do Ativo'})
        st.dataframe(stress_df.style.format('{:.2%}'), use_container_width=True)
        st.caption(f"A queda estimada do ativo é calculada como (Queda do Ibovespa * Beta do Ativo). Beta atual: {beta:.2f}")
    else:
        st.info("Não foi possível realizar a simulação de stress test.")