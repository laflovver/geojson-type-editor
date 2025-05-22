"""
Main entry point for the GeoJSON Editor application.
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from .core.config import load_config, setup_environment
from .core.styles import set_default_font
from .ui.main_window import MainWindow


def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    # Skip keyboard interrupt to allow normal exit
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Format the error message
    error_msg = """
    An unhandled exception occurred:
    
    Type: {}
    Message: {}
    
    {}
    """.format(
        exc_type.__name__,
        str(exc_value),
        ''.join(traceback.format_tb(exc_traceback))
    )
    
    # Show error message
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText("An error occurred")
    msg_box.setDetailedText(error_msg)
    msg_box.exec()


def main() -> int:
    """Run the application.
    
    Returns:
        int: Exit code
    """
    # Set up exception handling
    sys.excepthook = handle_exception
    
    try:
        # Set up the application
        app = QApplication(sys.argv)
        
        # Load configuration and set up environment
        config = load_config()
        setup_environment(config)
        
        # Set default font
        set_default_font(config)
        
        # Create and show the main window
        window = MainWindow(config)
        window.show()
        
        # Start the event loop
        return app.exec()
    except Exception as e:
        # This will be caught by the excepthook
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
