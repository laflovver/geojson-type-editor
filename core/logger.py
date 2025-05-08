import logging
from pathlib import Path

def setup_logger():
    """Set up the application logger."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'app.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)
