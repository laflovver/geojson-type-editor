import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings
from core.application import Application
from core.logger import setup_logger
from core.config import Config

logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize application
        app = Application(sys.argv)
        app.setFont(QFont('Roboto Mono', 14))
        
        # Load configuration
        config = Config()
        
        # Apply global style sheet
        script_dir = os.path.dirname(os.path.realpath(__file__))
        qss_path = os.path.join(script_dir, "qt_style.qss")
        try:
            with open(qss_path, 'r') as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            logger.warning(f"Failed to load stylesheet: {e}")
        
        # Initialize main window
        editor = app.create_main_window()
        editor.show()
        
        # Start application
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    setup_logger()
    main()