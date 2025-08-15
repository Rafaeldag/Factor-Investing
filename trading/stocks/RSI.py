from estrategia import BigStrategy
from indicadores import MakeIndicator
from data_feed import ReadData
from otimizacao_movel import WalkForwardAnalysis

class RSI_estrategia(BigStrategy):

    def __init__(self):
        super().__init__()

    
    def fazendo_indicadores(self):

        self.rsi = MakeIndicator().RSI(self.dados.fechamento, self.parametro1)

        self.lista_indicadores = [self.rsi]

    def evento(self, data, i):

        if self.rsi[data] > 60 and (self.comprado == False): #reversão a média!
            
            self.vender_cdi()

            self.compra()
            self.barra_executada = i

        elif self.rsi[data] <= 50 and self.comprado:

            self.venda(zerar = True)
            
            self.comprar_cdi()

  

if __name__ == '__main__':

    acao = "PETR4"

    dados = ReadData(

        caminho_parquet = r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br\cotacoes.parquet',
        tem_multiplas_empresas=True,
        empresa_escolhida=acao,
        nome_coluna_empresas = 'ticker',

        data_inicial = "2010-01-01", 
        data_final = "2023-04-18", 
        
        formato_data = ('%Y-%m-%d'), 

        coluna_data = 0, 
        abertura = 14, 
        minima = 17, 
        maxima = 15, 
        fechamento = 11, 
        volume = 9
    )
    

    walk = WalkForwardAnalysis(estrategia = RSI_estrategia(), class_dados = dados, parametro2= range(5, 30, 5),
                               parametro1= range(7, 50, 3), anos_otimizacao=2, anos_teste=1, 
                               nome_arquivo = rf"C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\analise_tecnica\backtest_2pra1_{acao}_RSI.pdf",
                               caminho_dados_benchmarks =r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br',
                               caminho_imagens= r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\imagens')

    
    walk.run_walk()

