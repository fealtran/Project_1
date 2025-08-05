import streamlit as st

def generate_insights(dados, score):
    """Gera insights automáticos em texto com base nos dados e no score."""
    st.subheader("Insights & Conclusão Automática")
    
    insights = []
    
    # Função interna para conversão segura
    def to_float(value):
        try:
            return float(str(value).replace('.','').replace(',','.').replace('%',''))
        except (ValueError, TypeError):
            return None

    # Análise do Score
    if score >= 75:
        insights.append(f"**Score Elevado ({score}/100):** O ativo apresenta um perfil fundamentalista muito forte, destacando-se positivamente na maioria das métricas.")
    elif score >= 50:
        insights.append(f"**Score Sólido ({score}/100):** O ativo possui fundamentos sólidos, com um bom equilíbrio entre crescimento, rentabilidade e valor.")
    else:
        insights.append(f"**Score de Atenção ({score}/100):** O ativo apresenta pontos de atenção em seus fundamentos que exigem uma análise mais aprofundada.")

    # Análise de Rentabilidade (ROE)
    roe = to_float(dados.get('ROE'))
    if roe is not None:
        if roe > 20:
            insights.append("**Excelente Rentabilidade:** O ROE acima de 20% indica que a empresa gera um lucro excecional em relação ao seu patrimônio líquido.")
        elif roe < 5 and roe > 0:
            insights.append("**Baixa Rentabilidade:** O ROE abaixo de 5% sugere que a empresa tem dificuldade em gerar retornos para os acionistas.")
        elif roe < 0:
            insights.append("**Prejuízo Operacional:** O ROE negativo é um sinal de alerta, indicando que a empresa opera com prejuízo.")

    # Análise de Valuation (P/L)
    pl = to_float(dados.get('P/L'))
    if pl is not None:
        if pl < 10 and pl > 0:
            insights.append("**Potencial de Subavaliação:** O P/L abaixo de 10 pode indicar que o ativo está barato em relação aos seus lucros.")
        elif pl > 25:
            insights.append("**Valuation Exigente:** O P/L acima de 25 sugere que o mercado tem altas expectativas de crescimento futuro, o que representa um risco maior.")

    # Análise de Endividamento (Dív.Líq/EBITDA)
    divida = to_float(dados.get('Dív Líq / EBITDA'))
    if divida is not None:
        if divida > 3.5:
            insights.append("**Endividamento Elevado:** A alavancagem (Dívida Líquida / EBITDA) está num nível que exige atenção, podendo representar um risco financeiro.")
        elif divida < 1 and divida >= 0:
            insights.append("**Baixo Endividamento:** A empresa possui uma estrutura de capital saudável com baixo endividamento.")
        elif divida < 0:
            insights.append("**Posição de Caixa Líquido:** A empresa tem mais caixa do que dívida, uma posição financeira muito confortável e rara.")

    # Exibe os insights
    for insight in insights:
        st.markdown(f"- {insight}")