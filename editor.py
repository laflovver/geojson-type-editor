from mts_manager import MTSManager
import os
from PySide6.QtWidgets import (
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
    QHeaderView,
    QTextEdit
)
from PySide6.QtCore import QSettings, Qt, QStandardPaths
from PySide6.QtGui import QIcon, QAction, QTextCursor
from logic import GeoJSONManager
from validators import EnglishTextValidator
import json

class GeoJSONEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoJSON Type Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.settings = QSettings("GeoJSONTypeEditor", "Settings")
        self.manager = GeoJSONManager()
        self.current_file = None
        self.load_settings()
        
        # === UI SETUP ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Load Button
        self.load_btn = QPushButton("Load GeoJSON")
        button_layout.addWidget(self.load_btn)
        
        # Toggle Table Button
        self.toggle_btn = QPushButton("Toggle Table")
        button_layout.addWidget(self.toggle_btn)
        
        # MTS Button
        self.mts_btn = QPushButton("MTS Integration")
        button_layout.addWidget(self.mts_btn)
        
        # Add stretch to push buttons to the left
        button_layout.addStretch()
        
        layout.addLayout(button_layout)

        # Table Widget with stretch
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.table, 1)  # Add stretch factor of 1

        # Log area with fixed height
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(100)
        self.log.setMaximumHeight(200)
        log_layout.addWidget(self.log)
        layout.addWidget(log_group)
        
        # Set up English text validator
        self.english_validator = EnglishTextValidator()
        
        # Apply validator to all input fields
        for widget in self.findChildren(QLineEdit):
            widget.setValidator(self.english_validator)
        
        # Connect Load GeoJSON button
        self.load_btn.clicked.connect(self.on_load_geojson)
        # Hide table until a file is loaded
        self.table.setVisible(False)
        # Connect Toggle Table button
        # Replace 'toggle_btn' with the actual object name from your UI if different
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.clicked.connect(self.handle_toggle_table)
        elif hasattr(self, 'toggleButton'):
            self.toggleButton.clicked.connect(self.handle_toggle_table)

        # Initialize MTS manager
        self.mts_manager = MTSManager(logger=self.append_log)
        # Debug: show loaded MTS settings
        settings = self.mts_manager.get_settings()
        cli = settings['cli_path']
        user = settings['username']
        self.append_log(f"MTS configured with CLI='{cli}', username='{user}'", "info")
        # Connect MTS Integration button
        try:
            self.mts_btn.clicked.connect(self.on_mts_integration)
        except AttributeError as e:
            self.append_log(f"Error connecting MTS button: {e}", "error")

    def load_settings(self):
        """Load and apply saved window settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

    def append_log(self, message, level="info"):
        """
        Append a message to the UI log console.
        """
        # Choose color based on level
        color = {"info": "#4F5D75", "success": "#4CAF50", "error": "#FF5C61"}.get(level, "#4F5D75")
        formatted = f'<span style="color:{color};">{message}</span>'
        # Append to QTextEdit named self.log only
        if hasattr(self, 'log') and isinstance(self.log, QTextEdit):
            self.log.append(formatted)
            cursor = self.log.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log.setTextCursor(cursor)
        else:
            print(message)

    def on_load_geojson(self):
        """Handle Load GeoJSON action"""
        # Get the Downloads folder path
        downloads_path = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0]
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open GeoJSON File",
            downloads_path,
            "GeoJSON Files (*.geojson);;All Files (*)"
        )
        self.append_log(f"Selected file: {file_path}", "info")
        if not file_path:
            return
            
        try:
            # Clear previous data
            self.table.clear()
            self.table.setColumnCount(0)
            self.table.setRowCount(0)
            
            # Load data via manager
            self.manager.load(file_path)
            self.append_log("Processing GeoJSON data...", "info")
            
            # Get features and keys
            features, keys = self.manager.get_features_and_keys()
            self.append_log(f"Loaded {len(features)} features with {len(keys)} properties", "info")
            
            if not features or not keys:
                self.append_log("No features or properties found in the GeoJSON file", "error")
                return
                
            # Set up table
            self.table.setColumnCount(len(keys))
            self.table.setRowCount(len(features))
            self.table.setHorizontalHeaderLabels(keys)
            
            # Enable sorting before populating data
            self.table.setSortingEnabled(False)
            
            # Populate table
            for i, feat in enumerate(features):
                for j, key in enumerate(keys):
                    val = feat.get('properties', {}).get(key, '')
                    item = QTableWidgetItem(str(val) if val is not None else '')
                    self.table.setItem(i, j, item)
            
            # Resize columns to content
            self.table.resizeColumnsToContents()
            
            # Enable sorting after populating data
            self.table.setSortingEnabled(True)
            
            # Show the table
            self.table.setVisible(True)
            self.toggle_btn.setEnabled(True)
            
            # Log success
            self.append_log(f"Successfully loaded GeoJSON: {os.path.basename(file_path)}", "success")
            
        except Exception as e:
            import traceback
            error_msg = f"Error loading GeoJSON: {str(e)}\n{traceback.format_exc()}"
            self.append_log(error_msg, "error")
            QMessageBox.critical(self, "Error", f"Failed to load GeoJSON file:\n{str(e)}")

    def populate_table(self, features, keys):
        """Helper to (re)populate the table from features and keys."""
        self.table.clear()
        self.table.setColumnCount(len(keys))
        self.table.setRowCount(len(features))
        self.table.setHorizontalHeaderLabels(keys)
        for i, feat in enumerate(features):
            for j, key in enumerate(keys):
                val = feat.get('properties', {}).get(key, '')
                item = QTableWidgetItem(str(val))
                self.table.setItem(i, j, item)
        self.table.setVisible(True)

    def handle_toggle_table(self):
        """
        Toggle visibility of the data table and log the change.
        """
        if not hasattr(self, 'table'):
            self.append_log("Toggle failed: table widget not found", "error")
            return
            
        # Toggle visibility
        is_visible = self.table.isVisible()
        self.table.setVisible(not is_visible)
        
        # Update button text
        self.toggle_btn.setText("Show Table" if is_visible else "Hide Table")
        
        # Log the action
        state = "hidden" if is_visible else "shown"
        self.append_log(f"Table {state}", "info")

    def update_recipe_table(self, username, source_name, layer_name, recipe_table):
        """Update the recipe table and JSON file with new values."""
        try:
            if recipe_table and recipe_table.rowCount() > 0:
                source_item = recipe_table.item(0, 0)
                if source_item and username:
                    # Always use the username, create default source if needed
                    source_parts = source_item.text().split('/')
                    if len(source_parts) >= 3:
                        source_parts[2] = username  # Update only the username part
                    else:
                        source_parts = ["mapbox:", "tileset-source", username, "layer_name-source"]
                    source = '/'.join(source_parts)
                    source_item.setText(source)
                    
                    # Update the JSON immediately
                    recipe_path = 'recipe.json'
                    recipe = {
                        "version": 1,
                        "layers": {
                            layer_name: {
                                "source": source,
                                "minzoom": 0,
                                "maxzoom": 14
                            }
                        }
                    }
                    
                    with open(recipe_path, 'w') as f:
                        json.dump(recipe, f, ensure_ascii=False, indent=2)
                    
                    self.append_log("Updated recipe JSON with current username", "info")
                
                layer_name_item = recipe_table.item(0, 3)
                if layer_name_item and layer_name:
                    layer_name_item.setText(layer_name)
        except Exception as e:
            self.append_log(f"Error updating recipe: {e}", "error")

    def on_mts_integration(self):
        from mts_dialog import MTSDialog
        dialog = MTSDialog(self, logger=self.append_log)
        dialog.update_recipe_table()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings when dialog is accepted
            settings = {
                'cli_path': dialog.mts_widgets['cli'].text(),
                'access_token': dialog.mts_widgets['token'].text(),
                'username': dialog.mts_widgets['username'].text(),
                'source_name': dialog.mts_widgets['source_name'].text(),
                'layer_name': dialog.mts_widgets['layer_name'].text()
            }
            self.mts_manager.save_settings(settings)

    def closeEvent(self, event):
        """Save window settings on close."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)