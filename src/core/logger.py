import logging
import os
from pathlib import Path

def setup_logger():
    """Configure the application logger."""
    log_dir = Path.home() / ".geojson_editor" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "app.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Create a logger for the application
    logger = logging.getLogger(__name__)
    logger.info("Logger initialized")
    return logger
