import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta  import relativedelta
from resultados_factor import MakeReportResult
import os
from os import listdir
from os.path import isfile, join
import openpyxl

class backtest_indicators():

    def __init__(self, data_final, filtro_liquidez, balanceamento, numero_ativos, nome_indicador = None, ordem_indicador = None,
                corretagem = 0, impacto_mercado = 0, data_inicial = None, nome_arquivo = 'backtest.pdf', 
                caminho_imagens = None, caminho_dados = None, **kargs):
        
        

        self.nome_arquivo = nome_arquivo
        self.caminho_imagens = caminho_imagens
        self.caminho_dados = caminho_dados

        if nome_indicador == None:

            self.indicadores = kargs

        else:

            self.indicadores = {'carteira1': {
                                            'indicadores': {
                                                nome_indicador: {'caracteristica': ordem_indicador}},                                    
                                            'peso': 1
                                        }}
        
        
        self.balanceamento = balanceamento
        self.liquidez = filtro_liquidez

        try:

            data_inicial = datetime.datetime.strptime(data_inicial, "%Y-%m-%d").date()
            data_final = datetime.datetime.strptime(data_final, "%Y-%m-%d").date()

        except:

            data_final = datetime.datetime.strptime(data_final, "%Y-%m-%d").date()

        self.data_inicial = data_inicial
        self.data_final = data_final
        self.numero_ativos = numero_ativos
        self.corretagem = corretagem
        self.impacto_mercado = impacto_mercado
        self.dinheiro_inicial = 10000

        os.chdir(caminho_dados)


    def pegando_dados(self):

        cotacoes = pd.read_parquet('cotacoes.parquet')
        cotacoes['data'] = pd.to_datetime(cotacoes['data']).dt.date
        cotacoes['ticker'] = cotacoes['ticker'].astype(str)
        self.cotacoes = cotacoes.sort_values('data', ascending=True)

        volume_mediano = pd.read_parquet('volume_mediano.parquet')
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

                    lendo_indicador = pd.read_parquet(f'{indicador}.parquet')
                    lendo_indicador['data'] = pd.to_datetime(lendo_indicador['data']).dt.date
                    lendo_indicador['ticker'] = lendo_indicador['ticker'].astype(str)
                    lendo_indicador['valor'] = lendo_indicador['valor'].astype(float)
                    lendo_indicador = lendo_indicador[['data', 'ticker', 'valor']]
                    lendo_indicador.columns = ['data', 'ticker', indicador]
                    lista_dfs.append(lendo_indicador)

        df_dados = lista_dfs[0]

        for df in lista_dfs[1:]:
            df_dados = pd.merge(df_dados, df,  how='inner', left_on=['data', 'ticker'], right_on=['data', 'ticker'])

        self.df_dados = df_dados.dropna()

        self.df_dados_bruto = df_dados.dropna()


    def filtrando_datas(self):

        df_dados = self.df_dados

        self.data_maxima = max(df_dados['data'])

        if self.data_inicial != None:
            df_dados = df_dados[df_dados['data'] >= self.data_inicial]

        else:
            df_dados = df_dados[df_dados['data'] >= (min(df_dados['data']) + relativedelta(months=+2))]

        df_dados = df_dados[df_dados['data'] < self.data_final]

        self.pegando_dias_das_carteiras(df = df_dados)
        df_dados = self.df_dados[self.df_dados['data'].isin(self.periodos_de_dias)]

        self.df_dados = df_dados

        print(max(df_dados['data']))

    def pegando_dias_das_carteiras(self, df):

        datas_disponiveis = np.sort(df['data'].unique())
        self.periodos_de_dias = [datas_disponiveis[i] for i in range(0, len(datas_disponiveis), self.balanceamento)] #Não vamos precisar no site - Talvez na versão premium gerenciamento automático das cartieira

    def criando_carteiras(self):

        df_dados = self.df_dados
        df_dados = df_dados[df_dados['volume'] > self.liquidez]
        # Mantém o maior volume se as 4 primeiras letras do ticker forem iguais
        df_dados = df_dados.assign(TICKER_PREFIX = df_dados['ticker'].str[:4])
        df_dados = df_dados.loc[df_dados.groupby(['data', 'TICKER_PREFIX'])['volume'].idxmax()]
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
            portfolio = df_carteiras[df_carteiras[f'posicao_{nome_carteira}'] <= self.numero_ativos]
            portfolio = portfolio.assign(peso = carteira['peso']/(portfolio.groupby('data').transform('size')))
            lista_df_carteiras.append(portfolio)

        carteira_por_periodo = pd.concat(lista_df_carteiras, ignore_index=True)
        carteira_por_periodo = carteira_por_periodo.sort_values('data', ascending=True)[['data', 'ticker', 'peso']]

        carteira_por_periodo = carteira_por_periodo.groupby(['data', 'ticker'])['peso'].sum()

        self.carteira_por_periodo = carteira_por_periodo.reset_index()

        print(self.carteira_por_periodo)

    def calculando_retorno_diario(self):

        cotacoes = self.cotacoes[(self.cotacoes['data'] >= self.carteira_por_periodo.iloc[0, 0]) &
                                       (self.cotacoes['data'] <= self.data_final)]
        
        datas_carteira = cotacoes['data'].unique()

        df_retornos = pd.DataFrame(columns=['data', 'dinheiro', 'numero_trade'], index = list(range(0, len(datas_carteira))))

        carteira = 0

        df_retornos.iloc[1, 0] = self.carteira_por_periodo.iloc[1, 0] #segunda data (a primeira foi pra gerar o sinal)
        df_retornos.iloc[1, 1] = self.dinheiro_inicial
        df_retornos.iloc[1, 2] = carteira 
        
        cotacoes = cotacoes.assign(var_fin = cotacoes.groupby('ticker')['preco_fechamento_ajustado'].diff())

        retorno_fin = cotacoes[['data', 'ticker', 'var_fin']]
        
        carteiras = self.carteira_por_periodo.copy()
        datas_rebalanceamento = carteiras['data'].unique()

        cotacoes_rebalanceamento = cotacoes[['ticker', 'data', 'preco_fechamento_ajustado']]

        retorno_fin.set_index(["data", "ticker"], inplace=True)
        carteiras.set_index(["data", "ticker"], inplace=True)
        cotacoes_rebalanceamento.set_index(["data", "ticker"], inplace=True)

        for i, data in enumerate(datas_carteira):

            if i not in [0, 1]:
    
                retorno_fin_dia = retorno_fin.loc[data]

                var_patrimonio_no_dia = (carteira_vigente["quantidade_acoes"] * retorno_fin_dia["var_fin"]).sum()
                df_retornos.iloc[i, 0] = data
                df_retornos.iloc[i, 1] = df_retornos.iloc[i - 1, 1] # Inicializando com o valor do dia anterior
                df_retornos.iloc[i, 1] += var_patrimonio_no_dia  # Agora a operação de adição deve funcionar corretamente
                df_retornos.iloc[i, 2] = carteira

            if data in datas_rebalanceamento:
                carteira_na_data = carteiras.loc[data].copy()
                trocar_carteira = True
                delay = 0
            
            if trocar_carteira:

                if delay == 0:

                    delay = delay + 1 #eu vou simular que eu só compro as açoes no preço de fechamento do dia seguinte.

                else:

                    carteira_na_data["dinheiro_por_acao"] = (carteira_na_data["peso"] * df_retornos.iloc[i, 1]) * (1 - self.corretagem) * (1 - self.impacto_mercado)
                    cotacoes_na_data = cotacoes_rebalanceamento.loc[data]
                    carteira_vigente = pd.merge(carteira_na_data, cotacoes_na_data, left_index=True, right_index=True)
                    carteira_vigente["quantidade_acoes"] = carteira_vigente["dinheiro_por_acao"] / carteira_vigente["preco_fechamento_ajustado"]
                    self.carteira_arquivo = carteira_vigente.copy()
                    carteira += 1
                    trocar_carteira = False

        df_retornos = df_retornos.assign(retorno = df_retornos['dinheiro'].pct_change())
        df_retornos = df_retornos.drop(0, axis = 0)

        self.df_retornos = df_retornos
        print(df_retornos)


    def make_report(self):

        self.carteira_por_periodo = self.carteira_por_periodo.set_index('data')

        MakeReportResult(df_trades=self.df_retornos, df_carteiras=self.carteira_por_periodo, 
                         caminho_imagens=self.caminho_imagens, caminho_benchmarks= self.caminho_dados,
                              nome_arquivo=self.nome_arquivo)
        
        self.carteira_por_periodo.to_csv(rf"C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\indicadores\{nome_csv}", sep=',', encoding='UTF8')


    def carteira_atual(self):

        df_dados = self.df_dados_bruto
        df_dados = df_dados[df_dados['volume'] > self.liquidez]

        # print(max(df_dados['data']))

        df_dados = df_dados[df_dados['data'] == max(df_dados['data'])]
        
        # Mantém o maior volume se as 4 primeiras letras do ticker forem iguais
        df_dados = df_dados.assign(TICKER_PREFIX = df_dados['ticker'].str[:4])
        df_dados = df_dados.loc[df_dados.groupby(['data', 'TICKER_PREFIX'])['volume'].idxmax()]
        df_dados = df_dados.drop('TICKER_PREFIX', axis = 1)


        lista_df_carteiras_atual = []
        colunas = ['data', 'ticker', 'peso', 'RANK_FINAL_carteira1']
               

        for nome_carteira, carteira in self.indicadores.items():
            df_carteiras_atual = df_dados.copy()
            df_carteiras_atual[f'RANK_FINAL_{nome_carteira}'] = 0
            indicadores = carteira['indicadores']

            for indicador, ordem in indicadores.items():

                crescente_condicao = (ordem['caracteristica'] == 'crescente')
                # Crie os rankings para os indicadores
                df_carteiras_atual[f'{indicador}_RANK_{nome_carteira}'] = df_carteiras_atual[indicador].rank(ascending = crescente_condicao)
                df_carteiras_atual[f'RANK_FINAL_{nome_carteira}'] = df_carteiras_atual[f'RANK_FINAL_{nome_carteira}'] + df_carteiras_atual[f'{indicador}_RANK_{nome_carteira}']
                
                coluna = [f'{indicador}_RANK_{nome_carteira}']
                colunas = colunas + coluna
                # print(colunas)
                
                # colunas = colunas.append(f'{indicador}_RANK_{nome_carteira}')
                # print(colunas)

            df_carteiras_atual[f'posicao_{nome_carteira}'] = df_carteiras_atual[f'RANK_FINAL_{nome_carteira}'].rank()
            
            df_carteiras_atual.to_csv(rf"C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\Carteira_atual.csv", sep=',', encoding='UTF8')
            
            portfolio_atual = df_carteiras_atual[df_carteiras_atual[f'posicao_{nome_carteira}'] <= self.numero_ativos]
            portfolio_atual = portfolio_atual.assign(peso = carteira['peso']/(portfolio_atual.groupby('data').transform('size')))
            lista_df_carteiras_atual.append(portfolio_atual)

        carteira_atual = pd.concat(lista_df_carteiras_atual, ignore_index=True)

        carteira_atual = carteira_atual.sort_values(f'RANK_FINAL_{nome_carteira}', ascending=True)[colunas]
        # carteira_atual = carteira_atual.sort_values(f'RANK_FINAL_{nome_carteira}', ascending=True)[colunas]

        carteira_atual = carteira_atual#.groupby(['data', 'ticker'])['peso'].sum()

        self.carteira_atual = carteira_atual.reset_index()

        print(self.carteira_atual)
        
        
    def carteira_atual_trading(self):
        onlyfiles = listdir(r'C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais')
        # print(onlyfiles)
        # print(rf"C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\{nome_xls}")
        if nome_xls in onlyfiles:
            carteira_excel = pd.read_excel(rf"C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\{nome_xls}", sheet_name='Carteira')
            data = carteira_excel.iloc[0, 1].date()
            ultima_carteira = self.carteira_atual.iloc[0, 1]
            
            if (ultima_carteira - data).days >= balanceamento/21*30:
                carteira_atual = self.carteira_atual.copy()
                carteira_atual.to_excel(rf"C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\{nome_xls}", sheet_name='Carteira', index=False)
        else:
            carteira_atual = self.carteira_atual.copy()
            carteira_atual.to_excel(rf"C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais\{nome_xls}", sheet_name='Carteira', index=False)


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
    nome_xls = ''

    for nome_carteira, carteira in dicionario_carteira.items():
            
            nome_pdf = nome_pdf + nome_carteira + "_peso" + str(carteira['peso']).replace(".", "") + "_" 
            nome_csv = nome_csv + nome_carteira + "_peso" + str(carteira['peso']).replace(".", "") + "_" 
            nome_xls = nome_xls + nome_carteira + "_peso" + str(carteira['peso']).replace(".", "") + "_" 

            indicadores = carteira['indicadores']

            for indicador, ordem in indicadores.items():

                nome_pdf = nome_pdf + indicador + "_"
                nome_csv = nome_csv + indicador + "_"
                nome_xls = nome_xls + indicador + "_"

    balanceamento = 21
    filtro_liquidez = 0.5
    numero_ativos = 20


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

    nome_csv = nome_csv + str(balanceamento) + '_' + str(filtro_liquidez) + "M_" + str(numero_ativos) + "A.csv"
    nome_xls = nome_xls + str(balanceamento) + '_' + str(filtro_liquidez) + "M_" + str(numero_ativos) + "A.xlsx"
    nome_pdf = nome_pdf + str(balanceamento) + '_' + str(filtro_liquidez) + "M_" + str(numero_ativos) + "A.pdf"

    backtest = backtest_indicators(data_final="2025-12-30", data_inicial= '2001-01-01', filtro_liquidez=(filtro_liquidez * 1000000), balanceamento=balanceamento, 
                                                numero_ativos=numero_ativos, caminho_dados=r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br',
                                            caminho_imagens=r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\imagens', corretagem=0.0,
                                                nome_arquivo=fr'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\indicadores\{nome_pdf}',
                                            **dicionario_carteira)
    

    backtest.pegando_dados()
    backtest.filtrando_datas()
    backtest.criando_carteiras()
    backtest.calculando_retorno_diario()
    backtest.make_report()

    backtest.carteira_atual()
    backtest.carteira_atual_trading()

    