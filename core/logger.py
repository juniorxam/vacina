"""
logger.py - Configuração centralizada de logging
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from config import CONFIG


def setup_logging():
    """Configura o sistema de logging da aplicação"""
    
    # Detectar ambiente
    is_cloud = CONFIG.is_streamlit_cloud or os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'
    
    # Formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)
    
    # Handler para console (sempre presente)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    
    # Em produção/cloud, usar apenas console
    if is_cloud or CONFIG.environment == "production":
        root_logger.setLevel(logging.INFO)
        # Remover handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.addHandler(console_handler)
        logging.info("Logging configurado para modo cloud (apenas console)")
        return root_logger
    
    # Em desenvolvimento, adicionar arquivo
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"nasst_{datetime.now().strftime('%Y%m')}.log"
    
    # Handler para arquivo (com rotação)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        date_format
    ))
    
    # Configurar nível baseado no debug
    if CONFIG.debug:
        root_logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
    
    # Remover handlers existentes e adicionar os novos
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Silenciar logs muito verbosos
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pdfplumber").setLevel(logging.WARNING)
    
    logging.info(f"Logging configurado para modo desenvolvimento. Arquivo: {log_file}")
    
    return root_logger


def get_logger(name):
    """Obtém um logger configurado"""
    return logging.getLogger(name)
