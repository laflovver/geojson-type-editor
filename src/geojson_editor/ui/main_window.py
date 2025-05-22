"""Main window for the GeoJSON Editor application."""

from typing import Dict, Any

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from ..core.styles import load_stylesheet


class MainWindow(QMainWindow):
    """Main window for the GeoJSON Editor application."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the main window.
        
        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config
        self.setup_ui()
        self.load_styles()

    def setup_ui(self) -> None:
        """Set up the user interface.
        
        This method initializes the main window layout and widgets.
        """
        self.setWindowTitle(f"{self.config['app_name']} v{self.config['version']}")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # TODO: Add UI components here

    def load_styles(self) -> None:
        """Load and apply the application stylesheet.
        
        This method loads the stylesheet and applies it to the main window.
        If loading fails, the default Qt styles will be used.
        """
        stylesheet = load_stylesheet(self.config)
        if stylesheet:
            self.setStyleSheet(stylesheet)
