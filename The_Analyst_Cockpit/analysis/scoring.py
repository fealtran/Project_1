import streamlit as st
import pandas as pd

def calculate_score(dados):
    """
    Calcula um score fundamentalista de 0 a 100 com base em vários indicadores.
    """
    if not dados: return 0, {}

    # Função interna para conversão segura para float
    def to_float(value):
        try:
            return float(str(value).replace('.','').replace(',','.').replace('%',''))
        except (ValueError, TypeError):
            return None

    # Pesos para cada indicador (soma deve ser 1.0)
    weights = {
        'P/L': 0.20, 'P/VP': 0.15, 'ROE': 0.20, 'Div.Yield': 0.15,
        'Dív.Líq/EBITDA': 0.15, 'Marg. Líquida': 0.15
    }

    # Extração e conversão segura dos dados
    metrics = {
        'P/L': to_float(dados.get('P/L')),
        'P/VP': to_float(dados.get('P/VP')),
        'ROE': to_float(dados.get('ROE')),
        'Div.Yield': to_float(dados.get('Div.Yield')),
        'Dív.Líq/EBITDA': to_float(dados.get('Dív Líq / EBITDA')), # Usa a chave corrigida
        'Marg. Líquida': to_float(dados.get('Marg. Líquida'))
    }

    scores = {}
    # Regras de pontuação (de 0 a 1) para cada métrica
    # P/L: Menor é melhor. Ideal < 15.
    if metrics['P/L'] is not None and metrics['P/L'] > 0:
        scores['P/L'] = max(0, min(1, (15 - metrics['P/L']) / 15))
    else: scores['P/L'] = 0.0

    # P/VP: Menor é melhor. Ideal < 2.
    if metrics['P/VP'] is not None and metrics['P/VP'] > 0:
        scores['P/VP'] = max(0, min(1, (2 - metrics['P/VP']) / 2))
    else: scores['P/VP'] = 0.0

    # ROE: Maior é melhor. Ideal > 15%.
    if metrics['ROE'] is not None:
        scores['ROE'] = max(0, min(1, metrics['ROE'] / 20.0)) # Normaliza por 20%
    else: scores['ROE'] = 0.0

    # Div.Yield: Maior é melhor. Ideal > 5%.
    if metrics['Div.Yield'] is not None:
        scores['Div.Yield'] = max(0, min(1, metrics['Div.Yield'] / 8.0)) # Normaliza por 8%
    else: scores['Div.Yield'] = 0.0
        
    # Dív.Líq/EBITDA: Menor é melhor. Ideal < 3.
    if metrics['Dív.Líq/EBITDA'] is not None:
        scores['Dív.Líq/EBITDA'] = max(0, min(1, (3 - metrics['Dív.Líq/EBITDA']) / 3))
    else: scores['Dív.Líq/EBITDA'] = 0.5 # Valor neutro se não houver dados

    # Marg. Líquida: Maior é melhor. Ideal > 10%.
    if metrics['Marg. Líquida'] is not None:
        scores['Marg. Líquida'] = max(0, min(1, metrics['Marg. Líquida'] / 15.0)) # Normaliza por 15%
    else: scores['Marg. Líquida'] = 0.0

    # Cálculo do Score Final Ponderado
    final_score = 0
    for metric, score in scores.items():
        final_score += score * weights[metric]

    # Converte para uma escala de 0 a 100
    return int(final_score * 100), {k: round(v, 2) for k, v in scores.items()}