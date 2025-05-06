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
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon
from ui import Ui_MainWindow
from logic import GeoJSONManager

class GeoJSONEditor(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Connect Load GeoJSON button
        self.load_btn.clicked.connect(self.handle_load_geojson)
        # Hide table until a file is loaded
        self.table.setVisible(False)
        # Connect Toggle Table button
        # Replace 'toggle_btn' with the actual object name from your UI if different
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.clicked.connect(self.handle_toggle_table)
        elif hasattr(self, 'toggleButton'):
            self.toggleButton.clicked.connect(self.handle_toggle_table)
        # Load MTS settings
        settings = QSettings("GeoJSONEditor", "MapboxMTS")
        # Initialize manager with saved settings
        self.manager = GeoJSONManager(
            cli_path=settings.value("mts/cli_path", ""),
            access_token=settings.value("mts/access_token", ""),
            username=settings.value("mts/username", ""),
            logger=self.append_log
        )
        # Debug: show loaded MTS settings
        cli = settings.value("mts/cli_path", "")
        user = settings.value("mts/username", "")
        self.append_log(f"MTS configured with CLI='{cli}', username='{user}'", "info")
        # Connect MTS Integration button
        try:
            self.mts_btn.clicked.connect(self.handle_mts_integration)
        except AttributeError:
            pass

    def append_log(self, message, level="info"):
        """
        Append a message to the UI log console.
        """
        # Choose color based on level
        color = {"info": "#4F5D75", "success": "#4CAF50", "error": "#FF5C61"}.get(level, "#4F5D75")
        formatted = f'<span style="color:{color};">{message}</span>'
        # Append to QTextEdit named self.log or self.logTextEdit
        if hasattr(self, 'log') and hasattr(self.log, 'append'):
            self.log.append(formatted)
            cursor = self.log.textCursor()
            cursor.movePosition(cursor.End)
            self.log.setTextCursor(cursor)
        elif hasattr(self, 'logTextEdit') and hasattr(self.logTextEdit, 'append'):
            self.logTextEdit.append(formatted)
            cursor = self.logTextEdit.textCursor()
            cursor.movePosition(cursor.End)
            self.logTextEdit.setTextCursor(cursor)
        else:
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
        except Exception as e:
            self.append_log(f"Error populating table: {e}", "error")
        # Log success
        self.append_log(f"Loaded GeoJSON: {path}", "success")

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

    def on_mts_integration(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("MTS Integration")
        dlg.setMinimumSize(800, 700)

        settings = QSettings("GeoJSONEditor", "MapboxMTS")
        layout = QVBoxLayout(dlg)

        # Settings form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft)
        # Make input fields expand to fill the dialog width
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Tilesets CLI Path with embedded browse icon
        cliEdit = QLineEdit(settings.value("mts/cli_path", ""))
        cliEdit.setPlaceholderText("Tilesets CLI Path")
        cliEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cliEdit.setStyleSheet("border: 1px solid #ccc;")
        def browse_cli():
            directory = QFileDialog.getExistingDirectory(self, "Select Tilesets CLI Directory")
            if directory:
                cliEdit.setText(directory)
        # Embed browse action inside the QLineEdit
        cliIcon = QIcon.fromTheme("folder-open") or QIcon("browse_icon.png")
        cliAction = QAction(cliIcon, "", cliEdit)
        cliAction.setToolTip("Browse for Tilesets CLI directory")
        cliEdit.addAction(cliAction, QLineEdit.TrailingPosition)
        cliAction.triggered.connect(browse_cli)
        form.addRow("Tilesets CLI :", cliEdit)

        tokenEdit = QLineEdit(settings.value("mts/access_token", ""))
        tokenEdit.setPlaceholderText("Access Token")
        tokenEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form.addRow("Mapbox Access Token :", tokenEdit)

        userEdit = QLineEdit(settings.value("mts/username", ""))
        userEdit.setPlaceholderText("Username")
        userEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form.addRow("Mapbox Username :", userEdit)

        layout.addLayout(form)

        # Recipe block
        recipeGroup = QGroupBox("Recipe")
        recipeLayout = QVBoxLayout(recipeGroup)
        recipeTable = QTableWidget(1, 6)
        recipeTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        recipeTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        recipeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        recipeTable.setHorizontalHeaderLabels(["source", "minzoom", "maxzoom", "layer_name", "fillzoom", "incremental"])
        defaults = [
            f"mapbox://tileset-source/{userEdit.text()}/layer_name-source",
            "0", "14", "layer_name", "", "false"
        ]
        for col, val in enumerate(defaults):
            recipeTable.setItem(0, col, QTableWidgetItem(val))
        recipeLayout.addWidget(recipeTable)

        btns = QHBoxLayout()
        saveRecBtn = QPushButton("Save Recipe")
        openRecBtn = QPushButton("Open Recipe")
        btns.addWidget(saveRecBtn)
        btns.addWidget(openRecBtn)
        recipeLayout.addLayout(btns)
        layout.addWidget(recipeGroup)

        # Fields below Recipe
        postForm = QFormLayout()
        postForm.setLabelAlignment(Qt.AlignLeft)
        postForm.setFormAlignment(Qt.AlignLeft)
        sourceEdit = QLineEdit(settings.value("mts/source_name", ""))
        sourceEdit.setPlaceholderText("Source Name")
        sourceEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        postForm.addRow("Source Name :", sourceEdit)
        idEdit = QLineEdit()
        idEdit.setPlaceholderText("32 characters or less")
        idEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        postForm.addRow("Identifier :", idEdit)
        nameEdit = QLineEdit()
        nameEdit.setPlaceholderText("64 characters or less")
        nameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        postForm.addRow("Tileset Name :", nameEdit)
        layout.addLayout(postForm)

        # Deploy and Publish buttons
        btnsDeploy = QHBoxLayout()
        deployBtn = QPushButton("Deploy Tileset")
        publishBtn = QPushButton("Publish")
        btnsDeploy.addWidget(deployBtn)
        btnsDeploy.addWidget(publishBtn)
        layout.addLayout(btnsDeploy)

        # Settings and actions
        def save_settings():
            settings.setValue("mts/cli_path", cliEdit.text())
            settings.setValue("mts/access_token", tokenEdit.text())
            settings.setValue("mts/username", userEdit.text())
            settings.setValue("mts/source_name", sourceEdit.text())
            self.manager.configure_mts(cliEdit.text(), tokenEdit.text(), userEdit.text(), logger=self.append_log)

        def on_save_recipe():
            save_settings()
            import json
            path, _ = QFileDialog.getSaveFileName(self, "Save Recipe", "recipe.json", "JSON Files (*.json)")
            if not path:
                return
            layers = {}
            for i in range(recipeTable.rowCount()):
                source = recipeTable.item(i, 0).text()
                minzoom = int(recipeTable.item(i, 1).text())
                maxzoom = int(recipeTable.item(i, 2).text())
                layer_name = recipeTable.item(i, 3).text()
                fillzoom_item = recipeTable.item(i, 4)
                spec = {"source": source, "minzoom": minzoom, "maxzoom": maxzoom}
                if fillzoom_item and fillzoom_item.text().strip():
                    spec["fillzoom"] = int(fillzoom_item.text())
                inc = False
                if recipeTable.item(i, 5) and recipeTable.item(i, 5).text().strip().lower() == "true":
                    inc = True
                spec["incremental"] = inc
                layers[layer_name] = spec
            recipe_spec = {"version": 1, "layers": layers}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(recipe_spec, f, ensure_ascii=False, indent=2)
            self.log_message(f"Recipe saved to {path}", "success")

        def on_deploy_tileset():
            save_settings()
            tileset_name = sourceEdit.text().strip()
            if not tileset_name:
                self.log_message("Tileset source name is required", "error")
                return
            try:
                upload_result = self.manager.upload_source(tileset_name)
                self.log_message(f"Upload Source result: {upload_result}", "success")
            except Exception as e:
                self.log_message(f"Upload source failed: {e}", "error")
                return
            try:
                create_result = self.manager.create_tileset(
                    idEdit.text(), getattr(self, 'currentRecipePath', ''), nameEdit.text()
                )
                self.log_message(f"Create Tileset result: {create_result}", "success")
            except Exception as e:
                self.log_message(f"Create tileset failed: {e}", "error")
                return

        saveRecBtn.clicked.connect(on_save_recipe)
        openRecBtn.clicked.connect(self.on_open_recipe)
        deployBtn.clicked.connect(on_deploy_tileset)
        publishBtn.clicked.connect(lambda: self.manager.publish_tileset(
            idEdit.text(), status_callback=self.log_message
        ))

        dlg.exec_()