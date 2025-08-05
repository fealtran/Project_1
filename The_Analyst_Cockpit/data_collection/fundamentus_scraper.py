
import requests; from bs4 import BeautifulSoup; import pandas as pd
def clean_value(v):
    if not isinstance(v,str) or v=='-': return None
    c=v.replace('R$','').replace('.','').replace('%','').strip().replace(',','.');
    try: return float(c)
    except(ValueError,TypeError): return v
def get_fundamentus_data(t):
    u=f'https://www.fundamentus.com.br/detalhes.php?papel={t}'; h={'User-Agent':'Mozilla/5.0'}
    try: r=requests.get(u,headers=h,timeout=10);
    except requests.exceptions.RequestException: return None
    if r.status_code!=200: return None
    s=BeautifulSoup(r.text,'lxml');
    if "Nenhum papel encontrado" in s.get_text(): return None
    sd={'Papel':t}
    for tdl in s.find_all('td',class_='label'):
        l=tdl.get_text(strip=True).replace('?',''); vtd=tdl.find_next_sibling('td',class_='data')
        if l and vtd: sd[l]=vtd.get_text(strip=True)
    rm={'Cotação':'Cotacao','Data últ cot':'Data_Ult_Cot','Empresa':'Empresa','Setor':'Setor','Subsetor':'Subsetor','P/L':'PL','P/VP':'PVP','PSR':'PSR','Div.Yield':'Div_Yield','P/Ativo':'P_Ativo','P/Cap.Giro':'P_Cap_Giro','P/EBIT':'P_EBIT','P/Ativ Circ.Liq':'P_Ativ_Circ_Liq','EV/EBIT':'EV_EBIT','EV/EBITDA':'EV_EBITDA','Mrg Ebit':'Mrg_Ebit','Mrg. Líq.':'Mrg_Liq','Liq. Corr.':'Liq_Corr','ROIC':'ROIC','ROE':'ROE','Liq.2meses':'Liq_2_Meses','Patrim. Líq':'Patrim_Liq','Dív. Brut/ Patrim.':'Div_Br_Patrim','Cresc. Rec.5a':'Cresc_Rec_5a'}
    fd={'Papel':t}
    for ok,nk in rm.items(): fd[nk]=clean_value(sd.get(ok))
    return fd
