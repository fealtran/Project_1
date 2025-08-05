import streamlit as st
from config import APP_ICON, APP_TITLE
from core.screener_logic import filter_stocks
from data_collection.database_updater import update_full_database
import pandas as pd

def run_app():
    st.title(f"{APP_ICON} Stock Screener")
    st.info("Filtre todo o mercado com base nos seus critérios fundamentalistas.")

    # --- Ferramenta de Atualização da Base de Dados ---
    with st.expander("Atualização da Base de Dados"):
        st.warning("O Screener funciona com os dados salvos localmente. Para garantir que os dados estão atualizados, execute a atualização em massa. Este processo pode demorar vários minutos.")
        if st.button("Atualizar Base de Dados Completa"):
            update_full_database()

    # --- Filtros do Screener ---
    st.header("Critérios de Filtragem")
    
    # Filtros em colunas para melhor organização
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pl_min, pl_max = st.slider("P/L", -100.0, 100.0, (0.0, 15.0), 0.1)
        roe_min = st.slider("ROE Mínimo (%)", -100.0, 100.0, 15.0, 0.5)
        
    with col2:
        pvp_min, pvp_max = st.slider("P/VP", 0.0, 50.0, (0.0, 2.0), 0.1)
        dy_min = st.slider("Dividend Yield Mínimo (%)", 0.0, 50.0, 5.0, 0.5)
        
    with col3:
        div_liq_ebitda_max = st.slider("Dív.Líq/EBITDA Máximo", -10.0, 20.0, 3.0, 0.1)
        mrg_liq_min = st.slider("Margem Líquida Mínima (%)", -100.0, 100.0, 10.0, 0.5)

    # Botão para executar a filtragem
    if st.button("Executar Screener", use_container_width=True, type="primary"):
        filters = {
            'P/L': (pl_min, pl_max),
            'ROE': roe_min,
            'P/VP': (pvp_min, pvp_max),
            'Div.Yield': dy_min,
            'Dív Líq / EBITDA': div_liq_ebitda_max,
            'Marg. Líquida': mrg_liq_min
        }
        
        with st.spinner("A filtrar a base de dados..."):
            results_df = filter_stocks(filters)
            st.session_state.screener_results = results_df

    # --- Exibição dos Resultados ---
    if 'screener_results' in st.session_state:
        results = st.session_state.screener_results
        st.header(f"Resultados: {len(results)} ativos encontrados")
        if not results.empty:
            # Formata o DataFrame para exibição
            display_df = results.copy()
            for col in ['ROE', 'Div.Yield', 'Marg. Líquida']:
                display_df[col] = (display_df[col] * 100).map('{:.2f}%'.format)
            
            st.dataframe(display_df, use_container_width=True)