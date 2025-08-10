import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta  import relativedelta
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar config
sys.path.append(str(Path(__file__).parent.parent))
from config import (DATA_DIR, RESULTS_DIR, IMAGES_DIR, CARTEIRAS_DIR, 
                   get_data_path, get_results_path, get_carteira_path,
                   get_market_data_path, get_factor_data_path)

class carteira_totais():
     
    def __init__(self, nome_indicador = None, ordem_indicador = None,
                data_inicial = None, data_final = None, nome_arquivo = 'backtest.pdf', nome_arquivo_atual = 'atual.pdf', 
                caminho_imagens = None, caminho_dados = None, **kargs):
        
        

        self.nome_arquivo = nome_arquivo
        # Se não especificado, usa os caminhos padrão do GitHub
        self.caminho_imagens = caminho_imagens if caminho_imagens else IMAGES_DIR
        self.caminho_dados = caminho_dados if caminho_dados else DATA_DIR
        self.nome_arquivo_atual = nome_arquivo_atual

        if nome_indicador == None:

            self.indicadores = kargs

        else:

            self.indicadores = {'carteira1': {
                                            'indicadores': {
                                                nome_indicador: {'caracteristica': ordem_indicador}},                                    
                                            'peso': 1
                                        }}
        
        try:

            data_inicial = datetime.datetime.strptime(data_inicial, "%Y-%m-%d").date()
            data_final = datetime.datetime.strptime(data_final, "%Y-%m-%d").date()

        except:

            data_final = datetime.datetime.strptime(data_final, "%Y-%m-%d").date()

        self.data_inicial = data_inicial
        self.data_final = data_final
        self.dinheiro_inicial = 10000

        os.chdir(caminho_dados)


    def pegando_dados(self):

        # Carrega cotações do diretório de market data
        cotacoes_path = get_market_data_path('cotacoes.parquet')
        cotacoes = pd.read_parquet(cotacoes_path)
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes['ticker'] = cotacoes['ticker'].astype(str)
        self.cotacoes = cotacoes.sort_values('data', ascending=True)

        # Carrega volume mediano do diretório de factor data
        volume_mediano_path = get_factor_data_path('volume_mediano.parquet')
        volume_mediano = pd.read_parquet(volume_mediano_path)
        volume_mediano['data'] = pd.to_datetime(volume_mediano['data']).dt.date
        volume_mediano['ticker'] = volume_mediano['ticker'].astype(str)
        volume_mediano = volume_mediano[['data', 'ticker', 'valor']]
        volume_mediano.columns = ['data', 'ticker', 'volume']

        lista_dfs = []

        lista_dfs.append(self.cotacoes)
        lista_dfs.append(volume_mediano)
        lista_indicadores_sem_rep = []

        for carteira in self.indicadores.values():
            indicadores = carteira['indicadores']

            for indicador in indicadores.keys():

                if indicador in lista_indicadores_sem_rep:

                    pass

                else:

                    lista_indicadores_sem_rep.append(indicador)

                    # Carrega indicador do diretório de factor data
                    indicador_path = get_factor_data_path(f'{indicador}.parquet')
                    lendo_indicador = pd.read_parquet(indicador_path)
                    lendo_indicador['data'] = pd.to_datetime(lendo_indicador['data']).dt.date
                    lendo_indicador['ticker'] = lendo_indicador['ticker'].astype(str)
                    lendo_indicador['valor'] = lendo_indicador['valor'].astype(float)
                    lendo_indicador = lendo_indicador[['data', 'ticker', 'valor']]
                    lendo_indicador.columns = ['data', 'ticker', indicador]
                    lista_dfs.append(lendo_indicador)

        df_dados = lista_dfs[0]

        for df in lista_dfs[1:]:
            # print(df[df.columns[0]].max())
            df_dados = pd.merge(df_dados, df,  how='left', left_on=['data', 'ticker'], right_on=['data', 'ticker'])
            
        self.df_dados = df_dados
        self.df_dados_bruto = df_dados

        # self.df_dados = df_dados.dropna()
        # self.df_dados_bruto = df_dados.dropna()
        
    def criando_carteiras(self):

        df_dados = self.df_dados
        # Mantém o maior volume se as 4 primeiras letras do ticker forem iguais
        df_dados = df_dados.assign(TICKER_PREFIX = df_dados['ticker'].str[:4])
        # df_dados = df_dados.loc[df_dados.groupby(['data', 'TICKER_PREFIX'])['volume'].idxmax()]
        
        df_dados = df_dados.sort_values(by=['data', 'TICKER_PREFIX', 'volume'], ascending=[True, True, False])
        df_dados = df_dados.groupby(['data', 'TICKER_PREFIX'], group_keys=False).first().reset_index()
        
        df_dados = df_dados.drop('TICKER_PREFIX', axis = 1)

        print(max(df_dados['data']))

        lista_df_carteiras = []

        for nome_carteira, carteira in self.indicadores.items():
            df_carteiras = df_dados.copy()
            df_carteiras[f'RANK_FINAL_{nome_carteira}'] = 0
            indicadores = carteira['indicadores']

            for indicador, ordem in indicadores.items():

                crescente_condicao = (ordem['caracteristica'] == 'crescente')
                # Crie os rankings para os indicadores
                df_carteiras[f'{indicador}_RANK_{nome_carteira}'] = df_carteiras.groupby('data')[indicador].rank(ascending = crescente_condicao)
                df_carteiras[f'RANK_FINAL_{nome_carteira}'] = df_carteiras[f'RANK_FINAL_{nome_carteira}'] + df_carteiras[f'{indicador}_RANK_{nome_carteira}']

            df_carteiras[f'posicao_{nome_carteira}'] = df_carteiras.groupby('data')[f'RANK_FINAL_{nome_carteira}'].rank()
            portfolio = df_carteiras
            portfolio = portfolio.assign(peso = carteira['peso']/(portfolio.groupby('data').transform('size')))
            print(portfolio)
            lista_df_carteiras.append(portfolio)

        carteira_por_periodo = pd.concat(lista_df_carteiras, ignore_index=True)
        carteira_por_periodo = carteira_por_periodo.sort_values('data', ascending=True)

        # carteira_por_periodo = carteira_por_periodo.groupby(['data', 'ticker'])['peso'].sum()

        self.carteira_por_periodo = carteira_por_periodo.reset_index()
        
        print(self.carteira_por_periodo)
        
        
    def calcular_retornos_futuros(self):
        # Ordenar o DataFrame por 'TICKER_PREFIX' e 'data'
        self.df_dados = self.df_dados.sort_values(by=['ticker', 'data'])

        def calcular_retornos(df_grupo):
            periodos = [1, 3, 6, 12]
            shifts = [22, 63, 126, 252]
            nomes_colunas = [f'Retorno_{p}D' for p in periodos]

            for periodo, shift, nome_coluna in zip(periodos, shifts, nomes_colunas):
                preco_futuro = df_grupo['preco_fechamento_ajustado'].shift(-shift)
                df_grupo[nome_coluna] = (preco_futuro - df_grupo['preco_fechamento_ajustado']) / df_grupo['preco_fechamento_ajustado']
            return df_grupo

        # Aplicar o groupby e a função de cálculo ao self.df_dados
        self.carteira_por_periodo = self.carteira_por_periodo.groupby('ticker', group_keys=False).apply(calcular_retornos)

        # (Opcional) Resetar o índice se desejar
        self.carteira_por_periodo = self.carteira_por_periodo.reset_index(drop=True)
        self.carteira_por_periodo = self.carteira_por_periodo.sort_values('data', ascending=False)
            
        self.carteira_por_periodo.to_csv(self.nome_arquivo, sep=',', encoding='UTF8', index=False)
        
        
    def salvar_carteira_atual(self):
        # Ordenar o DataFrame por 'TICKER_PREFIX' e 'data'
        self.carteira_atual = self.carteira_por_periodo.copy()
        self.carteira_atual = self.carteira_atual[self.carteira_atual['data'] == max(self.carteira_atual['data'])]
        self.carteira_atual.to_csv(self.nome_arquivo_atual, sep=',', encoding='UTF8', index=False)


