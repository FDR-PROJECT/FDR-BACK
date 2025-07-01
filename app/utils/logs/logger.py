from loguru import logger
import os

LOG_DIR = "logs"

# Garantir que o diretório para logs exista
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configuração do Loguru
logger.add(
    os.path.join(LOG_DIR, "console.log"),  # Nome do arquivo de log
    rotation="1 day",  # Rotação diária
    retention="30 days",  # Manter arquivos por 30 dias
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} - ROUTE: {extra[route]} - USER: {extra[user]} - {message}",
    level="INFO",
)
