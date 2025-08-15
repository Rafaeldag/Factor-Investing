import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta  import relativedelta
import os
import streamlit as st
from config import get_carteira_path


carteira_atual = "https://raw.githubusercontent.com/Rafaeldag/quant_invest/main/results/carteiras/atual_carteira1_peso1_ValorDeMercado_EBIT_EV_momento_6_meses_ebit_dl_volume_medio_prop_20_200_21_0.5M_2A.csv"


# carteira_hist = 'carteira1_peso1_ValorDeMercado_EBIT_EV_momento_6_meses_ebit_dl_volume_medio_prop_20_200.csv'
# carteira_atual = 'Carteira_atual.csv'

# caminho_atual = get_carteira_path(carteira_atual)
# caminho_hist = get_carteira_path(carteira_hist)

dados_atual = pd.read_csv(carteira_atual, parse_dates=["data"])

print(dados_atual)
           