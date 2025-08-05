import streamlit as st
from bcb import sgs
import pandas as pd
from datetime import datetime

@st.cache_data(ttl=86400) # Cache de 1 dia para dados macro
def get_macro_data():
    """
    Busca dados da Taxa Selic e do IPCA (Inflação) do Banco Central do Brasil.
    """
    print("[Macro Data] A buscar dados da Selic e IPCA do BCB...")
    try:
        # Códigos das séries no SGS (Sistema Gerenciador de Séries Temporais) do BCB
        # 432: Selic (taxa anualizada) | 433: IPCA (variação mensal)
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(years=5)
        
        df = sgs.get({'Selic': 432, 'IPCA': 433}, start=start_date.strftime('%Y-%m-%d'))
        
        # Calcula o IPCA acumulado em 12 meses
        df['IPCA_12M'] = (1 + df['IPCA']/100).rolling(window=12).apply(lambda x: x.prod(), raw=True) - 1
        df['IPCA_12M'] *= 100 # Converte para percentagem
        
        return df.dropna()
    except Exception as e:
        print(f"[Macro Data] Erro ao buscar dados do BCB: {e}")
        return None