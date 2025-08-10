"""
Configurações centralizadas para o sistema quant_invest
Define todos os caminhos baseados no repositório GitHub
"""
import os
from pathlib import Path

# URLs base do repositório GitHub
GITHUB_REPO_URL = "https://github.com/Rafaeldag/quant_invest"
GITHUB_DATA_URL = "https://github.com/Rafaeldag/quant_invest/tree/main/data"

# Caminhos base do projeto
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
MARKET_DATA_DIR = DATA_DIR / "market_data"
FACTOR_DATA_DIR = DATA_DIR / "factors_data"
FACTOR_INVESTING_DIR = PROJECT_ROOT / "factor_investing"
TRADING_DIR = PROJECT_ROOT / "trading"

# Caminhos para dados
BASE_DADOS_PATH = DATA_DIR
# Dados de mercado (CDI, IBOV, cotações)
COTACOES_PATH = MARKET_DATA_DIR / "cotacoes.parquet"
CDI_PATH = MARKET_DATA_DIR / "cdi.parquet" 
IBOV_PATH = MARKET_DATA_DIR / "ibov.parquet"

# Dados de fatores e indicadores contábeis
EBIT_PATH = FACTOR_DATA_DIR / "EBIT.parquet"
VALOR_MERCADO_PATH = FACTOR_DATA_DIR / "ValorDeMercado.parquet"
DIVIDA_BRUTA_PATH = FACTOR_DATA_DIR / "DividaBruta.parquet"
DIVIDA_LIQUIDA_PATH = FACTOR_DATA_DIR / "DividaLiquida.parquet"
LUCRO_LIQUIDO_PATH = FACTOR_DATA_DIR / "LucroLiquido.parquet"
PATRIMONIO_LIQUIDO_PATH = FACTOR_DATA_DIR / "PatrimonioLiquido.parquet"
RECEITA_LIQUIDA_PATH = FACTOR_DATA_DIR / "ReceitaLiquida.parquet"
EBIT_EV_PATH = FACTOR_DATA_DIR / "EBIT_EV.parquet"
L_P_PATH = FACTOR_DATA_DIR / "L_P.parquet"
ROE_PATH = FACTOR_DATA_DIR / "ROE.parquet"
ROIC_PATH = FACTOR_DATA_DIR / "ROIC.parquet"
LIQUIDEZ_CORRENTE_PATH = FACTOR_DATA_DIR / "LiquidezCorrente.parquet"
MARGEM_EBITDA_PATH = FACTOR_DATA_DIR / "MargemEBITDA.parquet"
MARGEM_LIQUIDA_PATH = FACTOR_DATA_DIR / "MargemLiquida.parquet"

# Caminhos para resultados e relatórios
RESULTS_DIR = PROJECT_ROOT / "results"
PDFS_DIR = RESULTS_DIR / "pdfs"
IMAGES_DIR = RESULTS_DIR / "images"
CARTEIRAS_DIR = RESULTS_DIR / "carteiras"

# Caminhos para resultados e relatórios Factor Investing
RESULTS_DIR_FACTOR = RESULTS_DIR / "factor_investing"
PDFS_DIR_FACTOR = RESULTS_DIR_FACTOR / "pdfs"
IMAGES_DIR_FACTOR = RESULTS_DIR_FACTOR / "images"
CARTEIRAS_DIR_FACTOR = RESULTS_DIR_FACTOR / "carteiras"

# Caminhos para resultados e relatórios Trading
RESULTS_DIR_TRADING = RESULTS_DIR / "trading"
PDFS_DIR_TRADING = RESULTS_DIR_TRADING / "pdfs"
IMAGES_DIR_TRADING = RESULTS_DIR_TRADING / "images"
CARTEIRAS_DIR_TRADING = RESULTS_DIR_TRADING / "carteiras"

# Caminhos para logs (trading)
LOGS_DIR = PROJECT_ROOT / "logs"
CRYPTO_LOGS_DIR = LOGS_DIR / "crypto"

# Caminhos para prêmios de risco
PREMIOS_RISCO_DIR = DATA_DIR / "premios_risco"

# Garante que os diretórios existam
def create_directories():
    """Cria todos os diretórios necessários se não existirem"""
    directories = [
        DATA_DIR,
        MARKET_DATA_DIR,
        FACTOR_DATA_DIR,
        RESULTS_DIR,
        PDFS_DIR,
        IMAGES_DIR,
        CARTEIRAS_DIR,
        LOGS_DIR,
        CRYPTO_LOGS_DIR,
        PREMIOS_RISCO_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Executa a criação de diretórios ao importar
create_directories()

# Configurações antigas (para compatibilidade durante migração)
OLD_PATHS = {
    'base_dados_br': r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_br',
    'projetos_pessoais': r'C:\Users\rafae\OneDrive\Documentos\Projetos Pessoais',
    'pdfs_backtest': r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\PDFS_BACKTEST',
    'base_dados_cripto': r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\base_dados_cripto',
    'robo_cripto_logs': r'C:\Users\rafae\OneDrive\Documentos\Bolsa de Valores\Modelos_Quantitativos\Analise_Tecnica\Robo_Cripto\logs'
}

# Mapeamento de caminhos antigos para novos
PATH_MAPPING = {
    OLD_PATHS['base_dados_br']: str(BASE_DADOS_PATH),
    OLD_PATHS['projetos_pessoais']: str(CARTEIRAS_DIR),
    OLD_PATHS['pdfs_backtest']: str(PDFS_DIR),
    OLD_PATHS['base_dados_cripto']: str(DATA_DIR),
    OLD_PATHS['robo_cripto_logs']: str(CRYPTO_LOGS_DIR)
}

def get_data_path(filename=""):
    """Retorna o caminho completo para um arquivo na pasta data"""
    if filename:
        return DATA_DIR / filename
    return DATA_DIR

def get_results_path(strategy="", subfolder="", filename=""):
    """Retorna o caminho completo para arquivos de resultados"""
    if strategy:
        path = RESULTS_DIR / strategy
        path.mkdir(parents=True, exist_ok=True)
        if subfolder:
            path = path / subfolder
            path.mkdir(parents=True, exist_ok=True)
            if filename:
                return path / filename
            return path
        elif filename:
            return path / filename
        return path
    elif subfolder:
        path = RESULTS_DIR / subfolder
        path.mkdir(parents=True, exist_ok=True)
        if filename:    
            return path / filename
        return path
    elif filename:
        return RESULTS_DIR / filename
    return RESULTS_DIR

def get_carteira_path(filename=""):
    """Retorna o caminho para arquivos de carteira"""
    if filename:
        return CARTEIRAS_DIR / filename
    return CARTEIRAS_DIR

def get_market_data_path(filename=""):
    """Retorna o caminho para dados de mercado (CDI, IBOV, cotações)"""
    if filename:
        return MARKET_DATA_DIR / filename
    return MARKET_DATA_DIR

def get_factor_data_path(filename=""):
    """Retorna o caminho para dados de fatores e indicadores contábeis"""
    if filename:
        return FACTOR_DATA_DIR / filename
    return FACTOR_DATA_DIR

print(f"✅ Configuração carregada - Projeto: {PROJECT_ROOT}")
print(f"📁 Diretório de dados: {DATA_DIR}")
print(f"📈 Diretório de dados de mercado: {MARKET_DATA_DIR}")
print(f"📊 Diretório de dados de fatores: {FACTOR_DATA_DIR}")
print(f"📊 Diretório de resultados: {RESULTS_DIR}")
