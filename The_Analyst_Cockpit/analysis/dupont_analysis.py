import streamlit as st
def to_float_safe(value_str):
    if value_str is None: return None
    try: return float(str(value_str).replace('.', '').replace(',', '.'))
    except (ValueError, TypeError): return None

def run_dupont_analysis(dados):
    st.header("Análise DuPont (Decomposição do ROE)")
    try:
        lucro_liquido = to_float_safe(dados.get('Lucro Líquido'))
        receita_liquida = to_float_safe(dados.get('Receita Líquida'))
        ativo_total = to_float_safe(dados.get('Ativo'))
        patrimonio_liquido = to_float_safe(dados.get('Patrim. Líq'))
        roe_original_str = dados.get('ROE')
        
        componentes = [lucro_liquido, receita_liquida, ativo_total, patrimonio_liquido]
        if not all(c is not None and c != 0 for c in componentes):
            st.warning("Não foi possível realizar a Análise DuPont. Faltam dados essenciais."); return

        if roe_original_str: st.info(f"O ROE de **{roe_original_str}** da empresa é explicado por:")
        
        margem_liquida = lucro_liquido / receita_liquida
        giro_ativo = receita_liquida / ativo_total
        alavancagem_financeira = ativo_total / patrimonio_liquido
        roe_calculado = margem_liquida * giro_ativo * alavancagem_financeira

        col1, col2, col3 = st.columns(3)
        col1.metric("Margem Líquida", f"{margem_liquida:.2%}")
        col2.metric("Giro do Ativo", f"{giro_ativo:.2f}x")
        col3.metric("Alavancagem Financeira", f"{alavancagem_financeira:.2f}x")
        st.markdown("---")
        st.subheader("Insights da Análise DuPont")
        st.markdown(f"- **Lucratividade:** A cada R$ 100 de receita, a empresa gera **R$ {margem_liquida*100:.2f}** de lucro líquido.")
        st.markdown(f"- **Eficiência:** A empresa gera **R$ {giro_ativo:.2f}** de receita para cada R$ 1,00 em ativos.")
        st.markdown(f"- **Alavancagem:** Para cada R$ 1,00 de capital próprio, a empresa possui **R$ {alavancagem_financeira:.2f}** de ativos.")
        st.latex(f"ROE \approx {margem_liquida:.2%} \times {giro_ativo:.2f} \times {alavancagem_financeira:.2f} \approx {roe_calculado:.2%}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao calcular a Análise DuPont: {e}")