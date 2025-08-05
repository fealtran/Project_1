import streamlit as st
import pandas as pd
import plotly.express as px
def run_sector_analysis(main_ticker_data, peer_tickers_data):
    # ... (código anterior continua o mesmo até a criação do df) ...
    st.subheader("Análise Comparativa Setorial")
    all_data = [main_ticker_data] + list(peer_tickers_data.values())
    comparison_list = []
    for data in all_data:
        if not data: continue
        comparison_list.append({'Ticker': data.get('Papel', 'N/A'), 'P/L': data.get('P/L'), 'P/VP': data.get('P/VP'), 'ROE': data.get('ROE'), 'Div.Yield': data.get('Div.Yield')})
    if len(comparison_list) < 1: st.info("Selecione pelo menos um par na barra lateral para a análise setorial."); return None
    df = pd.DataFrame(comparison_list)
    def to_numeric_safe(series): return pd.to_numeric(series.astype(str).str.replace('.','').str.replace(',','.').str.replace('%',''), errors='coerce')
    for col in ['P/L', 'P/VP', 'ROE', 'Div.Yield']:
        df[col] = to_numeric_safe(df[col])
        if 'ROE' in col or 'Yield' in col: df[col] /= 100
    st.dataframe(df.set_index('Ticker').style.format({'P/L': '{:.2f}', 'P/VP': '{:.2f}', 'ROE': '{:.2%}', 'Div.Yield': '{:.2%}'}).background_gradient(cmap='RdYlGn_r', subset=['P/L', 'P/VP']).background_gradient(cmap='RdYlGn', subset=['ROE', 'Div.Yield']), use_container_width=True)
    
    if len(df) > 1:
        st.markdown("---")
        st.subheader("Posicionamento de Mercado (P/L vs. ROE)")
        df_chart = df.dropna(subset=['P/L', 'ROE'])
        if not df_chart.empty:
            fig = px.scatter(df_chart, x='P/L', y='ROE', text='Ticker', title='P/L vs. ROE do Setor')
            fig.update_traces(textposition='top center')
            fig.add_hline(y=df_chart['ROE'].mean(), line_dash="dot", annotation_text="Média ROE Setor")
            fig.add_vline(x=df_chart['P/L'].mean(), line_dash="dot", annotation_text="Média P/L Setor")
            st.plotly_chart(fig, use_container_width=True)
            return fig # RETORNA O GRÁFICO PARA O RELATÓRIO
    return None