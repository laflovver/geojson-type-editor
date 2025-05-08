from PyQt5.QtWidgets import QApplication
from ui.main_window import GeoJSONEditor
from core.logger import logger

class Application(QApplication):
    """Main application class that manages the application lifecycle."""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.logger = logger
        
    def create_main_window(self) -> GeoJSONEditor:
        """Create and return the main window instance."""
        try:
            return GeoJSONEditor()
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}", exc_info=True)
            raise
