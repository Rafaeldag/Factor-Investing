import os
import pandas as pd
import streamlit as st
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine

# Configurações iniciais do Streamlit
st.set_page_config(page_title="Carteira Indicada - Factor", layout="wide")

# Variáveis de ambiente para conexão ao Cloud SQL
INSTANCE_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")  # ex: "projeto:regiao:instancia"
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER", "pg8000")        # ou "pymysql" para MySQL

# Cria conector
connector = Connector()

def getconn():
    return connector.connect(
        INSTANCE_CONNECTION_NAME,
        DB_DRIVER,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )

# Cria engine SQLAlchemy
engine = create_engine(
    f"postgresql+{DB_DRIVER}://",
    creator=getconn,
)

# Função para carregar dados do Cloud SQL (cache por 24h)
@st.cache_data(ttl=24 * 3600)
def carregar_dados():
    sql = "SELECT data, ticker, EBIT_EV, ValorDeMercado, momento_6_meses, ebit_dl, volume_medio_prop_20_200, \
            EBIT_EV_RANK_carteira1, ValorDeMercado_RANK_carteira1, momento_6_meses_RANK_carteira1, \
            ebit_dl_RANK_carteira1, volume_medio_prop_20_200_RANK_carteira1, posicao_carteira1 AS RankFinal, volume \
            FROM sua_tabela_de_carteira;"
    df = pd.read_sql(sql, con=engine, parse_dates=["data"])
    return df

# Carrega dados
dados = carregar_dados()

# Renomeia colunas para exibição
col_map = {
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
    'RankFinal': 'Rank Final',
    'volume': 'Volume'
}

dados.rename(columns=col_map, inplace=True)

df = dados.copy()
# Normaliza a data e ordena
df['Data'] = pd.to_datetime(df['Data']).dt.normalize()
df.sort_values('Rank Final', inplace=True)
df.dropna(how='any', inplace=True)

# Sidebar: filtros
st.sidebar.title("Filtros")

# Ativos
tickers = sorted(df['Ação'].unique())
sel_tickers = st.sidebar.multiselect("Tickers", options=tickers, default=tickers)

# Liquidez
min_liq = st.sidebar.number_input("Mínimo de Volume", min_value=0)

# Indicadores
min_ebit_ev = st.sidebar.number_input("Mínimo de EBIT/EV", min_value=0)
min_mom6 = st.sidebar.number_input("Mínimo de Momentum 6M", min_value=-1e9)

# Aplica filtros
df_filt = df.loc[
    (df['Ação'].isin(sel_tickers)) &
    (df['Volume'] >= min_liq) &
    (df['EBIT/EV'] >= min_ebit_ev) &
    (df['Momentum 6M'] >= min_mom6)
]

# Exibição
st.dataframe(df_filt.style.format({"Data": "{%Y-%m-%d}"}), use_container_width=True, hide_index=True)