if __name__ == "__main__":


    
    dicionario_carteira = {
        'carteira1': {
                'indicadores': {
                    'ValorDeMercado': {'caracteristica': 'crescente'},
                    'EBIT_EV': {'caracteristica': 'decrescente'},
                    'momento_6_meses': {'caracteristica': 'decrescente'},
                    'ebit_dl': {'caracteristica': 'decrescente'},
                    'volume_medio_prop_20_200': {'caracteristica': 'decrescente'},
                    # 'beta_756': {'caracteristica': 'crescente'},
                    # 'ROIC': {'caracteristica': 'decrescente'},
                    # 'mm_7_40': {'caracteristica': 'decrescente'},
                    # 'growth_receita_1': {'caracteristica': 'decrescente'},
                    # 'P_SR': {'caracteristica': 'decrescente'},
                },
                'peso': 1
        },
 }
    
    nome_pdf = ''
    nome_csv = ''

    for nome_carteira, carteira in dicionario_carteira.items():
            
            nome_pdf = nome_pdf + nome_carteira + "_peso" + str(carteira['peso']).replace(".", "")
            nome_csv = nome_csv + nome_carteira + "_peso" + str(carteira['peso']).replace(".", "")

            indicadores = carteira['indicadores']

            for indicador, ordem in indicadores.items():

                nome_pdf = nome_pdf + "_" + indicador
                nome_csv = nome_csv + "_" + indicador
        
    
    nome_arquivo_atual = 'Carteira_atual'


    '''

    Quanto dinheiro o meu modelo aguenta?

    Qual é o meu filtro de liquidez? 1M
    Qual é o número de ativos da carteira? 10
    Qual é a % de cada ativo? 10%
    Quantos dias eu quero demorar pra comprar o modelo? 5
    Quanto eu aceito negociar do volume diário de uma ação por dia? 20%

    1M * 0.2% = 200k/0.1 = 2M * 5 = 10M

    (Filtro liquidez * % do volume negociado * dias que demora pra comprar o modelo)/% em cada ativo = Capacity 

    Capacity = 10M

    '''

    
    # Usa os caminhos padrão do GitHub
    nome_arquivo_path = get_carteira_path(f"{nome_csv}.csv")
    nome_arquivo_atual_path = get_carteira_path(f"{nome_arquivo_atual}.csv")
    
    backtest = carteira_totais(data_inicial='2010-01-01',
                               data_final='2030-04-18',
                               nome_arquivo=str(nome_arquivo_path),
                               nome_arquivo_atual=str(nome_arquivo_atual_path),
                               **dicionario_carteira)


    backtest.pegando_dados()
    backtest.criando_carteiras()
    backtest.calcular_retornos_futuros()
    backtest.salvar_carteira_atual()
