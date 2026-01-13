"""Logging-Funktionalität"""

import logging
from datetime import datetime
from pathlib import Path
from src.config.settings import Settings


def setup_logger(name: str = "research_tool") -> logging.Logger:
    """
    Initialisiert Logger mit File- und Console-Handler
    
    Args:
        name: Name des Loggers
        
    Returns:
        Konfigurierter Logger
    """
    # Logs-Verzeichnis erstellen
    Settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Timestamp für Log-Dateiname
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Settings.LOGS_DIR / f"research_{timestamp}.log"
    
    # Logger konfigurieren
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialisiert - Log-Datei: {log_file}")
    
    return logger
