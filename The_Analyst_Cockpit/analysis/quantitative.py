import streamlit as st

def safe_format(value, is_percent=False):
    if value is None: return 'N/A'
    try:
        val_str = str(value).strip().replace('.','').replace(',','.').replace('%','')
        num = float(val_str)
        if '%' in str(value) or is_percent: return f'{num:,.2f}%'
        return f'{num:,.2f}'
    except: return 'N/A'

def get_quantitative_data(dados):
    """Função de CÁLCULO: Retorna um dicionário com os dados quantitativos formatados."""
    indicadores = {
        'P/L': dados.get('P/L'), 'P/VP': dados.get('P/VP'),
        'ROE': dados.get('ROE'), 'Div.Yield': dados.get('Div.Yield'),
        'Dív Líq / EBITDA': dados.get('Dív Líq / EBITDA'), 'Cres. Rec (5a)': dados.get('Cres. Rec (5a)'),
        'Marg. EBIT': dados.get('Marg. EBIT'), 'Marg. Líquida': dados.get('Marg. Líquida')
    }
    
    formatted_data = {}
    for key, value in indicadores.items():
        is_percent = any(s in key for s in ['Yield', 'ROE', 'ROIC', 'Cres.', 'Marg.'])
        formatted_data[key] = safe_format(value, is_percent=is_percent)
        
    return formatted_data

def run_quantitative_analysis(dados, score):
    """Função de EXIBIÇÃO: Mostra a análise no Streamlit."""
    st.header("Análise Quantitativa")

    st.subheader("Score Fundamentalista")
    st.progress(score / 100)
    st.metric(label="Pontuação Geral", value=f"{score} / 100")
    st.caption("Score baseado em P/L, P/VP, ROE, Dividend Yield, Dívida e Margem Líquida.")
    st.markdown("---")

    # Pega os dados já formatados da função de cálculo
    indicadores_formatados = get_quantitative_data(dados)
    
    cols = st.columns(4)
    i = 0
    for key, value in indicadores_formatados.items():
        cols[i % 4].metric(label=key, value=value)
        i += 1