# Atualização da Estrutura de Dados

Este documento descreve as mudanças na organização dos diretórios de dados do sistema quant_invest.

## 🔄 Mudanças Implementadas

### Nova Estrutura de Diretórios

```
quant_invest/
├── data/
│   ├── market_data/        # 📈 Dados de mercado
│   │   ├── cotacoes.parquet
│   │   ├── cdi.parquet
│   │   └── ibov.parquet
│   ├── factors_data/       # 📊 Dados de fatores e indicadores contábeis
│   │   ├── EBIT.parquet
│   │   ├── ValorDeMercado.parquet
│   │   ├── DividaBruta.parquet
│   │   ├── DividaLiquida.parquet
│   │   ├── LucroLiquido.parquet
│   │   ├── PatrimonioLiquido.parquet
│   │   ├── ReceitaLiquida.parquet
│   │   ├── EBIT_EV.parquet
│   │   └── volume_mediano.parquet
│   └── premios_risco/      # 📈 Prêmios de risco calculados
└── results/
    ├── carteiras/          # 💼 Arquivos de carteiras
    ├── images/             # 📸 Gráficos e imagens
    ├── pdfs/               # 📄 Relatórios em PDF
    └── indicadores/        # 📊 Resultados de indicadores
```

### Separação por Tipo de Dado

#### 📈 `data/market_data/` - Dados de Mercado
- **cotacoes.parquet**: Preços históricos de ações
- **cdi.parquet**: Taxa CDI histórica
- **ibov.parquet**: Índice Ibovespa histórico

#### 📊 `data/factors_data/` - Dados de Fatores
- **Demonstrações contábeis**: EBIT, DividaBruta, DividaLiquida, etc.
- **Indicadores**: EBIT_EV, ValorDeMercado, etc.
- **Outros**: volume_mediano, etc.

## 🛠️ Arquivos Modificados

### 1. `config.py`
- ✅ Adicionado `MARKET_DATA_DIR` e `FACTOR_DATA_DIR`
- ✅ Criadas funções `get_market_data_path()` e `get_factor_data_path()`
- ✅ Atualizados caminhos específicos (COTACOES_PATH, CDI_PATH, etc.)

### 2. `data/load_data_fintz_v2.py`
- ✅ CDI salvo em `data/market_data/cdi.parquet`
- ✅ IBOV salvo em `data/market_data/ibov.parquet`  
- ✅ Cotações salvas em `data/market_data/cotacoes.parquet`
- ✅ Demonstrações contábeis salvas em `data/factors_data/`
- ✅ Indicadores salvos em `data/factors_data/`

### 3. `factor_investing/calculadora_factor.py`
- ✅ Carregamento de cotações de `market_data/`
- ✅ Carregamento de indicadores de `factors_data/`
- ✅ Atualizado para usar as novas funções de path

### 4. `factor_investing/factor_todos_dias.py`
- ✅ Carregamento de cotações de `market_data/`
- ✅ Carregamento de indicadores de `factors_data/`
- ✅ Atualizado para usar as novas funções de path

### 5. `trading/stocks/estrategia.py`
- ✅ Carregamento de CDI de `market_data/`
- ✅ Atualizado para usar `get_market_data_path()`

## 📚 Como Usar a Nova Estrutura

### Importar Configurações
```python
from config import (
    get_market_data_path,
    get_factor_data_path,
    get_results_path,
    get_carteira_path
)
```

### Carregar Dados de Mercado
```python
# CDI
cdi = pd.read_parquet(get_market_data_path('cdi.parquet'))

# Cotações
cotacoes = pd.read_parquet(get_market_data_path('cotacoes.parquet'))

# IBOV
ibov = pd.read_parquet(get_market_data_path('ibov.parquet'))
```

### Carregar Dados de Fatores
```python
# EBIT
ebit = pd.read_parquet(get_factor_data_path('EBIT.parquet'))

# Valor de Mercado
valor_mercado = pd.read_parquet(get_factor_data_path('ValorDeMercado.parquet'))

# Indicadores
ebit_ev = pd.read_parquet(get_factor_data_path('EBIT_EV.parquet'))
```

### Salvar Resultados
```python
# Carteiras
carteira.to_csv(get_carteira_path('minha_carteira.csv'))

# Relatórios
resultado.to_csv(get_results_path('indicadores', 'backtest_resultado.csv'))
```

## 🎯 Benefícios da Nova Estrutura

1. **📂 Organização Clara**: Separação lógica entre dados de mercado e fatores
2. **🔍 Facilita Localização**: Easier to find specific types of data
3. **🚀 Performance**: Carregamento mais eficiente
4. **🔧 Manutenção**: Easier to maintain and backup specific data types
5. **📈 Escalabilidade**: Easy to add new data categories

## ✅ Teste da Implementação

Execute o script de teste para verificar se tudo está funcionando:

```bash
python test_migration.py
```

O teste verifica:
- ✅ Criação automática de diretórios
- ✅ Funcionamento das funções de path
- ✅ Salvamento e carregamento de arquivos
- ✅ Estrutura completa do sistema

## 🔄 Migração de Dados Existentes

Se você tem dados nos caminhos antigos, será necessário movê-los:

```bash
# Mover dados de mercado
move cotacoes.parquet data/market_data/
move cdi.parquet data/market_data/
move ibov.parquet data/market_data/

# Mover dados de fatores
move EBIT.parquet data/factors_data/
move ValorDeMercado.parquet data/factors_data/
# ... outros indicadores
```

## 🚨 Importante

- Todos os novos downloads de dados usarão automaticamente a nova estrutura
- Scripts antigos continuarão funcionando com paths relativos
- Para melhor performance, atualize scripts para usar as novas funções
- O sistema cria automaticamente os diretórios necessários
