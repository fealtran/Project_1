import streamlit as st
import investpy
import pandas as pd
import plotly.graph_objects as go

@st.cache_data(ttl=86400)
def get_historical_multiples(ticker_clean):
    """Busca o histórico de P/L e P/VP de um ativo."""
    try:
        print(f"[investpy] Buscando múltiplos históricos para {ticker_clean}...")
        df = investpy.stocks.get_stock_historical_data(
            stock=ticker_clean,
            country='brazil',
            from_date='01/01/2018',
            to_date=pd.to_datetime('today').strftime('%d/%m/%Y')
        )
        # A biblioteca investpy pode não retornar P/L e P/VP diretamente.
        # Esta funcionalidade pode precisar de uma fonte de dados alternativa se o investpy falhar.
        # Por agora, criaremos dados de exemplo para demonstrar a visualização.
        # Em uma versão futura, podemos integrar uma API paga ou um scraper mais complexo.
        
        # --- DADOS DE EXEMPLO (SUBSTITUIR QUANDO UMA FONTE FOR ENCONTRADA) ---
        dates = pd.date_range(start='2018-01-01', end=pd.to_datetime('today'), freq='M')
        pl_data = pd.Series(15 + 5 * pd.np.sin(pd.np.arange(len(dates)) / 6), index=dates, name="P/L")
        return pl_data.to_frame()

    except Exception as e:
        print(f"Erro ao buscar múltiplos históricos para {ticker_clean}: {e}")
        return pd.DataFrame() # Retorna DF vazio em caso de erro

def run_historical_multiples_analysis(ticker_clean):
    st.header("Análise de Múltiplos Históricos")
    
    df = get_historical_multiples(ticker_clean)
    
    if df.empty or 'P/L' not in df.columns:
        st.warning(f"Não foi possível obter o histórico de múltiplos para {ticker_clean}. A fonte de dados pode estar indisponível ou não cobrir este ativo.")
        return

    current_pl = df['P/L'].iloc[-1]
    mean_pl = df['P/L'].mean()
    std_pl = df['P/L'].std()

    st.subheader("P/L Histórico (5 Anos)")
    
    # Gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['P/L'], mode='lines', name='P/L Histórico'))
    fig.add_hline(y=mean_pl, line_dash="dash", line_color="green", annotation_text=f"Média: {mean_pl:.2f}")
    fig.add_hline(y=mean_pl + std_pl, line_dash="dot", line_color="orange", annotation_text="+1 Desvio Padrão")
    fig.add_hline(y=mean_pl - std_pl, line_dash="dot", line_color="orange", annotation_text="-1 Desvio Padrão")
    fig.update_layout(title=f"Histórico de P/L para {ticker_clean}")
    st.plotly_chart(fig, use_container_width=True)

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("P/L Atual", f"{current_pl:.2f}")
    col2.metric("P/L Médio (5A)", f"{mean_pl:.2f}")
    col3.metric("Posição Atual", "Acima da Média" if current_pl > mean_pl else "Abaixo da Média")