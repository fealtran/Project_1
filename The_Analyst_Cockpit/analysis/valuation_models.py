import streamlit as st
def to_float_safe(value_str): # Função de conversão robusta
    if value_str is None: return None
    try: return float(str(value_str).replace('.', '').replace(',', '.').replace('%',''))
    except (ValueError, TypeError): return None

def run_valuation_analysis(dados):
    st.header("Modelos de Valuation")
    with st.expander("Modelo de Gordon (Crescimento de Dividendos)"):
        try:
            dy = to_float_safe(dados.get('Div.Yield')) / 100 if dados.get('Div.Yield') else 0.0
            cotacao = to_float_safe(dados.get('Cotação'))
            
            if cotacao is None or cotacao == 0:
                st.warning("Cotação indisponível. Não é possível calcular o modelo."); return

            d0 = cotacao * dy
            g = st.slider("Crescimento dos Dividendos (g)", 0.0, 0.20, 0.05, format="%.2f%%", key="g_gordon_final")
            k = st.slider("Retorno Exigido (k)", 0.0, 0.30, 0.15, format="%.2f%%", key="k_gordon_final")

            if k > g:
                valor = (d0 * (1 + g)) / (k - g)
                st.metric("Valor Intrínseco Estimado (Gordon)", f"R$ {valor:,.2f}", f"{((valor/cotacao)-1):.2%}")
            else: st.error("k deve ser maior que g.")
        except Exception: st.warning("Não foi possível calcular. Dados de dividendos/cotação em falta.")