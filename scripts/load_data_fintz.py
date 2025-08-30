import requests
import pandas as pd
import os
import urllib.request
from dotenv import load_dotenv
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar config
sys.path.append(str(Path(__file__).parent.parent))
from config import (get_data_path, DATA_DIR, MARKET_DATA_DIR, FACTOR_DATA_DIR,
                   get_market_data_path, get_factor_data_path)

load_dotenv()

class dados_fintz:

    def __init__(self, caminho_dados=None):
        
        self.chave_api = os.getenv("API_FINTZ")
        self.headers = {'accept': 'application/json',
                        'X-API-Key': self.chave_api}
        
        # Se não especificado, usa o diretório de dados padrão do GitHub
        if caminho_dados is None:
            self.caminho_dados = DATA_DIR
        else:
            self.caminho_dados = Path(caminho_dados)
        
        # Garante que o diretório existe
        self.caminho_dados.mkdir(parents=True, exist_ok=True)
        os.chdir(self.caminho_dados)

    def cdi(self):

        response = requests.get('https://api.fintz.com.br/taxas/historico?codigo=12&dataInicio=2000-01-01&ordem=ASC',
                                headers=self.headers)
    
        cdi = pd.DataFrame(response.json())

        cdi = cdi.drop(["dataFim", 'nome'], axis = 1)

        cdi.columns = ['data', 'retorno']

        cdi['retorno'] = cdi['retorno']/100 

        # Salva no diretório de dados de mercado
        caminho_cdi = get_market_data_path('cdi.parquet')
        cdi.to_parquet(caminho_cdi, index = False)

        # print(max(cdi['data']))


    def ibov(self):

        response = requests.get('https://api.fintz.com.br/indices/historico?indice=IBOV&dataInicio=2000-01-01',
                                headers=self.headers)

        df = pd.DataFrame(response.json())

        df = df.sort_values('data', ascending=True)

        df.columns = ['indice', 'data', 'fechamento']

        df = df.drop('indice', axis = 1)

        # Salva no diretório de dados de mercado
        caminho_ibov = get_market_data_path('ibov.parquet')
        df.to_parquet(caminho_ibov, index = False)  

        # print(max(df['data']))        

    def pegar_cotacoes(self):
        
        
        response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/cotacoes/historico/arquivos?classe=ACOES&preencher=true', 
                                headers=self.headers)

        link_download = (response.json())['link']

        # Download temporário
        urllib.request.urlretrieve(link_download, f"cotacoes_temp.parquet")

        df = pd.read_parquet('cotacoes_temp.parquet')

        colunas_pra_ajustar = ['preco_abertura', 'preco_maximo', 'preco_medio', 'preco_minimo']

        for coluna in colunas_pra_ajustar:

            df[f'{coluna}_ajustado'] = df[coluna] * df['fator_ajuste']

        df['preco_fechamento_ajustado'] = df.groupby('ticker')['preco_fechamento_ajustado'].transform('ffill')

        df = df.sort_values('data', ascending=True)

        # Salva no diretório de dados de mercado
        caminho_cotacoes = get_market_data_path('cotacoes.parquet')
        df.to_parquet(caminho_cotacoes, index = False)
        
        # Remove arquivo temporário
        if os.path.exists('cotacoes_temp.parquet'):
            os.remove('cotacoes_temp.parquet') 

        print(max(df['data']))


    def pegando_arquivo_contabil(self, demonstracao = False, indicadores = False, nome_dado = '', prazo = ''):

        if demonstracao:

            try:

                response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/itens-contabeis/point-in-time/arquivos?item={nome_dado}&tipoPeriodo={prazo}',  
                                        headers=self.headers)
            
            except:

                print("Demonstração não encontrada!")
                exit()
            
            link_download = (response.json())['link']
            # Download temporário
            urllib.request.urlretrieve(link_download, f"{nome_dado}_temp.parquet")

            df = pd.read_parquet(f"{nome_dado}_temp.parquet")
            
            # Salva no diretório de dados de fatores
            caminho_factor = get_factor_data_path(f"{nome_dado}.parquet")
            df.to_parquet(caminho_factor, index=False)
            
            # Remove arquivo temporário
            if os.path.exists(f"{nome_dado}_temp.parquet"):
                os.remove(f"{nome_dado}_temp.parquet")
            # print(max(df['data']))

        elif indicadores:

            try:

                response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/indicadores/point-in-time/arquivos?indicador={nome_dado}&tipoPeriodo=12M',  
                                        headers=self.headers)
            
            except:

                print("Indicador não encontrado!")
                exit()

            link_download = (response.json())['link']
            # Download temporário
            urllib.request.urlretrieve(link_download, f"{nome_dado}_temp.parquet")

            df = pd.read_parquet(f"{nome_dado}_temp.parquet")
            
            # Salva no diretório de dados de fatores
            caminho_factor = get_factor_data_path(f"{nome_dado}.parquet")
            df.to_parquet(caminho_factor, index=False)
            
            # Remove arquivo temporário
            if os.path.exists(f"{nome_dado}_temp.parquet"):
                os.remove(f"{nome_dado}_temp.parquet")
            # print(max(df['data']))

        else:

            print("Escolha uma demonstração ou indicador.")


if __name__ == "__main__":

    # Usa o caminho padrão do GitHub (pasta data/)
    lendo_dados = dados_fintz()

    # lendo_dados.pegar_cotacoes()

    lista_demonstracoes = {
                           'EBIT': "12M",
                           'DividaBruta': "TRIMESTRAL",
                           'DividaLiquida': "TRIMESTRAL",
                           'LucroLiquido': "12M",
                           'PatrimonioLiquido': "TRIMESTRAL",
                           'ReceitaLiquida': "12M",
                            }
    lista_indicadores = [
                         'EBIT_EV',
                         'ValorDeMercado',
                         'L_P',
                         'ROE',
                         'ROIC',
                         'LiquidezCorrente',
                         'MargemEBITDA',
                         'MargemLiquida',
                        #  'EBITDA_EV',
                        #  'P_EBITDA',
                        #  'P_EBIT',
                        #  'P_SR',
                        #  'DividaLiquida_EBITDA',
                        #  'DividaLiquida_EBIT',
                         ]


    for key, value in lista_demonstracoes.items():

        # print(key)

        lendo_dados.pegando_arquivo_contabil(demonstracao=True, nome_dado = key, prazo=value)

    for indicador in lista_indicadores:

        # print(indicador)

        lendo_dados.pegando_arquivo_contabil(indicadores=True, nome_dado = indicador)


    lendo_dados.cdi()
    lendo_dados.pegar_cotacoes()
    lendo_dados.ibov()