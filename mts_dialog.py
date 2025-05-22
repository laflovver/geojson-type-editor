from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QTextEdit,
    QSizePolicy,
    QFileDialog,
    QAction
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import json
import os
from mts_manager import MTSManager

class MTSDialog(QDialog):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.setWindowTitle("MTS Integration")
        self.setMinimumSize(800, 700)
        self.logger = logger
        
        self.mts_manager = MTSManager(logger=logger)
        self.mts_widgets = {}
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Initialize settings before any QSettings.value usage
        from PyQt5.QtCore import QSettings
        self.settings = QSettings("GeoJSONEditor", "MapboxMTS")

        # Settings form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setSpacing(10)

        # Tilesets CLI Path with embedded browse icon
        cliEdit = QLineEdit(self.settings.value("mts/cli_path", ""))
        cliEdit.setPlaceholderText("Tilesets CLI Path")
        cliEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mts_widgets['cli'] = cliEdit

        def browse_cli():
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.Directory)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                directory = dialog.selectedFiles()[0]
                if directory:
                    cliEdit.setText(directory)

        cliIcon = QIcon.fromTheme("folder-open") or QIcon("browse_icon.png")
        cliAction = QAction(cliIcon, "", cliEdit)
        cliAction.setToolTip("Browse for Tilesets CLI directory")
        cliEdit.addAction(cliAction, QLineEdit.TrailingPosition)
        cliAction.triggered.connect(browse_cli)
        form.addRow("Tilesets CLI :", cliEdit)

        tokenEdit = QLineEdit(self.settings.value("mts/access_token", ""))
        tokenEdit.setPlaceholderText("Access Token")
        tokenEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mts_widgets['token'] = tokenEdit
        form.addRow("Mapbox Access Token :", tokenEdit)

        # ---- Fields above Recipe (username/layer/source/id/name) ----
        postForm = QFormLayout()
        postForm.setLabelAlignment(Qt.AlignLeft)
        postForm.setFormAlignment(Qt.AlignLeft)
        postForm.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        postForm.setSpacing(10)

        # Add username field for update_recipe_table usage
        usernameEdit = QLineEdit(self.settings.value("mts/username", ""))
        usernameEdit.setPlaceholderText("Username")
        usernameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mts_widgets['username'] = usernameEdit
        postForm.addRow("Username :", usernameEdit)

        # Layer Name field (should be above Source Name)
        layerNameEdit = QLineEdit(self.settings.value("mts/layer_name", ""))
        layerNameEdit.setPlaceholderText("Layer Name")
        layerNameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layerNameEdit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
                box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
            }
        """)
        self.mts_widgets['layer_name'] = layerNameEdit
        postForm.addRow("Layer Name :", layerNameEdit)

        # Source Name field (should be below Layer Name)
        sourceEdit = QLineEdit(self.settings.value("mts/source_name", ""))
        sourceEdit.setPlaceholderText("Source Name")
        sourceEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sourceEdit.setStyleSheet(layerNameEdit.styleSheet())
        self.mts_widgets['source_name'] = sourceEdit
        postForm.addRow("Source Name :", sourceEdit)

        idEdit = QLineEdit()
        idEdit.setPlaceholderText("32 characters or less")
        idEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        idEdit.setStyleSheet(layerNameEdit.styleSheet())
        self.mts_widgets['id'] = idEdit
        postForm.addRow("Identifier :", idEdit)

        nameEdit = QLineEdit()
        nameEdit.setPlaceholderText("64 characters or less")
        nameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        nameEdit.setStyleSheet(layerNameEdit.styleSheet())
        self.mts_widgets['name'] = nameEdit
        postForm.addRow("Tileset Name :", nameEdit)
        # Place postForm above recipeGroup!
        layout.addLayout(postForm)

        # ---- Recipe block ----
        recipeGroup = QGroupBox("Recipe")
        recipeGroup.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 1ex;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333;
            }
        """)

        recipeLayout = QVBoxLayout(recipeGroup)
        recipeLayout.setSpacing(10)

        recipeTable = QTableWidget(1, 6)
        recipeTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        recipeTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        recipeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        recipeTable.setHorizontalHeaderLabels(["source", "minzoom", "maxzoom", "layer_name", "fillzoom", "incremental"])
        recipeTable.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            QTableWidget:hover {
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: 1px solid #e0e0e0;
                color: #333;
                transition: all 0.2s ease;
            }
            QHeaderView::section:hover {
                background-color: #e0e0e0;
                color: #2196F3;
            }
        """)
        recipeTable.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.mts_widgets['recipe_table'] = recipeTable

        # Initialize recipe table with default values
        defaults = [
            "mapbox://tileset-source/username/layer_name-source",
            "0", "14", "layer_name",
            "", "false"
        ]
        for col, val in enumerate(defaults):
            recipeTable.setItem(0, col, QTableWidgetItem(val))

        recipeLayout.addWidget(recipeTable)

        # Add buttons for adding rows and columns
        addButtonsLayout = QHBoxLayout()
        addButtonsLayout.setSpacing(10)

        addRowBtn = QPushButton("+ Строка")
        addColBtn = QPushButton("+ Столбец")
        addButtonsLayout.addWidget(addRowBtn)
        addButtonsLayout.addWidget(addColBtn)
        recipeLayout.addLayout(addButtonsLayout)

        self.mts_widgets['add_row'] = addRowBtn
        self.mts_widgets['add_col'] = addColBtn

        # Add QTextEdit for JSON view below the table
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        self.json_view.setVisible(True)
        recipeLayout.addWidget(self.json_view)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        saveRecBtn = QPushButton("Save Recipe")
        saveRecBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: #45a049;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }
            QPushButton:pressed {
                background-color: #388e3c;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }
        """)
        self.mts_widgets['save_recipe'] = saveRecBtn

        openRecBtn = QPushButton("Open Recipe")
        openRecBtn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: #1976D2;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }
            QPushButton:pressed {
                background-color: #1565C0;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }
        """)
        self.mts_widgets['open_recipe'] = openRecBtn

        btns.addWidget(saveRecBtn)
        btns.addWidget(openRecBtn)
        recipeLayout.addLayout(btns)
        layout.addWidget(recipeGroup)

        # Deploy and Publish buttons
        btnsDeploy = QHBoxLayout()
        btnsDeploy.setSpacing(10)

        deployBtn = QPushButton("Deploy Tileset")
        deployBtn.setStyleSheet(saveRecBtn.styleSheet())
        self.mts_widgets['deploy'] = deployBtn

        publishBtn = QPushButton("Publish")
        publishBtn.setStyleSheet(openRecBtn.styleSheet())
        self.mts_widgets['publish'] = publishBtn

        btnsDeploy.addWidget(deployBtn)
        btnsDeploy.addWidget(publishBtn)
        layout.addLayout(btnsDeploy)

        self.setLayout(layout)

        # Activate JSON View at the end
        self.json_view.setFocus()

        # Update recipe table and JSON view after UI setup
        self.update_recipe_table()

    def setup_connections(self):
        # Connect username, source_name, layer_name changes to update recipe table and JSON view
        self.mts_widgets['username'].textChanged.connect(self.update_recipe_table)
        self.mts_widgets['layer_name'].textChanged.connect(self.update_recipe_table)
        self.mts_widgets['source_name'].textChanged.connect(self.update_recipe_table)
        self.mts_widgets['recipe_table'].cellChanged.connect(self.update_recipe_table)

        # Connect add row button
        def add_row():
            recipeTable = self.mts_widgets['recipe_table']
            rowPos = recipeTable.rowCount()
            recipeTable.insertRow(rowPos)
            # Use default values for new row
            defaults = [
                "mapbox://tileset-source/username/layer_name-source",
                "0", "14", "layer_name",
                "", "false"
            ]
            for col in range(recipeTable.columnCount()):
                recipeTable.setItem(rowPos, col, QTableWidgetItem(defaults[col] if col < len(defaults) else ""))

        self.mts_widgets['add_row'].clicked.connect(add_row)

        # Connect add column button
        def add_column():
            recipeTable = self.mts_widgets['recipe_table']
            colPos = recipeTable.columnCount()
            recipeTable.insertColumn(colPos)
            # Set default header name editable
            default_header = f"column_{colPos+1}"
            recipeTable.setHorizontalHeaderItem(colPos, QTableWidgetItem(default_header))
            # Fill new column cells with empty strings
            for row in range(recipeTable.rowCount()):
                recipeTable.setItem(row, colPos, QTableWidgetItem(""))

        self.mts_widgets['add_col'].clicked.connect(add_column)

        # Connect buttons
        self.mts_widgets['save_recipe'].clicked.connect(self.on_save_recipe)
        self.mts_widgets['deploy'].clicked.connect(self.on_deploy_tileset)

    def update_recipe_table(self):
        # Defensive: check all required widgets exist
        if not all(k in self.mts_widgets for k in ['username', 'source_name', 'layer_name', 'recipe_table']):
            return

        username = self.mts_widgets['username'].text()
        source_name = self.mts_widgets['source_name'].text()
        layer_name = self.mts_widgets['layer_name'].text()
        recipeTable = self.mts_widgets['recipe_table']

        if recipeTable.rowCount() > 0:
            # Ensure source item exists
            if not recipeTable.item(0, 0):
                recipeTable.setItem(0, 0, QTableWidgetItem())
            recipeTable.item(0, 0).setText(f"mapbox://tileset-source/{username}/{layer_name}-source")

            # Ensure layer_name item exists
            if not recipeTable.item(0, 3):
                recipeTable.setItem(0, 3, QTableWidgetItem())
            recipeTable.item(0, 3).setText(layer_name)

        # Build JSON from table and fields
        recipe_dict = {"layers": {}}
        headers = [recipeTable.horizontalHeaderItem(i).text() for i in range(recipeTable.columnCount())]

        for row in range(recipeTable.rowCount()):
            layer = {}
            layer_key = None
            for col in range(recipeTable.columnCount()):
                item = recipeTable.item(row, col)
                text = item.text() if item else ""
                header = headers[col]
                if header == "layer_name":
                    layer_key = text
                else:
                    layer[header] = text
            if layer_key:
                recipe_dict["layers"][layer_key] = layer

        # Add username, source_name, layer_name fields
        recipe_dict["username"] = username
        recipe_dict["source_name"] = source_name
        recipe_dict["layer_name"] = layer_name

        # Debug print: show JSON in console to verify update
        print(json.dumps(recipe_dict, indent=2))
        self.json_view.setPlainText(json.dumps(recipe_dict, indent=2))

    def on_save_recipe(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Recipe", "recipe.json", "JSON Files (*.json)")
        if not path:
            return

        recipeTable = self.mts_widgets['recipe_table']
        headers = [recipeTable.horizontalHeaderItem(i).text() for i in range(recipeTable.columnCount())]

        recipe_dict = {"layers": {}}

        for row in range(recipeTable.rowCount()):
            layer = {}
            layer_key = None
            for col in range(recipeTable.columnCount()):
                item = recipeTable.item(row, col)
                text = item.text() if item else ""
                header = headers[col]
                if header == "layer_name":
                    layer_key = text
                else:
                    layer[header] = text
            if layer_key:
                recipe_dict["layers"][layer_key] = layer

        # Optionally add username, source_name, layer_name fields from widgets
        recipe_dict["username"] = self.mts_widgets['username'].text()
        recipe_dict["source_name"] = self.mts_widgets['source_name'].text()
        recipe_dict["layer_name"] = self.mts_widgets['layer_name'].text()

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(recipe_dict, f, ensure_ascii=False, indent=2)
            if self.logger:
                self.logger(f"Saved recipe to {path}", "success")
        except Exception as e:
            if self.logger:
                self.logger(f"Failed to save recipe: {e}", "error")

    def on_deploy_tileset(self):
        source_name = self.mts_widgets['source_name'].text()
        layer_name = self.mts_widgets['layer_name'].text()
        identifier = self.mts_widgets['id'].text()
        name = self.mts_widgets['name'].text()
        
        if not all([source_name, layer_name, identifier, name]):
            self.logger("All fields must be filled to deploy", "error")
            return
            
        try:
            # Create recipe file
            recipe = {
                "version": 1,
                "layers": {
                    layer_name: {
                        "source": f"mapbox://tileset-source/{self.username}/{source_name}-source",
                        "minzoom": 0,
                        "maxzoom": 14
                    }
                }
            }
            
            # Save recipe
            recipe_path = "recipe.json"
            with open(recipe_path, 'w') as f:
                json.dump(recipe, f, ensure_ascii=False, indent=2)
            
            # Upload source and create tileset
            self.logger("Uploading source...", "info")
            result = self.manager.upload_source(f"{source_name}-source", self.file_path)
            self.logger(result, "info")
            
            self.logger("Creating tileset...", "info")
            result = self.manager.create_tileset(identifier, recipe_path, name)
            self.logger(result, "info")
            
            self.logger("Publishing tileset...", "info")
            result = self.manager.publish_tileset(identifier, self.logger)
            self.logger(result, "info")
            
            self.logger("Tileset deployment complete!", "success")
        except Exception as e:
            self.logger(f"Error deploying tileset: {e}", "error")
