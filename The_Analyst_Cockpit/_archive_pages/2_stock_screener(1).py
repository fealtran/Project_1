
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from data_collection import fundamentus_scraper

st.set_page_config(layout="wide")
st.title("Atualização e Validação da Base de Dados")
st.caption(f"Última verificação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Caminho para o banco de dados
DB_DIR = 'data'
DB_PATH = os.path.join(DB_DIR, 'dados.db')

# --- ETAPA 1: TESTE RÁPIDO DO COLETOR DE DADOS ---
st.subheader("Etapa 1: Teste Rápido do Coletor")
st.markdown("Antes de atualizar a base completa, realize um teste rápido com 5 ativos para garantir que o coletor de dados (scraper) está funcionando corretamente.")

test_tickers = ['PETR4', 'VALE3', 'ITUB4', 'WEGE3', 'MGLU3']

if 'test_results' not in st.session_state:
    st.session_state.test_results = None

if st.button("Executar Teste Rápido"):
    with st.spinner("Testando o coletor com 5 ativos..."):
        test_data = []
        for ticker in test_tickers:
            data = fundamentus_scraper.get_fundamentus_data(ticker)
            if data:
                test_data.append(data)

        if test_data:
            st.session_state.test_results = pd.DataFrame(test_data)
        else:
            st.session_state.test_results = pd.DataFrame() # DataFrame vazio para indicar falha

# Exibe os resultados do teste se existirem
if st.session_state.test_results is not None:
    if not st.session_state.test_results.empty:
        st.success("Teste concluído com sucesso! O coletor está funcional.")
        st.markdown("Amostra de dados coletados:")
        st.dataframe(st.session_state.test_results[['Papel', 'Cotacao', 'PL', 'PVP', 'Div_Yield', 'ROE']].set_index('Papel'))

        # Libera a Etapa 2
        st.session_state.test_successful = True
    else:
        st.error("O teste falhou. O coletor não conseguiu extrair dados. Verifique a conexão ou se o site Fundamentus está online antes de prosseguir.")
        st.session_state.test_successful = False

st.divider()

# --- ETAPA 2: ATUALIZAÇÃO COMPLETA DA BASE DE DADOS ---
st.subheader("Etapa 2: Atualização Completa da Base")

# A atualização completa só é habilitada se o teste rápido foi bem-sucedido
if st.session_state.get('test_successful', False):
    st.info("O teste foi bem-sucedido. Agora você pode prosseguir com a atualização da base de dados completa.")

    tickers_input = st.text_area("Insira os tickers para a atualização completa, separados por vírgula:", height=150, value="PETR4,VALE3,ITUB4,BBDC4,ITSA4,ABEV3,MGLU3,WEGE3,B3SA3,SUZB3,GGBR4,JBSS3,RENT3,LREN3,EQTL3,RADL3,PRIO3,HAPV3,VBBR3,RAIL3")

    if st.button("Iniciar Atualização Completa da Base"):
        tickers = [ticker.strip().upper() for ticker in tickers_input.split(',') if ticker.strip()]
        if tickers:
            with st.spinner("Atualizando a base de dados... Isso pode levar vários minutos."):
                os.makedirs(DB_DIR, exist_ok=True)
                conn = sqlite3.connect(DB_PATH)

                all_data = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, ticker in enumerate(tickers):
                    status_text.text(f"Buscando dados para {ticker}... ({i+1}/{len(tickers)})")
                    data = fundamentus_scraper.get_fundamentus_data(ticker)
                    if data:
                        all_data.append(data)
                    progress_bar.progress((i + 1) / len(tickers))

                if all_data:
                    df = pd.DataFrame(all_data).set_index('Papel')
                    df.to_sql('fundamentals', conn, if_exists='replace', index=True)
                    st.success(f"Banco de dados atualizado com sucesso com {len(all_data)} ativos!")
                else:
                    st.error("Nenhum dado foi coletado na atualização completa.")

                conn.close()
        else:
            st.warning("Por favor, insira ao menos um ticker.")
else:
    st.warning("Execute o Teste Rápido com sucesso para habilitar a atualização completa.")
