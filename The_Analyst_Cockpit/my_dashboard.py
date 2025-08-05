import streamlit as st
from config import APP_ICON
from core.database_manager import get_watchlist, load_all_data_as_dataframe
import pandas as pd

def run_app():
    st.title(f"{APP_ICON} Meu Dashboard (Watchlist)")
    
    watchlist = get_watchlist()
    if not watchlist:
        st.info("A sua Watchlist está vazia. Vá para a página de 'Análise de Ativo Individual' e clique em '⭐ Adicionar à Watchlist' para começar a acompanhar os seus ativos de interesse.")
        return

    df_full = load_all_data_as_dataframe()
    if df_full.empty:
        st.warning("A base de dados parece vazia. Vá à página do 'Stock Screener' e execute a 'Atualização da Base de Dados Completa'.")
        return

    df_watchlist = df_full[df_full['Papel'].isin(watchlist)].copy()
    
    if df_watchlist.empty:
        st.warning("Não foram encontrados dados para os ativos na sua Watchlist. Tente atualizar a base de dados.")
        return

    st.header("Resumo da Watchlist")
    cols_to_display = ['Papel', 'Cotação', 'P/L', 'P/VP', 'ROE', 'Div.Yield', 'Dív.Líq/EBITDA']
    existing_cols = [col for col in cols_to_display if col in df_watchlist.columns]
    df_display = df_watchlist[existing_cols].set_index('Papel')
    format_dict = {'P/L': '{:.2f}', 'P/VP': '{:.2f}', 'ROE': '{:.2%}', 'Div.Yield': '{:.2%}', 'Dív.Líq/EBITDA': '{:.2f}'}
    existing_format_dict = {k: v for k, v in format_dict.items() if k in df_display.columns}
    st.dataframe(df_display.style.format(existing_format_dict), use_container_width=True)