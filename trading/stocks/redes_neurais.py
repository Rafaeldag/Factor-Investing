import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

cotacoes = pd.read_parquet(r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br\cotacoes.parquet')

acao_escolhida = 'MGLU3'

dados = cotacoes[cotacoes['ticker'] == acao_escolhida]

datas = pd.to_datetime(dados['data'].iloc[:-1]).dt.date
dados = dados[['preco_fechamento_ajustado']]

dados['cotacao_dia_seguinte'] = dados['preco_fechamento_ajustado'].shift(-1)
dados = dados.dropna()
dados

tamanho_dados_treinamento = int(len(dados) * 0.8)

#vamos escalar os dados entre 0 e 1. 
#Mas tem que escalar os dados de teste e treino individualmente! 
escalador_treinamento = MinMaxScaler(feature_range=(0, 1))
escalador_teste = MinMaxScaler(feature_range=(0, 1))

dados_entre_0_e_1_treinamento = escalador_treinamento.fit_transform(dados.iloc[0: tamanho_dados_treinamento, :])

dados_entre_0_e_1_teste = escalador_teste.fit_transform(dados.iloc[tamanho_dados_treinamento: , :])

x_treinamento = dados_entre_0_e_1_treinamento[:,0]
y_treinamento = dados_entre_0_e_1_treinamento[:,1]

x_teste = dados_entre_0_e_1_teste[:,0]
y_teste = dados_entre_0_e_1_teste[:,1]

x_treinamento

x_treinamento = x_treinamento.reshape(x_treinamento.shape[0], 1, 1)
y_treinamento = y_treinamento.reshape(y_treinamento.shape[0], 1, 1)
x_teste = x_teste.reshape(x_teste.shape[0], 1, 1)
y_teste = y_teste.reshape(y_teste.shape[0], 1, 1)

inputs = keras.layers.Input(shape=(x_treinamento.shape[1], 1)) #1 "X" e 1 output pra esse X. 
x = keras.layers.LSTM(150, return_sequences= True)(inputs)
x = keras.layers.LSTM(150, return_sequences=True)(x)
x = keras.layers.LSTM(150, return_sequences=True)(x)
outputs = keras.layers.Dense(1, activation='linear')(x)

rede_neural = keras.Model(inputs=inputs, outputs=outputs)
rede_neural.compile(optimizer='adam', loss="mse")
rede_neural.summary()

rede_neural.fit(
    x_treinamento, y_treinamento,
    epochs = 2,
    batch_size = 32,
    validation_split = 0.2
)

precos_preditos = rede_neural.predict(x_teste)

precos_preditos = precos_preditos.reshape(precos_preditos.shape[0], 1)
x_treinamento = x_treinamento.reshape(x_treinamento.shape[0], 1)
y_treinamento = y_treinamento.reshape(y_treinamento.shape[0], 1)
x_teste = x_teste.reshape(x_teste.shape[0], 1)
y_teste = y_teste.reshape(y_teste.shape[0], 1)

dados_teste = np.concatenate((x_teste, y_teste),axis=1)
dados_preditos = np.concatenate((x_teste, precos_preditos),axis=1)

#tirando escalas dos dados

precos_teste_reais = escalador_teste.inverse_transform(dados_teste)
precos_teste_preditos = escalador_teste.inverse_transform(dados_preditos)

fig, ax = plt.subplots(figsize = (10, 4))

ax.plot(datas.iloc[tamanho_dados_treinamento:], precos_teste_reais[:, 1], label = 'Real')
ax.plot(datas.iloc[tamanho_dados_treinamento:], precos_teste_preditos[:, 1], label = 'Modelo')

plt.legend()

df = pd.DataFrame(precos_teste_preditos, index = datas.iloc[tamanho_dados_treinamento:])

df.columns = ['preco', 'preco_predito_dia_seguinte']

df['retorno'] = df['preco'].pct_change()

df['comprado_vendido'] = pd.NA

df.loc[df['preco_predito_dia_seguinte'] > df['preco'], 'comprado_vendido'] = 'comprado'
df.loc[df['preco_predito_dia_seguinte'] < df['preco'], 'comprado_vendido'] = 'vendido'

df['acertos'] = pd.NA

df.loc[(df['comprado_vendido'] == 'comprado') & (df['retorno'] > 0), 'acertos'] = 1
df.loc[(df['comprado_vendido'] == 'comprado') & (df['retorno'] < 0), 'acertos'] = 0
df.loc[(df['comprado_vendido'] == 'vendido') & (df['retorno'] > 0), 'acertos'] = 0
df.loc[(df['comprado_vendido'] == 'vendido') & (df['retorno'] < 0), 'acertos'] = 1
df.loc[df['acertos'].isna(), 'acertos'] = 0

df = df.dropna()

acertou_o_lado = df['acertos'].sum()/len(df)
errou_o_lado = 1 - acertou_o_lado

df['retorno_absoluto'] = df['retorno'].abs()

media_lucros_e_perdas = df.groupby('acertos')['retorno_absoluto'].mean()
print(media_lucros_e_perdas)

exp_mat_lucro = acertou_o_lado * media_lucros_e_perdas[1] - media_lucros_e_perdas[0] * errou_o_lado

df['retorno_modelo'] = pd.NA

df.loc[df['acertos'] == True, 'retorno_modelo'] = df.loc[df['acertos'] == True]['retorno_absoluto']
df.loc[df['acertos'] == False, 'retorno_modelo'] = df.loc[df['acertos'] == False]['retorno_absoluto'] * - 1

df['retorno_acum_modelo'] = (1 + df['retorno_modelo']).cumprod() - 1
df['retorno_acum_acao'] = (1 + df['retorno']).cumprod() - 1

retornos = df[['retorno_acum_modelo', 'retorno_acum_acao']]

retornos.plot() 
print(retornos)