import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
# ... (função calculate_cagr e get_historical_data continuam as mesmas) ...
def calculate_cagr(end_value, start_value, periods):
    if start_value is None or end_value is None or start_value <= 0 or periods <= 0: return np.nan
    return (end_value / start_value) ** (1 / periods) - 1
@st.cache_data(ttl=86400)
def get_historical_data(ticker):
    try:
        stock = yf.Ticker(ticker); income_stmt = stock.income_stmt
        if income_stmt.empty: return None
        years = income_stmt.columns[:4]
        data = {
            'Ano': years.year,
            'Receita (R$)': [income_stmt.loc['Total Revenue', year] if 'Total Revenue' in income_stmt.index else np.nan for year in years],
            'Lucro Líquido (R$)': [income_stmt.loc['Net Income', year] if 'Net Income' in income_stmt.index else np.nan for year in years],
        }
        df = pd.DataFrame(data).set_index('Ano').dropna().sort_index()
        return df if not df.empty else None
    except Exception: return None

def run_historical_analysis(ticker):
    st.subheader("Análise Histórica (Últimos Anos Disponíveis)")
    data_df = get_historical_data(ticker)
    
    if data_df is None or len(data_df) < 2:
        st.warning(f"Não foi possível obter dados históricos suficientes para {ticker}.")
        return None # Retorna None se não houver dados/gráfico

    periods = len(data_df) - 1
    cagr_receita = calculate_cagr(data_df['Receita (R$)'].iloc[-1], data_df['Receita (R$)'].iloc[0], periods)
    cagr_lucro = calculate_cagr(data_df['Lucro Líquido (R$)'].iloc[-1], data_df['Lucro Líquido (R$)'].iloc[0], periods)

    col1, col2 = st.columns(2)
    col1.metric("CAGR da Receita", f"{cagr_receita:.2%}" if pd.notna(cagr_receita) else "N/A")
    col2.metric("CAGR do Lucro", f"{cagr_lucro:.2%}" if pd.notna(cagr_lucro) else "N/A")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=data_df.index, y=data_df['Receita (R$)'], name='Receita'))
    fig.add_trace(go.Bar(x=data_df.index, y=data_df['Lucro Líquido (R$)'], name='Lucro Líquido'))
    fig.update_layout(title_text="Evolução da Receita e Lucro Líquido", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    return fig # RETORNA O GRÁFICO PARA O RELATÓRIO