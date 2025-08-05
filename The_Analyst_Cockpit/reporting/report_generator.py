import jinja2
import pandas as pd
from datetime import datetime

# Importa as funções de CÁLCULO de todos os módulos de análise
from analysis.scoring import calculate_score
from analysis.quantitative import get_quantitative_data
from analysis.historical_analysis import get_historical_data, calculate_cagr
from analysis.risk_analysis import calculate_risk_metrics
import plotly.graph_objects as go

def generate_html_report(ticker, ticker_data):
    """Gera um relatório HTML completo com todas as análises."""
    
    # 1. Executa todos os cálculos
    score, _ = calculate_score(ticker_data)
    quant_data = get_quantitative_data(ticker_data)
    quant_data['Cotação'] = ticker_data.get('Cotação', 'N/A')
    
    historical_df = get_historical_data(ticker)
    historical_plot_html = None
    if historical_df is not None and len(historical_df) > 1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=historical_df.index, y=historical_df['Receita (R$)'], name='Receita'))
        fig.add_trace(go.Bar(x=historical_df.index, y=historical_df['Lucro Líquido (R$)'], name='Lucro Líquido'))
        fig.update_layout(title_text="Evolução da Receita e Lucro Líquido", barmode='group')
        historical_plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Template HTML
    template_str = '''
    <!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><title>Relatório - {{ ticker_data.Nome }}</title>
    <style>
        body{font-family:Arial,sans-serif;margin:0;padding:0;background-color:#f4f4f9;color:#333}
        .container{max-width:1000px;margin:20px auto;padding:20px;background-color:#fff;box-shadow:0 0 10px rgba(0,0,0,0.1)}
        h1,h2{color:#1e3a8a;border-bottom:2px solid #1e3a8a;padding-bottom:10px}
        h1{text-align:center} .header{text-align:center;margin-bottom:20px} .section{margin-bottom:30px}
        table{width:100%;border-collapse:collapse;margin-bottom:20px} th,td{border:1px solid #ddd;padding:8px;text-align:left}
        th{background-color:#eef2f9} .score-box{background-color:#e6f0ff;border-left:5px solid #1e3a8a;padding:20px;text-align:center}
        .score-value{font-size:3em;font-weight:bold;color:#1e3a8a}
    </style></head><body><div class="container">
        <div class="header"><h1>Relatório de Análise de Ativo</h1>
            <p><strong>Ativo:</strong> {{ ticker_data.Papel }} ({{ ticker_data.Nome }})</p>
            <p><strong>Setor:</strong> {{ ticker_data.Setor }} | <strong>Subsetor:</strong> {{ ticker_data.Subsetor }}</p>
            <p><em>Gerado em: {{ generation_date }}</em></p></div>
        <div class="section score-box"><h2>Score Fundamentalista</h2><div class="score-value">{{ score }} / 100</div></div>
        <div class="section"><h2>Resumo Quantitativo</h2>{{ quant_table_html | safe }}</div>
        {% if historical_plot_html %}
        <div class="section"><h2>Análise Histórica</h2>{{ historical_plot_html | safe }}</div>
        {% endif %}
    </div></body></html>
    '''
    template = jinja2.Template(template_str)
    quant_df = pd.DataFrame(quant_data.items(), columns=['Indicador', 'Valor']).set_index('Indicador')
    quant_table_html = quant_df.to_html(classes='dataframe')
    
    html_output = template.render(
        ticker_data=ticker_data, score=score, quant_table_html=quant_table_html,
        historical_plot_html=historical_plot_html, generation_date=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )
    return html_output