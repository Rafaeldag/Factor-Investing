# Guia de Migração - GitHub Paths

Este documento descreve as alterações feitas para migrar todos os caminhos hardcoded do sistema para usar o repositório GitHub.

## Mudanças Principais

### 1. Arquivo de Configuração Central (`config.py`)
- Criado arquivo `config.py` na raiz do projeto
- Define todos os caminhos baseados no repositório GitHub
- Cria automaticamente os diretórios necessários
- Fornece funções utilitárias para acessar caminhos

### 2. Estrutura de Diretórios no GitHub
```
quant_invest/
├── data/                    # Bases de dados (salvas aqui)
├── results/                 # Resultados e relatórios
│   ├── pdfs/               # PDFs de backtest
│   ├── images/             # Gráficos e imagens
│   ├── carteiras/          # Arquivos de carteiras
│   └── indicadores/        # Resultados de indicadores
├── logs/                   # Logs do sistema
│   └── crypto/             # Logs específicos de crypto
├── factor_investing/       # Módulos de factor investing
├── trading/                # Módulos de trading
└── config.py              # Configurações centralizadas
```

### 3. Arquivos Modificados

#### `app.py`
- ✅ Importa configurações do `config.py`
- ✅ Usa `get_carteira_path()` para arquivos de carteira
- ✅ Remove caminhos hardcoded do Windows

#### `data/load_data_fintz_v2.py`
- ✅ Importa configurações do `config.py`
- ✅ Usa `DATA_DIR` como diretório padrão
- ✅ Salva dados na pasta `data/` do GitHub

#### `factor_investing/calculadora_factor.py`
- ✅ Importa configurações do `config.py`
- ✅ Usa caminhos padrão do GitHub
- ✅ Salva resultados em `results/indicadores/`
- ✅ Salva carteiras em `results/carteiras/`

#### `factor_investing/factor_todos_dias.py`
- ✅ Importa configurações do `config.py`
- ✅ Usa caminhos padrão do GitHub
- ✅ Remove referências a caminhos do Windows

#### `trading/stocks/estrategia.py`
- ✅ Importa configurações do `config.py`
- ✅ Usa `DATA_DIR` para benchmarks

### 4. Benefícios da Migração

1. **Portabilidade**: O código funciona em qualquer sistema operacional
2. **Organização**: Estrutura padronizada de diretórios
3. **GitHub Integration**: Dados salvos diretamente no repositório
4. **Facilidade de Deploy**: Caminhos relativos facilitam deploy
5. **Colaboração**: Outros desenvolvedores podem usar sem modificar caminhos

### 5. Como Usar

#### Para desenvolvedores:
```python
from config import get_data_path, get_results_path, get_carteira_path

# Carregar dados
dados = pd.read_parquet(get_data_path("cotacoes.parquet"))

# Salvar resultados
resultado.to_csv(get_results_path("indicadores", "meu_resultado.csv"))

# Trabalhar com carteiras
carteira.to_csv(get_carteira_path("carteira_atual.csv"))
```

#### Para executar scripts:
Os scripts agora usam automaticamente os caminhos do GitHub. Não é necessário modificar caminhos hardcoded.

### 6. Próximos Passos

Para completar a migração, ainda precisamos atualizar:
- [ ] Mais arquivos do módulo `trading/`
- [ ] Arquivos do módulo `factor_investing/` restantes
- [ ] Scripts de crypto trading
- [ ] Atualizar requirements.txt se necessário

### 7. Compatibilidade

O sistema mantém compatibilidade com caminhos antigos através do mapeamento em `config.py`, mas recomenda-se usar as novas funções utilitárias.
