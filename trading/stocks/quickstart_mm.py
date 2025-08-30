from estrategia import BigStrategy
from indicadores import MakeIndicator
from data_feed import ReadData
from otimizacao_movel import WalkForwardAnalysis


class MM_estrategia(BigStrategy):

    def __init__(self):
        super().__init__()

    def fazendo_indicadores(self):

        self.sma_rapida = MakeIndicator().media_movel_simples(self.dados.fechamento, 7)
        self.sma_lenta = MakeIndicator().media_movel_simples(self.dados.fechamento, 40)

        self.lista_indicadores = [self.sma_lenta, self.sma_rapida]

    def evento(self, data, i):

        if self.sma_rapida[data] > self.sma_lenta[data]:

            if self.comprado:

                pass

            else:

                self.compra(inverter=True)

        elif self.sma_rapida[data] < self.sma_lenta[data]:

            if self.vendido:
                
                self.comprar_cdi()

                pass

            else:

                self.venda(zerar = True)
                self.comprar_cdi()
               



            
if __name__ == "__main__":

    acao = "B3SA3"

    dados = ReadData(

        caminho_parquet = r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br\cotacoes.parquet',
        tem_multiplas_empresas=True,
        empresa_escolhida=acao,
        nome_coluna_empresas = 'ticker',

        data_inicial = "2010-01-01", 
        data_final = "2023-04-30", 
        
        formato_data = ('%Y-%m-%d'), 

        coluna_data = 0, 
        abertura = 14, 
        minima = 17, 
        maxima = 15, 
        fechamento = 11, 
        volume = 9
    )
    
    start_estrategia = MM_estrategia()

    start_estrategia.corretagem = 0.0005
    
    start_estrategia.add_caminhos(caminho_dados=r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br',
                                  caminho_imagens=r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\imagens')

    start_estrategia.add_data(dados)
    start_estrategia.add_cdi()
    start_estrategia.run_strategy()

    start_estrategia.make_report(nome_arquivo = r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST\analise_tecnica\mm_teste.pdf')

    print(start_estrategia.df_trades)

































































