
import streamlit as st; import plotly.graph_objects as go; import os; import pandas as pd
from data_fetcher import get_market_data
st.set_page_config(layout="wide", page_title="The Analyst's Cockpit v2.3")

def load_css():
    with open(os.path.join(os.path.dirname(__file__), "assets", "style.css")) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

# --- Módulos de Análise (v2.3) ---
def render_risk_radar(data):
    vix_val = data.get('VIX', {}).get('value', 20) if data.get('VIX') else 20
    st.markdown('<div class="risk-radar-box">', unsafe_allow_html=True)
    st.markdown("<h5>Radar de Riscos Estratégicos</h5>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    p1.markdown("<div class='risk-pillar'><h6>🏛️ Político & Geopolítico</h6>As atenções se voltam para a <span class='keyword'>reforma tributária</span> no Congresso. Globalmente, as <span class='keyword'>tensões comerciais</span> podem impactar a demanda por commodities.</div>", unsafe_allow_html=True)
    p2.markdown("<div class='risk-pillar'><h6>📉 Macroeconômico</h6>A persistência do <span class='keyword'>dólar</span> acima de R$5,00 adiciona <span class='keyword'>pressão inflacionária</span>, diminuindo o espaço para cortes na <span class='keyword'>taxa Selic</span> e limitando o potencial da bolsa.</div>", unsafe_allow_html=True)
    p3.markdown(f"<div class='risk-pillar'><h6>📊 Mercado & Fluxo</h6>O <span class='keyword'>VIX</span> negociado em <span class='keyword'>{vix_val:.1f}</span> indica um ambiente de **'risk-off' global**. O <span class='keyword'>fluxo de capital</span> para emergentes segue contido.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_diagnostics_modules(market_data):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="widget-box">', unsafe_allow_html=True)
        st.markdown("<h6>Fluxo de Capital Estrangeiro (B3)</h6>", unsafe_allow_html=True)
        yoy_flow_data = {'Ano': [2021, 2022, 2023, 2024, '2025 (YTD)'], 'Saldo (R$ Bi)': [-55, 105, -15, 80, 58]}
        df_yoy = pd.DataFrame(yoy_flow_data)
        colors = ['#F87171' if x < 0 else '#34D399' for x in df_yoy['Saldo (R$ Bi)']]
        fig = go.Figure(go.Bar(x=df_yoy['Ano'], y=df_yoy['Saldo (R$ Bi)'], marker_color=colors))
        fig.update_layout(title_text='Saldo Líquido Anual', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E0E0', size=12), height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="widget-box">', unsafe_allow_html=True)
        st.markdown("<h6>Regime de Volatilidade (IBOV)</h6>", unsafe_allow_html=True)
        vol_series = market_data.get('IBOV', {}).get('history') if market_data.get('IBOV') else None
        if vol_series is not None and len(vol_series) > 20:
            ma20 = vol_series.rolling(window=20).mean()
            std20 = vol_series.rolling(window=20).std()
            bollinger_bw = ((std20 * 4) / ma20)
            if bollinger_bw.iloc[-1] < 0.05: regime = "Contração de Volatilidade"
            elif bollinger_bw.iloc[-1] > 0.15: regime = "Expansão de Volatilidade"
            elif ma20.diff().iloc[-1] > 0: regime = "Tendência de Alta"
            else: regime = "Tendência de Baixa"
            st.metric(label="Status Atual", value=regime)
            
            fig = go.Figure(go.Scatter(x=bollinger_bw.index, y=bollinger_bw, line_color='#38BDF8', name='Largura da Banda'))
            fig.update_layout(title_text='Histórico da Largura das Bandas de Bollinger', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E0E0', size=10), height=200, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.info("O regime é definido pela Largura das Bandas de Bollinger (compressão/expansão) e pela inclinação da Média Móvel.", icon="ℹ️")
        else: st.metric(label="Status Atual", value="Indisponível")
        st.markdown('</div>', unsafe_allow_html=True)

def render_correlation_module(market_data):
    with st.expander("Análise de Correlação entre Ativos"):
        keys_for_matrix = ['IBOV', 'Dolar', 'S&P 500', 'US 10Y']
        df_corr = pd.DataFrame({k: market_data[k]['history'] for k in keys_for_matrix if market_data.get(k)})
        if not df_corr.empty:
            corr_matrix = df_corr.corr()
            heatmap = go.Figure(go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns, colorscale='RdBu', zmin=-1, zmax=1, text=corr_matrix.round(2).values, texttemplate="%{text}", textfont={"size":12}))
            heatmap.update_layout(title="Matriz de Correlação (60 dias)", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E0E0', size=12))
            st.plotly_chart(heatmap, use_container_width=True)

def render_metric_expander(title, icon, data_dict):
    if not data_dict:
        st.markdown(f"<div style='background-color:#171e2e; padding: 20px; border-radius:12px; text-align:center; border: 1px solid #2a3447;'><strong>{icon} {title}</strong><br><small>Dados Indisponíveis</small></div>", unsafe_allow_html=True)
        return

    with st.expander(f"{icon} **{title}**"):
        value, change_percent, history = data_dict['value'], data_dict['change_percent'], data_dict['history']
        st.markdown(f'<p style="font-size: 2.2rem; font-weight: 700; text-align:center; margin:0;">{value:,.2f}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="{"positive" if change_percent >= 0 else "negative"}" style="text-align:center; font-size:1.1rem; font-weight:700;">({change_percent:+.2f}%)</p>', unsafe_allow_html=True)
        
        fig = go.Figure(go.Scatter(x=history.index, y=history, line_color='#38BDF8' if history.iloc[-1] >= history.iloc[0] else '#F87171'))
        fig.update_layout(template='plotly_dark', height=150, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0')
        st.plotly_chart(fig, use_container_width=True)

# --- LAYOUT DA APLICAÇÃO (v2.3) ---
st.markdown("<h1><img src='https://emojicdn.elk.sh/📡' style='height:40px;'> The Analyst's Cockpit v2.3</h1>", unsafe_allow_html=True)
market_data = get_market_data()

render_risk_radar(market_data)
st.markdown("<h3 class='section-header'>Diagnósticos de Mercado</h3>", unsafe_allow_html=True)
render_diagnostics_modules(market_data)
render_correlation_module(market_data)

st.markdown("<h3 class='section-header'>Painel Macroeconômico (Brasil)</h3>", unsafe_allow_html=True)
cols_br = st.columns(3)
br_names = ["IBOV", "SMLL", "Dolar"]; br_icons = ["🇧🇷", "📈", "💵"]
for i, n in enumerate(br_names):
    with cols_br[i]: render_metric_expander(n, br_icons[i], market_data.get(n))

st.markdown("<h3 class='section-header'>Cenário Global</h3>", unsafe_allow_html=True)
cols_g1 = st.columns(4)
g1 = ["S&P 500", "NASDAQ", "Petroleo", "Metais (XME)"]; g1_icons = ["🇺🇸", "💻", "🛢️", "⛏️"]
for i, n in enumerate(g1):
    with cols_g1[i]: render_metric_expander(n, g1_icons[i], market_data.get(n))
cols_g2 = st.columns(4)
g2 = ["VIX", "US 10Y", "EEM", "EFA"]; g2_icons = ["⚡", "🇺🇸", "🌏", "🌍"]
for i, n in enumerate(g2):
    with cols_g2[i]: render_metric_expander(n, g2_icons[i], market_data.get(n))

