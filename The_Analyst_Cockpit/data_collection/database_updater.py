import streamlit as st
import time
from utils.b3_tickers import get_b3_tickers
from data_collection.fundamentus_scraper import get_fundamentus_data
from core.database_manager import salvar_dados_ativo

def update_full_database():
    """
    Itera sobre todos os tickers da B3, busca os dados no Fundamentus
    e salva na base de dados local.
    """
    tickers = get_b3_tickers()
    if not tickers:
        st.error("Não foi possível carregar a lista de tickers para a atualização.")
        return

    total_tickers = len(tickers)
    progress_bar = st.progress(0, text=f"A iniciar atualização para {total_tickers} ativos...")
    
    success_count = 0
    fail_count = 0
    
    for i, ticker_sa in enumerate(tickers):
        ticker = ticker_sa.replace('.SA', '')
        
        # Atualiza o texto da barra de progresso
        progress_bar.progress((i + 1) / total_tickers, text=f"A processar {ticker} ({i+1}/{total_tickers})... Sucessos: {success_count}, Falhas: {fail_count}")
        
        try:
            data = get_fundamentus_data(ticker)
            if data:
                salvar_dados_ativo(ticker, data)
                success_count += 1
            else:
                fail_count += 1
            
            time.sleep(0.2) # Pausa para não sobrecarregar o site do Fundamentus
            
        except Exception:
            fail_count += 1
            continue
            
    progress_bar.progress(1.0, text=f"Atualização Concluída! Sucessos: {success_count}, Falhas: {fail_count}")
    st.success(f"Base de dados atualizada. {success_count} ativos processados com sucesso.")