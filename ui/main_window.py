from typing import Optional, List, Dict
import os
from PyQt5.QtWidgets import (
    QAction,
    QLineEdit,
    QFormLayout,
    QSizePolicy,
    QFileDialog,
    QMainWindow,
    QWidget,
    QStyle,
    QMessageBox,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.ui_main_window import Ui_MainWindow
from core.config import Config
from logic.geojson_manager import GeoJSONManager
from ui.mts_dialog import MTSIntegrationDialog
from logic.json_utils import populate_table_from_features
from core.logger import logger

class GeoJSONEditor(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.config = Config()
        self._setup_connections()
        self._initialize_manager()
        self._setup_logging()
        
    def _setup_connections(self) -> None:
        """Set up all widget connections."""
        self.ui.load_btn.clicked.connect(self.handle_load_geojson)
        self._setup_toggle_button()
        self._setup_mts_button()
        
    def _setup_toggle_button(self) -> None:
        """Set up the toggle table button connection."""
        if hasattr(self.ui, 'toggle_btn'):
            self.ui.toggle_btn.clicked.connect(self.handle_toggle_table)
        elif hasattr(self.ui, 'toggleButton'):
            self.ui.toggleButton.clicked.connect(self.handle_toggle_table)
        
    def _setup_mts_button(self) -> None:
        """Set up the MTS integration button connection."""
        try:
            if hasattr(self.ui, 'mts_btn'):
                self.ui.mts_btn.clicked.connect(self.open_mts_dialog)
        except AttributeError:
            logger.warning("MTS button not found in UI")
            
    def _initialize_manager(self) -> None:
        """Initialize the GeoJSON manager with configuration settings."""
        try:
            self.manager = GeoJSONManager(
                cli_path=self.config.mts_cli_path,
                access_token=self.config.mts_access_token,
                username=self.config.mts_username,
                logger=self.append_log
            )
            logger.info("GeoJSON manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GeoJSON manager: {e}", exc_info=True)
            raise
            
    def _setup_logging(self) -> None:
        """Set up initial logging."""
        cli = self.config.mts_cli_path
        user = self.config.mts_username
        self.append_log(f"MTS configured with CLI='{cli}', username='{user}'", "info")

    def append_log(self, message: str, level: str = "info") -> None:
        """
        Append a message to the UI log console.
        
        Args:
            message: The message to log
            level: The log level (info, success, error)
        """
        try:
            color = {"info": "#4F5D75", "success": "#4CAF50", "error": "#FF5C61"}.get(level, "#4F5D75")
            formatted = f'<span style="color:{color};">{message}</span>'
            
            # Find the log widget
            if hasattr(self.ui, 'log') and hasattr(self.ui.log, 'append'):
                self.ui.log.append(formatted)
                cursor = self.ui.log.textCursor()
                cursor.movePosition(cursor.End)
                self.ui.log.setTextCursor(cursor)
            elif hasattr(self.ui, 'logTextEdit') and hasattr(self.ui.logTextEdit, 'append'):
                self.ui.logTextEdit.append(formatted)
                cursor = self.ui.logTextEdit.textCursor()
                cursor.movePosition(cursor.End)
                self.ui.logTextEdit.setTextCursor(cursor)
            else:
                logger.warning("Log widget not found in UI")
                print(message)
        except Exception as e:
            logger.error(f"Failed to append log message: {e}", exc_info=True)
            print(message)

    def handle_load_geojson(self):
        """Load a GeoJSON file and populate the table."""
        self.append_log("handle_load_geojson invoked", "info")
        path, _ = QFileDialog.getOpenFileName(self, "Open GeoJSON", "", "GeoJSON Files (*.geojson *.json)")
        self.append_log(f"Selected file: {path}", "info")
        if not path:
            return
        # Load data via manager
        self.manager.load(path)
        self.append_log("manager.load completed", "info")
        features, keys = self.manager.get_features_and_keys()
        self.append_log(f"Loaded {len(features)} features; keys: {keys}", "info")
        try:
            populate_table_from_features(self.table, features, keys)
            self.table.setVisible(True)
        except Exception as e:
            self.append_log(f"Error populating table: {e}", "error")
        # Log success
        self.append_log(f"Loaded GeoJSON: {path}", "success")

    def handle_toggle_table(self):
        """
        Toggle visibility of the data table and log the change.
        """
        # Determine which attribute holds the table widget
        table_attr = 'table' if hasattr(self, 'table') else 'tableWidget' if hasattr(self, 'tableWidget') else None
        if not table_attr:
            self.append_log("Toggle failed: no table widget found", "error")
            return
        tbl = getattr(self, table_attr)
        visible = tbl.isVisible()
        tbl.setVisible(not visible)
        state = "shown" if not visible else "hidden"
        self.append_log(f"Table {state}", "info")

    def open_mts_dialog(self):
        dlg = MTSIntegrationDialog(self.manager, parent=self)
        dlg.exec_()