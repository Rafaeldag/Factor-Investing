import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta  import relativedelta
import os
import streamlit as st

st.set_page_config(page_title = "Carteira Indicada - Factor", layout="wide")

carteira_hist = 'carteira1_peso1_ValorDeMercado_EBIT_EV_momento_6_meses_ebit_dl_volume_medio_prop_20_200.csv'
carteira_atual = 'Carteira_atual.csv'

caminho_atual = fr'C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\{carteira_atual}'
caminho_hist = fr'C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\{carteira_hist}'

if "carteira_atual" not in st.session_state:
        
        if os.path.exists(caminho_atual):
            colunas_selecionadas = [
            'data',
            'ticker',
            'EBIT_EV',
            'ValorDeMercado',
            'momento_6_meses',
            'ebit_dl',
            'volume_medio_prop_20_200',
            'EBIT_EV_RANK_carteira1',
            'ValorDeMercado_RANK_carteira1',
            'momento_6_meses_RANK_carteira1',
            'ebit_dl_RANK_carteira1',
            'volume_medio_prop_20_200_RANK_carteira1',
            'posicao_carteira1',
            'volume'
        ]
            dados_atual = pd.read_csv(caminho_atual, parse_dates=["data"])
            dados_atual= dados_atual[colunas_selecionadas]
            dados_atual.rename(columns={
                    'data': 'Data',
                    'ticker': 'Ação',
                    'EBIT_EV': 'EBIT/EV',
                    'ValorDeMercado': 'Valor de Mercado',
                    'momento_6_meses': 'Momentum 6M',
                    'ebit_dl': 'EBIT/Divida',
                    'volume_medio_prop_20_200': 'Volume 20/200',
                    'EBIT_EV_RANK_carteira1': 'EBIT/EV Rank',
                    'ValorDeMercado_RANK_carteira1': 'Valor de Mercado Rank',
                    'momento_6_meses_RANK_carteira1': 'Momentum 6M Rank',
                    'ebit_dl_RANK_carteira1': 'EBIT/Divida Rank',
                    'volume_medio_prop_20_200_RANK_carteira1': 'Volume 20/200 Rank',
                    'posicao_carteira1': 'Rank Final',
                    'volume': 'Volume',
                }, inplace=True)
            st.session_state.carteira_atual = dados_atual
        else:
            st.session_state.carteira_atual = pd.DataFrame(columns= ["Data", "Ação", "EBIT/EV", "Momentum 6M",
                                                                "EBIT/Divida","Volume 20/200",
                                                                "EBIT/EV Rank", "Momentum 6M Rank","EBIT/Divida Rank",
                                                                "Volume 20/200 Rank", "Posição Carteira", "Volume",])
st.sidebar.title("Adicionar Transação")



if st.session_state.carteira_atual.empty:
        st.info("Adicione transações para começar.")  

df = st.session_state.carteira_atual.copy()
df["Data"] = pd.to_datetime(df["Data"]).dt.normalize()
df.sort_values("Rank Final", inplace=True)
df = df.dropna(how='any')


TICKERS = df['Ação'].unique().tolist()

with st.sidebar.expander("Filtros de Ativos", expanded=False):
        
        tickers_filtro = st.multiselect("Tickers",
                                    options=sorted(df["Ação"].dropna().unique()),
                                    default=sorted(df["Ação"].dropna().unique()))
        

with st.sidebar.expander("Filtros de Liquidez", expanded=False):
        min_liquidez = st.number_input(
                            "Mínimo de Volume",
                            min_value=0,
                        )
        
with st.sidebar.expander("Filtros de Indicadores", expanded=False):
    
        min_ebit_ev = st.number_input(
                            "Mínimo de EBIT/EV",
                            min_value=0,
                        )
    
        min_momentum6m = st.number_input(
                            "Mínimo de Momentum 6M",
                            min_value=-99999999,
                        )

df_filtrado = df.loc[
      (df["Ação"].isin(tickers_filtro)) 
    & (df["Volume"] >= min_liquidez)
    & (df["EBIT/EV"] >= min_ebit_ev)
    & (df["Momentum 6M"] >= min_momentum6m)
    ]
        

st.dataframe(
        df_filtrado.style.format({"Data": "{:%Y-%m-%d}"}),
        use_container_width=True,
        hide_index=True
)