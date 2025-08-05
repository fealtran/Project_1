import pandas as pd
from core.database_manager import load_all_data_as_dataframe

def filter_stocks(filters):
    """
    Carrega todos os dados da base de dados e aplica os filtros do screener.
    """
    df = load_all_data_as_dataframe()
    
    if df.empty:
        return pd.DataFrame()

    # Aplica os filtros
    # Filtro P/L
    df = df[(df['P/L'] >= filters['P/L'][0]) & (df['P/L'] <= filters['P/L'][1])]
    
    # Filtro P/VP
    df = df[(df['P/VP'] >= filters['P/VP'][0]) & (df['P/VP'] <= filters['P/VP'][1])]
    
    # Filtro ROE
    df = df[df['ROE'] >= (filters['ROE'] / 100)]
    
    # Filtro Dividend Yield
    df = df[df['Div.Yield'] >= (filters['Div.Yield'] / 100)]
    
    # Filtro Dívida
    df = df[df['Dív Líq / EBITDA'] <= filters['Dív.Líq/EBITDA']]

    # Filtro Margem Líquida
    df = df[df['Marg. Líquida'] >= (filters['Marg. Líquida'] / 100)]
    
    return df