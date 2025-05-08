# config/settings.py
# Define as configurações globais do projeto, como anos de temporada.
# Também pode incluir diretórios, nomes padrão de arquivos, etc.

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Token de autenticação da API (lido do .env)
API_TOKEN = os.getenv("API_TOKEN")

# URL base da versão 4 da API
BASE_URL = "https://api.football-data.org/v4"

# Temporadas desejadas
SEASON_YEARS = [2020, 2021, 2022, 2023, 2024]

# Pasta de saída para os arquivos CSV
OUTPUT_DIR = "data"
