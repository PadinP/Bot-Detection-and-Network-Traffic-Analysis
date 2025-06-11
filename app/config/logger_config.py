import os
import logging
from app.config.settings import LOG_PATH

def setup_logger(logger_name: str, log_dir: str, log_filename: str, level=logging.INFO) -> logging.Logger:
    """
    Configura y retorna un logger con el nombre, directorio y nombre de archivo especificados.
    """
    # Se asegura que el directorio exista
    os.makedirs(log_dir, exist_ok=True)
    
    # Se obtiene el logger, y se establece el nivel
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Para evitar agregar múltiples handlers
    if not logger.handlers:
        log_file = os.path.join(log_dir, log_filename)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Configuración de los loggers específicos:
capture_logger = setup_logger("capture_logger", LOG_PATH, "capture_bto_logs.log")
detection_logger = setup_logger("detection_logger", LOG_PATH, "detection_bto_logs.log")
