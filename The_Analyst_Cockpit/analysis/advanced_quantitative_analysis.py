import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_collection.price_history import get_price_history

def calculate_advanced_metrics(ticker, ibov_ticker='^BVSP'):
    """Calcula rolling beta, rolling sharpe e max drawdown."""
    # Busca os dados de preços para o ativo e para o Ibovespa
    prices = get_price_history([ticker, ibov_ticker], period="2y")
    
    if prices is None or prices.empty or ticker not in prices.columns or ibov_ticker not in prices.columns:
        return None, None

    returns = prices.pct_change().dropna()
    
    # --- Cálculo do Max Drawdown ---
    cumulative_returns = (1 + returns[ticker]).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()

    # --- Cálculo das Métricas Rolling (Janela de 60 dias) ---
    window = 60
    if len(returns) < window:
        return max_drawdown, None # Retorna o drawdown, mas não as métricas rolling

    # Rolling Beta
    cov_rolling = returns[ticker].rolling(window=window).cov(returns[ibov_ticker])
    var_ibov_rolling = returns[ibov_ticker].rolling(window=window).var()
    rolling_beta = cov_rolling / var_ibov_rolling

    # Rolling Sharpe (assumindo taxa livre de risco de 0)
    rolling_std = returns[ticker].rolling(window=window).std()
    rolling_mean_return = returns[ticker].rolling(window=window).mean()
    # Anualiza o Sharpe
    rolling_sharpe = (rolling_mean_return / rolling_std) * np.sqrt(252)

    rolling_df = pd.DataFrame({
        'Rolling Beta': rolling_beta,
        'Rolling Sharpe': rolling_sharpe
    }).dropna()
    
    return max_drawdown, rolling_df

def run_advanced_quantitative_analysis(ticker):
    st.subheader("Análise Quantitativa Avançada")
    
    max_drawdown, rolling_df = calculate_advanced_metrics(ticker)

    if max_drawdown is None:
        st.warning(f"Não foi possível calcular as métricas avançadas para {ticker}. Dados históricos insuficientes.")
        return

    # Exibe o Max Drawdown
    st.metric(label="Drawdown Máximo (2 anos)", value=f"{max_drawdown:.2%}")

    if rolling_df is not None and not rolling_df.empty:
        # Gráfico do Rolling Beta
        fig_beta = go.Figure()
        fig_beta.add_trace(go.Scatter(x=rolling_df.index, y=rolling_df['Rolling Beta'], mode='lines', name='Beta Móvel (60d)'))
        fig_beta.update_layout(title="Beta Móvel vs. Ibovespa", yaxis_title="Beta")
        st.plotly_chart(fig_beta, use_container_width=True)

        # Gráfico do Rolling Sharpe
        fig_sharpe = go.Figure()
        fig_sharpe.add_trace(go.Scatter(x=rolling_df.index, y=rolling_df['Rolling Sharpe'], mode='lines', name='Sharpe Móvel (60d)', line=dict(color='orange')))
        fig_sharpe.update_layout(title="Sharpe Móvel Anualizado", yaxis_title="Sharpe Ratio")
        st.plotly_chart(fig_sharpe, use_container_width=True)
    else:
        st.info("Não há dados suficientes para calcular as métricas móveis (rolling).")