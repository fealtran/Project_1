
import streamlit as st; import pandas as pd; import sqlite3; import os; from datetime import datetime; from data_collection import fundamentus_scraper
st.set_page_config(layout="wide"); st.title("Atualização e Validação da Base de Dados")

# --- CORREÇÃO AQUI: Define o caminho absoluto para o banco de dados ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'dados.db')

st.subheader("Etapa 1: Teste Rápido do Coletor")
if st.button("Executar Teste Rápido"):
    with st.spinner("Testando..."):
        td = [d for t in ['PETR4', 'VALE3', 'ITUB4', 'WEGE3', 'MGLU3'] if (d := fundamentus_scraper.get_fundamentus_data(t))]
        st.session_state.test_results = pd.DataFrame(td) if td else pd.DataFrame()

if 'test_results' in st.session_state:
    if not st.session_state.test_results.empty:
        st.success("Teste concluído com sucesso!"); st.dataframe(st.session_state.test_results[['Papel','Cotacao','PL','PVP']].set_index('Papel'))
        st.session_state.test_successful = True
    else: st.error("O teste falhou."); st.session_state.test_successful = False

st.divider(); st.subheader("Etapa 2: Atualização Completa da Base")
if st.session_state.get('test_successful', False):
    ti = st.text_area("Insira os tickers para a atualização completa:", "PETR4,VALE3,ITUB4,BBDC4,ITSA4,ABEV3,MGLU3,WEGE3,B3SA3,SUZB3")
    if st.button("Iniciar Atualização Completa"):
        ts = [t.strip().upper() for t in ti.split(',') if t.strip()]
        if ts:
            with st.spinner("Atualizando..."):
                os.makedirs(DATA_DIR, exist_ok=True); c = sqlite3.connect(DB_PATH)
                ad = [d for i,t in enumerate(ts) if (d := fundamentus_scraper.get_fundamentus_data(t))]
                if ad: pd.DataFrame(ad).set_index('Papel').to_sql('fundamentals', c, if_exists='replace', index=True); st.success(f"Banco de dados atualizado com {len(ad)} ativos!")
                else: st.error("Nenhum dado foi coletado.")
                c.close()
else: st.warning("Execute o Teste Rápido com sucesso para habilitar a atualização completa.")
