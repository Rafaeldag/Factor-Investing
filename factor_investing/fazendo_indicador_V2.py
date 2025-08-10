import pandas as pd
import os
import numpy as np
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar config
sys.path.append(str(Path(__file__).parent.parent))
from config import (get_data_path, get_market_data_path, get_factor_data_path)

#A COLUNA COM O INDICADOR TEM QUE SE CHAMAR "valor"

class MakeIndicator():

    def __init__(self, caminho_dados=None):
        # Se não especificado, usa os caminhos padrão do config
        # Não mudamos mais de diretório, usamos caminhos absolutos
        pass

    def fazer_indicador_momento(self, meses):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes = cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]

        # print(max(cotacoes['data']))

        cotacoes['valor'] = cotacoes.groupby('ticker')['preco_fechamento_ajustado'].pct_change(periods = (meses * 21))
        cotacoes.loc[cotacoes['valor'] == 0, 'valor'] = pd.NA
        cotacoes.loc[cotacoes['valor'] == np.inf, 'valor'] = pd.NA
        cotacoes = cotacoes.dropna()
        valor = cotacoes[['data', 'ticker', 'valor']]

        print(max(valor['data']))

        valor.to_parquet(get_factor_data_path(f'momento_{meses}_meses.parquet'), index = False)

    def volume_mediano(self):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date

        cotacoes = cotacoes[['data', 'ticker', 'volume_negociado']]
        cotacoes['volume_negociado'] = cotacoes.groupby('ticker')['volume_negociado'].fillna(0)
        cotacoes['valor'] = cotacoes.groupby('ticker')['volume_negociado'].rolling(21).median().reset_index(0,drop=True)
        cotacoes = cotacoes.dropna()
        valor = cotacoes[['data', 'ticker', 'valor']]

        print(max(valor['data']))

        valor.to_parquet(get_factor_data_path(f'volume_mediano.parquet'), index = False)


    def ebit_divida_liquida(self):

        df_ebit = pd.read_parquet(get_factor_data_path('EBIT.parquet'))
        df_ebit = df_ebit.assign(id_dado = df_ebit['ticker'].astype(str) + "_" + df_ebit['data'].astype(str))
        df_ebit['valor'] = df_ebit['valor'].astype(float)
        df_ebit = df_ebit[['ticker', 'data', 'id_dado', 'valor']]
        df_ebit.columns = ['ticker', 'data', 'id_dado', 'ebit']

        df_divida_liquida = pd.read_parquet(get_factor_data_path('DividaLiquida.parquet'))
        df_divida_liquida = df_divida_liquida.assign(id_dado = df_divida_liquida['ticker'].astype(str) + "_" + df_divida_liquida['data'].astype(str))
        df_divida_liquida['valor'] = df_divida_liquida['valor'].astype(float)
        df_divida_liquida = df_divida_liquida[['id_dado', 'valor']]
        df_divida_liquida.columns = ['id_dado', 'divida']

        df_indicadores = pd.merge(df_ebit, df_divida_liquida, how = 'inner', on = 'id_dado')
        df_indicadores['ebit_DL'] = pd.NA
        df_indicadores.loc[df_indicadores['divida'] <= 0, 'ebit_DL'] = 999
        df_indicadores.loc[df_indicadores['ebit'] <= 0, 'ebit_DL'] = -999
        df_indicadores.loc[df_indicadores['ebit_DL'].isna(), 'ebit_DL'] = (df_indicadores[df_indicadores['ebit_DL'].isna()]['ebit']/
                                                                df_indicadores[df_indicadores['ebit_DL'].isna()]['divida'])
        df_indicadores = df_indicadores[['data', 'ticker', 'ebit_DL']]
        df_indicadores.columns = ['data', 'ticker', 'valor'] 

        df_indicadores.to_parquet(get_factor_data_path(f'ebit_dl.parquet'), index = False)

        print(max(df_indicadores['data']))


    def pl_divida_bruta(self):

        df_pl = pd.read_parquet(get_factor_data_path('PatrimonioLiquido.parquet'))
        df_pl = df_pl.dropna()
        df_pl = df_pl.assign(id_dado = df_pl['ticker'].astype(str) + "_" + df_pl['data'].astype(str))
        df_pl['valor'] = df_pl['valor'].astype(float)
        df_pl = df_pl[['data', 'ticker', 'valor', 'id_dado']]
        df_pl.columns = ['data', 'ticker', 'patrimonio_liquido', 'id_dado']

        df_divida_bruta = pd.read_parquet(get_factor_data_path('DividaBruta.parquet'))
        df_divida_bruta[df_divida_bruta['valor'] == '0.0'] = pd.NA
        df_divida_bruta = df_divida_bruta.dropna()
        df_divida_bruta = df_divida_bruta.assign(id_dado = df_divida_bruta['ticker'].astype(str) + "_" + df_divida_bruta['data'].astype(str))
        df_divida_bruta['valor'] = df_divida_bruta['valor'].astype(float)
        df_divida_bruta = df_divida_bruta[['id_dado', 'valor']]
        df_divida_bruta.columns = ['id_dado', 'divida']

        df_indicadores = pd.merge(df_pl, df_divida_bruta, how = 'inner', on = 'id_dado')
        df_indicadores['PL_DB'] = pd.NA
        df_indicadores.loc[df_indicadores['patrimonio_liquido'] <= 0, 'PL_DB'] = 0
        df_indicadores.loc[df_indicadores['PL_DB'].isna(), 'PL_DB'] = (df_indicadores[df_indicadores['PL_DB'].isna()]['patrimonio_liquido']/
                                                                df_indicadores[df_indicadores['PL_DB'].isna()]['divida'])
        df_indicadores = df_indicadores[['data', 'ticker', 'PL_DB']]
        df_indicadores.columns = ['data', 'ticker', 'valor'] 

        df_indicadores.to_parquet(get_factor_data_path('pl_db.parquet'), index = False)

        print(max(df_indicadores['data']))

    def volatilidade(self, anos):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes = cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]
        cotacoes['retorno'] = cotacoes.groupby('ticker')['preco_fechamento_ajustado'].pct_change()
        cotacoes.loc[cotacoes['retorno'] == 0, 'retorno'] = pd.NA
        cotacoes.loc[cotacoes['retorno'] == np.inf, 'retorno'] = pd.NA
        cotacoes['valor'] = cotacoes.groupby('ticker')['retorno'].rolling(window=int(252 * anos), min_periods=int(252 * anos * 0.8)).std().reset_index(0,drop=True)
        cotacoes = cotacoes.dropna()
        cotacoes['valor'] = cotacoes['valor'] * np.sqrt(252) 
        valor = cotacoes[['data', 'ticker', 'valor']]

        valor.to_parquet(get_factor_data_path(f'vol_{int(252 * anos)}.parquet'), index = False)

    def beta(self, anos):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        cotaoces_ibov = pd.read_parquet(get_market_data_path('ibov.parquet'))


        cotaoces_ibov.loc['5846'] = ['2023-08-10', 118349.60]

        cotaoces_ibov['retorno_ibov'] = cotaoces_ibov['fechamento'].pct_change()
        cotaoces_ibov = cotaoces_ibov[['data', 'retorno_ibov']]
        cotaoces_ibov['data'] = pd.to_datetime(cotaoces_ibov['data']).dt.date

        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes = cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]
        cotacoes['retorno'] = cotacoes.groupby('ticker')['preco_fechamento_ajustado'].pct_change()
        cotacoes.loc[cotacoes['retorno'] == 0, 'retorno'] = pd.NA
        cotacoes.loc[cotacoes['retorno'] == np.inf, 'retorno'] = pd.NA

        dados_totais = pd.merge(cotacoes, cotaoces_ibov, on='data', how='inner')

        empresas = dados_totais['ticker'].unique()
        dados_totais = dados_totais.set_index('ticker')
        lista_df_betas = []

        for empresa in empresas:

            dado_empresa = dados_totais.loc[empresa]

            if dado_empresa.dropna().empty == False:

                if len(dado_empresa) > int(252 * anos):

                    datas = dado_empresa.data.values
                    exog = sm.add_constant(dado_empresa.retorno_ibov)
                    model = RollingOLS(endog=dado_empresa.retorno.values, exog=exog, 
                                    window=int(252 * anos), min_nobs = int(252 * anos * 0.8))
                    betas = model.fit()
                    betas = betas.params
                    dado_empresa = betas.reset_index()
                    dado_empresa['data'] = datas
                    dado_empresa.columns = ['ticker', 'const', 'valor', 'data']
                    dado_empresa = dado_empresa[['data', 'ticker', 'valor']]
                    dado_empresa = dado_empresa.dropna()
                    lista_df_betas.append(dado_empresa)

        betas = pd.concat(lista_df_betas)
        betas.to_parquet(get_factor_data_path(f'beta_{int(252 * anos)}.parquet'), index = False)


    def media_movel_proporcao(self, mm_curta, mm_longa):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes = cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]
        cotacoes['media_curta'] = cotacoes.groupby('ticker')['preco_fechamento_ajustado'].rolling(window=mm_curta, min_periods=int(mm_curta * 0.8)).mean().reset_index(0,drop=True)
        cotacoes['media_longa'] = cotacoes.groupby('ticker')['preco_fechamento_ajustado'].rolling(window=mm_longa, min_periods=int(mm_longa * 0.8)).mean().reset_index(0,drop=True)
        cotacoes['valor'] = cotacoes['media_curta']/cotacoes['media_longa']
        valor = cotacoes[['data', 'ticker', 'valor']]
        valor = valor.dropna()

        valor.to_parquet(get_factor_data_path(f'mm_{mm_curta}_{mm_longa}.parquet'), index = False)

        print(max(valor['data']))

    def media_movel_volume_proporcao(self, n_dias_curto, n_dias_longo):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        # print(cotacoes.columns)
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes = cotacoes[['data', 'ticker', 'volume_negociado']]
        cotacoes['volume_curto'] = cotacoes.groupby('ticker')['volume_negociado'].rolling(window=n_dias_curto, min_periods=int(n_dias_curto * 0.8)).mean().reset_index(0,drop=True)
        cotacoes['volume_longo'] = cotacoes.groupby('ticker')['volume_negociado'].rolling(window=n_dias_longo, min_periods=int(n_dias_longo * 0.8)).mean().reset_index(0,drop=True)
        cotacoes['valor'] = cotacoes['volume_curto']/cotacoes['volume_longo']

        volume_medio = cotacoes[['data', 'ticker', 'valor']]
        volume_medio.to_parquet(get_factor_data_path(f'volume_medio_prop_{n_dias_curto}_{n_dias_longo}.parquet'), index = False)

        print(max(volume_medio['data']))

    def media_movel_volume(self, n_dias):

        cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))
        # print(cotacoes.columns)
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes = cotacoes[['data', 'ticker', 'volume_negociado']]
        cotacoes['valor'] = cotacoes.groupby('ticker')['volume_negociado'].rolling(window=n_dias, min_periods=int(n_dias * 0.8)).mean().reset_index(0,drop=True)

        volume_medio = cotacoes[['data', 'ticker', 'valor']]
        volume_medio.to_parquet(get_factor_data_path(f'volume_medio{n_dias}.parquet'), index = False)

    
    def cagr_lucro_anos(self, anos):

        df_lucros = pd.read_parquet(get_factor_data_path('LucroLiquido.parquet'))
        df_lucros['data'] = pd.to_datetime(df_lucros['data']).dt.date
        df_lucros = df_lucros.sort_values('data', ascending=True)

        df_lucros_x_anos_atras = df_lucros.copy()

        df_lucros['x_anos_atras'] = df_lucros['data'] - pd.DateOffset(years = anos)
        df_lucros['x_anos_atras'] = pd.to_datetime(df_lucros['x_anos_atras']).dt.date

        df_lucros_x_anos_atras = df_lucros_x_anos_atras.rename(columns={'data': 'x_anos_atras', 'valor': 'valor_x_anos_atras'})

        df_cagr = df_lucros.merge(df_lucros_x_anos_atras[['ticker', 'x_anos_atras', 'valor_x_anos_atras']], on = ['ticker', 'x_anos_atras'], suffixes=('', '_X_anos_atras'))
        df_cagr['cagr'] = df_cagr['valor']/df_cagr['valor_x_anos_atras']
        df_cagr = df_cagr[['data', 'ticker', 'cagr']].rename(columns={'cagr': 'valor'})
        df_cagr.to_parquet(get_factor_data_path(f'growth_lucro_{anos}.parquet'), index = False)

    def cagr_receita_anos(self, anos):

        df_receita = pd.read_parquet(get_factor_data_path('ReceitaLiquida.parquet'))
        df_receita['data'] = pd.to_datetime(df_receita['data']).dt.date
        df_receita = df_receita.sort_values('data', ascending=True)

        df_receita_x_anos_atras = df_receita.copy()

        df_receita['x_anos_atras'] = df_receita['data'] - pd.DateOffset(years = anos)
        df_receita['x_anos_atras'] = pd.to_datetime(df_receita['x_anos_atras']).dt.date

        df_receita_x_anos_atras = df_receita_x_anos_atras.rename(columns={'data': 'x_anos_atras', 'valor': 'valor_x_anos_atras'})

        df_cagr = df_receita.merge(df_receita_x_anos_atras[['ticker', 'x_anos_atras', 'valor_x_anos_atras']], on = ['ticker', 'x_anos_atras'], suffixes=('', '_X_anos_atras'))
        df_cagr['cagr'] = df_cagr['valor']/df_cagr['valor_x_anos_atras']
        df_cagr = df_cagr[['data', 'ticker', 'cagr']].rename(columns={'cagr': 'valor'})
        df_cagr.to_parquet(get_factor_data_path(f'growth_receita_{anos}.parquet'), index = False)
        


if __name__ == "__main__":

    # Agora usa os caminhos padrão do config automaticamente
    indicador = MakeIndicator()

    indicador.fazer_indicador_momento(meses=12)
    indicador.fazer_indicador_momento(meses=1)
    indicador.fazer_indicador_momento(meses=6)
    indicador.volume_mediano()
    indicador.media_movel_proporcao(7, 40)
    indicador.beta(3)
    indicador.volatilidade(1)
    indicador.pl_divida_bruta()
    indicador.ebit_divida_liquida()
    indicador.media_movel_volume_proporcao(5,60)
    indicador.media_movel_volume_proporcao(20,200)
    indicador.cagr_lucro_anos(3)
    indicador.cagr_lucro_anos(1)
    indicador.cagr_lucro_anos(5)
    indicador.cagr_receita_anos(1)
    indicador.cagr_receita_anos(3)
    indicador.cagr_receita_anos(5)
