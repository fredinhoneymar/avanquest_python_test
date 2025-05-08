from services.api_client import get_matches
from utils.data_processing import process_matches, save_to_csv
from config.settings import SEASON_YEARS
from config.logging_config import setup_logger

# Inicializando o logger
logger = setup_logger(__name__)

def run_pipeline_for_year(year, logger):
    """Executa o pipeline de dados para uma temporada específica"""
    logger.info(f"... Iniciando pipeline para a temporada {year}")
    
    # Obtém os jogos para o ano
    matches = get_matches(year, logger)
    
    if matches:
        # Processa os jogos e salva os dados em CSV
        stats = process_matches(matches, logger)
        save_to_csv(stats, year, logger)
        logger.info(f" Pipeline concluída para {year}")
    else:
        logger.warning(f"⚠ Nenhum jogo encontrado para o ano {year}")

def main():
    """Função principal para rodar o pipeline de várias temporadas"""
    for year in SEASON_YEARS:
        run_pipeline_for_year(year, logger)  # Passando logger corretamente para o pipeline

if __name__ == "__main__":
    main()
