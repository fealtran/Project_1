import streamlit as st
from config import APP_ICON
from core.database_manager import load_all_data_as_dataframe
from data_collection.price_history import get_price_history
from analysis.scoring import calculate_score
import pandas as pd
import plotly.express as px

def run_app():
    st.title(f"{APP_ICON} Quadrante de Mercado")
    st.info("Visualize o mercado com base na Qualidade (Score Fundamentalista) vs. Momentum (Performance do Preço).")
    df_full = load_all_data_as_dataframe()
    if df_full.empty:
        st.warning("A base de dados parece vazia. Vá à página do 'Stock Screener' e execute a 'Atualização da Base de Dados Completa'.")
        return
    
    with st.spinner("A calcular scores e momentum para todo o mercado..."):
        df_full['Score'] = df_full.apply(lambda row: calculate_score(row.to_dict())[0], axis=1)
        tickers_sa = [f"{ticker}.SA" for ticker in df_full['Papel']]
        prices_1y = get_price_history(tickers_sa, period="1y")
        if prices_1y is not None:
            returns_1y = (prices_1y.iloc[-1] / prices_1y.iloc[0]) - 1
            returns_1y.name = "Momentum_12M"
            
            # --- CORREÇÃO APLICADA AQUI ---
            # Remove o sufixo .SA do índice de retornos para a junção funcionar
            returns_1y.index = returns_1y.index.str.replace('.SA', '')
            df_full = df_full.set_index('Papel').join(returns_1y).reset_index()

    df_plot = df_full.dropna(subset=['Score', 'Momentum_12M'])
    if df_plot.empty:
        st.warning("Não há dados suficientes para gerar o gráfico do quadrante. Tente atualizar a base de dados.")
        return
    
    st.header("Análise de Quadrantes: Qualidade vs. Momentum")
    median_score = df_plot['Score'].median()
    median_momentum = df_plot['Momentum_12M'].median()
    fig = px.scatter(df_plot, x='Momentum_12M', y='Score', text='Papel', color='Setor', title='Qualidade vs. Momentum')
    fig.update_traces(textposition='top center', textfont_size=10)
    fig.add_hline(y=median_score, line_dash="dot", annotation_text=f"Mediana Qualidade ({median_score:.0f})")
    fig.add_vline(x=median_momentum, line_dash="dot", annotation_text=f"Mediana Momentum ({median_momentum:.1%})")
    st.plotly_chart(fig, use_container_width=True, height=700)