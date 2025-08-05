
import streamlit as st; import pandas as pd; from datetime import datetime, timedelta; import investpy
SGS_CODES = {'SELIC': 11, 'IPCA': 433, 'DOLAR': 1}
@st.cache_data(ttl=3600)
def get_sgs_data(c, d=730): # Busca 2 anos para os minigráficos
    e=datetime.now(); s=e-timedelta(days=d)
    u=f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{c}/dados?formato=json&dataInicial={s.strftime("%d/%m/%Y")}&dataFinal={e.strftime("%d/%m/%Y")}'
    try: df=pd.read_json(u); df['data']=pd.to_datetime(df['data'],dayfirst=True); df.set_index('data',inplace=True); df['valor']=df['valor'].astype(float); return df
    except: return pd.DataFrame()
@st.cache_data(ttl=3600)
def get_economic_calendar(from_date, to_date, countries, importances):
    try:
        df=investpy.economic_calendar(from_date=from_date, to_date=to_date, countries=countries, importances=importances)
        df['time'] = pd.to_datetime(df['time'], format='%H:%M').dt.time
        return df[['time', 'event', 'country', 'importance']].sort_values('time').reset_index(drop=True)
    except Exception as e: return pd.DataFrame()
