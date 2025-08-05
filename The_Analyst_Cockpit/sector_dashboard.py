import streamlit as st
from config import APP_ICON
from core.database_manager import load_all_data_as_dataframe
from data_collection.price_history import get_price_history
import pandas as pd
import plotly.express as px

def run_app():
    st.title(f"{APP_ICON} Super Dashboard Setorial")
    st.info("Analise, compare e descubra os destaques de cada setor da bolsa.")
    df = load_all_data_as_dataframe()

    if df.empty or 'Setor' not in df.columns:
        st.warning("A base de dados parece vazia. Vá à página do 'Stock Screener' e execute a 'Atualização da Base de Dados Completa'.")
        return

    setores = sorted(df['Setor'].dropna().unique())
    selected_sector = st.selectbox("1. Selecione um Setor para Análise:", setores)
    if not selected_sector: return

    df_sector = df[df['Setor'] == selected_sector].copy()
    st.header(f"Análise do Setor: {selected_sector} ({len(df_sector)} empresas na base)")

    st.subheader("🏆 Destaques do Setor")
    cols_best = st.columns(4)
    def get_top3(df, metric, ascending): return df.sort_values(by=metric, ascending=ascending).head(3)[['Papel', metric]]
    if 'ROE' in df_sector: cols_best[0].write("**Maior ROE:**"); cols_best[0].dataframe(get_top3(df_sector, 'ROE', False))
    if 'Div.Yield' in df_sector: cols_best[1].write("**Maior Div. Yield:**"); cols_best[1].dataframe(get_top3(df_sector, 'Div.Yield', False))
    if 'P/L' in df_sector: cols_best[2].write("**Menor P/L:**"); cols_best[2].dataframe(get_top3(df_sector[df_sector['P/L'] > 0], 'P/L', True))
    if 'P/VP' in df_sector: cols_best[3].write("**Menor P/VP:**"); cols_best[3].dataframe(get_top3(df_sector[df_sector['P/VP'] > 0], 'P/VP', True))

    st.subheader("Performance Histórica (Último Ano)")
    with st.spinner("A calcular a performance do setor..."):
        tickers_sa = [f"{ticker}.SA" for ticker in df_sector['Papel']]
        if tickers_sa:
            ibov_prices = get_price_history('^BVSP', period="1y")
            sector_prices = get_price_history(tickers_sa, period="1y")
            if sector_prices is not None and not sector_prices.empty and ibov_prices is not None:
                sector_returns = sector_prices.pct_change().mean(axis=1)
                sector_cumulative = (1 + sector_returns).cumprod()
                ibov_cumulative = (1 + ibov_prices.pct_change()).cumprod()
                df_performance = pd.DataFrame({'Setor': sector_cumulative, 'Ibovespa': ibov_cumulative}).dropna()
                st.line_chart(df_performance)

    st.subheader("Análise Comparativa Visual")
    cols_scatter = [col for col in ['P/L', 'P/VP', 'ROE', 'Div.Yield', 'Marg. Líquida', 'Dív.Líq/EBITDA'] if col in df_sector.columns]
    if len(cols_scatter) >= 2:
        col_x, col_y = st.columns(2)
        x_axis = col_x.selectbox("Eixo X:", cols_scatter, index=0)
        y_axis = col_y.selectbox("Eixo Y:", cols_scatter, index=2)
        df_chart = df_sector.dropna(subset=[x_axis, y_axis])
        if not df_chart.empty:
            fig = px.scatter(df_chart, x=x_axis, y=y_axis, text='Papel', title=f"{x_axis} vs. {y_axis} do Setor")
            fig.update_traces(textposition='top center', textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)