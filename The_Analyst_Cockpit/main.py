import streamlit as st
from config import *
from utils.b3_tickers import get_b3_tickers
from core.database_manager import carregar_dados_ativo, salvar_dados_ativo, add_to_watchlist, remove_from_watchlist, get_watchlist
from analysis.quantitative import run_quantitative_analysis
from analysis.valuation_models import run_valuation_analysis
from analysis.historical_analysis import run_historical_analysis
from analysis.sector_analysis import run_sector_analysis
from analysis.advanced_quantitative_analysis import run_advanced_quantitative_analysis
from analysis.risk_analysis import run_risk_analysis
from analysis.scoring import calculate_score
from analysis.insights import generate_insights
from analysis.dupont_analysis import run_dupont_analysis
from analysis.historical_multiples import run_historical_multiples_analysis # Importa a nova análise

def run_app():
    # ... (código da sidebar e da página inicial continua o mesmo) ...
    with st.sidebar:
        st.header("Configurações de Análise")
        tickers_list = get_b3_tickers()
        if not tickers_list: st.error("Carregue a lista de tickers primeiro (no Screener)."); return
        selected_ticker = st.selectbox("1. Selecione o Ativo Principal:", tickers_list, index=tickers_list.index(DEFAULT_TICKER) if DEFAULT_TICKER in tickers_list else 0)
        peers_list = [t for t in tickers_list if t != selected_ticker]
        selected_peers = st.multiselect("2. (Opcional) Selecione Pares para Comparação:", peers_list)
        if st.button("Analisar", use_container_width=True, type="primary"):
            st.session_state.ticker_to_analyze = selected_ticker; st.session_state.peers_to_analyze = selected_peers
    if 'ticker_to_analyze' not in st.session_state:
        st.title(f"{APP_ICON} {APP_TITLE}"); st.info("Selecione um ativo na barra lateral e clique em 'Analisar' para começar."); return

    ticker = st.session_state.ticker_to_analyze
    ticker_clean = ticker.replace('.SA', '')
    main_ticker_data = carregar_dados_ativo(ticker_clean)
    if not main_ticker_data:
        from data_collection.fundamentus_scraper import get_fundamentus_data
        with st.spinner(f"A buscar dados online para {ticker_clean}..."):
            main_ticker_data = get_fundamentus_data(ticker_clean)
            if main_ticker_data: salvar_dados_ativo(ticker_clean, main_ticker_data)
    if not main_ticker_data: st.error(f"Não foi possível obter os dados para o ativo principal {ticker}."); return
    
    watchlist = get_watchlist(); is_in_watchlist = ticker_clean in watchlist
    col1, col2 = st.columns([0.8, 0.2])
    with col1: st.title(f"Análise de {main_ticker_data.get('Nome', ticker_clean)}")
    with col2:
        if is_in_watchlist:
            if st.button("💔 Remover", use_container_width=True): remove_from_watchlist(ticker_clean); st.experimental_rerun()
        else:
            if st.button("⭐ Adicionar", use_container_width=True): add_to_watchlist(ticker_clean); st.experimental_rerun()
    st.markdown(f"**Setor:** {main_ticker_data.get('Setor', 'N/A')} | **Subsetor:** {main_ticker_data.get('Subsetor', 'N/A')}")
    st.markdown("---")
    
    score, _ = calculate_score(main_ticker_data)
    
    tabs = st.tabs(["Insights & Score", "Análise DuPont", "Múltiplos Históricos", "Histórico", "Setorial", "Quant. Avançada", "Risco", "Valuation"])
    with tabs[0]: generate_insights(main_ticker_data, score); run_quantitative_analysis(main_ticker_data, score)
    with tabs[1]: run_dupont_analysis(main_ticker_data)
    with tabs[2]: run_historical_multiples_analysis(ticker_clean) # Nova aba
    with tabs[3]: run_historical_analysis(ticker)
    with tabs[4]: 
        peer_tickers_data = {} # Lógica para carregar pares
        if st.session_state.peers_to_analyze:
            for peer_ticker in st.session_state.peers_to_analyze:
                peer_ticker_clean = peer_ticker.replace('.SA', '')
                peer_data = carregar_dados_ativo(peer_ticker_clean)
                if not peer_data:
                    from data_collection.fundamentus_scraper import get_fundamentus_data
                    peer_data = get_fundamentus_data(peer_ticker_clean)
                    if peer_data: salvar_dados_ativo(peer_ticker_clean, peer_data)
                if peer_data: peer_tickers_data[peer_ticker_clean] = peer_data
        run_sector_analysis(main_ticker_data, peer_tickers_data)
    with tabs[5]: run_advanced_quantitative_analysis(ticker)
    with tabs[6]:
        try:
            last_price = float(main_ticker_data.get('Cotação', '0').replace('.', '').replace(',', '.'))
            run_risk_analysis(ticker, last_price)
        except (ValueError, TypeError): st.warning("Não foi possível obter a cotação.")
    with tabs[7]: run_valuation_analysis(main_ticker_data)