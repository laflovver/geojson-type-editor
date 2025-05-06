import sys
import json
import tempfile
import folium
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QInputDialog,
    QLineEdit, QDialog, QMessageBox, QTextEdit,
    QFormLayout, QTabWidget, QSizePolicy, QAbstractScrollArea,
    QGroupBox, QLabel, QAction
)
from PyQt5.QtCore import QSettings
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtGui import QIcon
import os
from logic import GeoJSONManager

class GeoJSONEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = GeoJSONManager()
        self.init_ui()
        # Set initial window size to 800×600
        self.resize(800, 600)

    def init_ui(self):
        self.setWindowTitle("GeoJSON Blossom")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Button panel
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load GeoJSON")
        self.toggle_btn = QPushButton("Toggle Type")
        self.extract_btn = QPushButton("Extract Route")
        self.save_btn = QPushButton("Save As")
        # Disable until GeoJSON is loaded
        self.toggle_btn.setEnabled(False)
        self.extract_btn.setEnabled(False)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addWidget(self.extract_btn)
        btn_layout.addWidget(self.save_btn)
        # MTS Integration button
        self.mts_btn = QPushButton("MTS Integration")
        btn_layout.addWidget(self.mts_btn)
        self.view_btn = QPushButton("Show Table")
        self.view_btn.setObjectName("view_btn")
        self.view_btn.setStyleSheet("""
        QPushButton#view_btn {
            border-radius: 5px;
            background: rgba(217, 217, 217, 0.20);
            margin-bottom: 10px;
        }
        QPushButton#view_btn:hover {
            background: rgba(217, 217, 217, 0.40);
        }
        QPushButton#view_btn:pressed {
            background: rgba(217, 217, 217, 0.60);
        }
        """)
        self.view_btn.setVisible(False)
        # btn_layout.addWidget(self.view_btn)

        layout.addLayout(btn_layout)

        # Feature table
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Map preview (hidden by default) within a container for overlay button
        self.map_view = QWebEngineView()
        self.map_view.setVisible(False)
        # Container to overlay the Show Table button on the map
        map_container = QWidget()
        map_layout = QGridLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 10)
        # add map view
        map_layout.addWidget(self.map_view, 0, 0)
        # overlay Show Table button at bottom-center
        self.view_btn.setVisible(False)
        map_layout.addWidget(self.view_btn, 0, 0, alignment=Qt.AlignHCenter | Qt.AlignBottom)
        layout.addWidget(map_container)

        # Log console (read-only, five lines high)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(5 * self.fontMetrics().height())
        layout.addWidget(self.log)

        # Connections
        self.load_btn.clicked.connect(self.load_geojson)
        self.toggle_btn.clicked.connect(self.on_toggle)
        self.extract_btn.clicked.connect(self.on_extract)
        self.save_btn.clicked.connect(self.on_save)
        self.view_btn.clicked.connect(self.on_view_table)
        # Connect MTS Integration
        self.mts_btn.clicked.connect(self.on_mts_integration)

    def log_message(self, msg, level="info"):
        color = {"info": "#4F5D75", "success": "#4CAF50", "error": "#FF5C61"}.get(level, "#4F5D75")
        self.log.insertHtml(f'<span style="color:{color};">{msg}</span><br>')
        # auto-scroll to bottom
        cursor = self.log.textCursor()
        cursor.movePosition(cursor.End)
        self.log.setTextCursor(cursor)

    def load_geojson(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open GeoJSON", "", "GeoJSON Files (*.geojson *.json)")
        if path:
            self.manager.load(path)
            features, keys = self.manager.get_features_and_keys()
            self.populate_table(features, keys)
            self.log_message(f"Loaded GeoJSON: {path}", "success")
            # Enable actions now that data is loaded
            self.toggle_btn.setEnabled(True)
            self.extract_btn.setEnabled(True)

    def populate_table(self, features, keys):
        self.table.clear()
        self.table.setColumnCount(len(keys))
        self.table.setRowCount(len(features))
        self.table.setHorizontalHeaderLabels(keys)
        for i, feat in enumerate(features):
            props = feat.get("properties", {})
            for j, key in enumerate(keys):
                val = props.get(key, "")
                text = str(val)
                # Prefix by type indicator
                if isinstance(val, int):
                    text = "# " + text
                elif isinstance(val, float):
                    text = "% " + text
                else:
                    text = '" ' + text
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        # Adjust column widths to contents
        self.table.resizeColumnsToContents()

    def on_toggle(self):
        col = self.table.currentColumn()
        row = self.table.currentRow()
        features, keys = self.manager.get_features_and_keys()
        if col < 0 or col >= len(keys):
            return
        # Capture the current cell's text before toggling
        old_text = None
        if row >= 0 and col >= 0:
            item = self.table.item(row, col)
            if item:
                old_text = item.text()
        try:
            self.manager.toggle_type(col, keys)
        except Exception as e:
            self.log_message(f"Cannot toggle type in column '{keys[col]}': {e}", "error")
            return
        features, keys = self.manager.get_features_and_keys()
        self.populate_table(features, keys)
        # restore selection of cell and entire column
        if row >= 0 and col >= 0:
            self.table.setCurrentCell(row, col)
            self.table.selectColumn(col)
        # Capture new cell's text after toggling
        new_text = None
        if row >= 0 and col >= 0:
            item = self.table.item(row, col)
            if item:
                new_text = item.text()
        # Map type indicators to human-readable types
        type_map = {'#': 'integer', '"': 'string', '%': 'float'}
        old_type = type_map.get(old_text[0], 'unknown') if old_text else 'unknown'
        new_type = type_map.get(new_text[0], 'unknown') if new_text else 'unknown'
        self.log_message(f"Column '{keys[col]}' changed from {old_type} to {new_type}", "success")

    def on_extract(self):
        # Prompt for route name; Enter will accept
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Route Name")
        dialog.setLabelText("Enter route name:")
        dialog.setTextValue(getattr(self.manager, "route_name", ""))
        # find the internal QLineEdit and bind Enter
        line_edit = dialog.findChild(__import__('PyQt5').QtWidgets.QLineEdit)
        if line_edit:
            line_edit.returnPressed.connect(dialog.accept)
        if dialog.exec_() == dialog.Accepted:
            name = dialog.textValue().strip()
            if name:
                self.manager.route_name = name
        # Attempt to extract route
        try:
            self.manager.extract_route()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            self.log_message(f"Error extracting route: {e}", "error")
            return
        # Show map preview
        self._show_map_preview()
        self.log_message("Route prepared successfully", "success")

    def _show_map_preview(self):
        # Hide table, show map
        self.table.setVisible(False)
        self.map_view.setVisible(True)
        self.view_btn.setVisible(True)

        # Prepare GeoJSON and calculate center
        features, _ = self.manager.get_features_and_keys()
        geojson_obj = {"type": "FeatureCollection", "features": features}

        lats, lons = [], []
        for f in features:
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [])
            pts = []
            if isinstance(coords, (list, tuple)):
                if len(coords) == 2 and isinstance(coords[0], (int, float)):
                    pts = [coords]
                else:
                    for part in coords:
                        if isinstance(part[0], (int, float)):
                            pts.append(part)
                        else:
                            pts.extend(part)
            for lon, lat in pts:
                lons.append(lon)
                lats.append(lat)

        if lats and lons:
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
        else:
            center_lat, center_lon = 0, 0

        # Create folium map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
        folium.GeoJson(geojson_obj).add_to(m)

        # Save and load in QWebEngineView
        tmp = tempfile.NamedTemporaryFile(prefix="geojson_preview_", suffix=".html", delete=False)
        m.save(tmp.name)
        tmp.flush()
        self.map_view.load(QUrl.fromLocalFile(tmp.name))

    def on_save(self):
        # Use route name as default if set, otherwise fallback to manager’s default
        if hasattr(self.manager, "route_name") and self.manager.route_name:
            default_name = f"{self.manager.route_name}.geojson"
        else:
            default_name = self.manager.get_default_filename()
        path, _ = QFileDialog.getSaveFileName(self, "Save GeoJSON", default_name, "GeoJSON Files (*.geojson)")
        if path:
            self.manager.save(path)
            self.log_message(f"File saved to: {path}", "success")

    def on_view_table(self):
        # Hide map, show table, hide view button
        self.map_view.setVisible(False)
        self.table.setVisible(True)
        self.view_btn.setVisible(False)

    def on_mts_integration(self):
        # Open MTS Integration dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("MTS Integration")
        dlg.setMinimumSize(800, 700)
        dlg_layout = QVBoxLayout(dlg)

        settings = QSettings("GeoJSONEditor", "MapboxMTS")

        # MTS Settings form
        form = QFormLayout()
        # Ensure input fields expand with dialog
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        # Align form labels and fields to the left
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft)
        # Tilesets CLI Path – встроенный browse-icon в поле
        cliEdit = QLineEdit(settings.value("mts/cli_path", ""))
        cliEdit.setPlaceholderText("Tilesets CLI Path")
        cliEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cliEdit.setStyleSheet("border: 1px solid #ccc;")
        def browse_cli():
            directory = QFileDialog.getExistingDirectory(self, "Select Tilesets CLI Directory")
            if directory:
                cliEdit.setText(directory)
        # Embed browse icon action inside the QLineEdit
        cliIcon = QIcon.fromTheme("folder-open") or QIcon("browse_icon.png")
        cliAction = QAction(cliIcon, "", cliEdit)
        cliAction.setToolTip("Browse for Tilesets CLI directory")
        cliEdit.addAction(cliAction, QLineEdit.TrailingPosition)
        cliAction.triggered.connect(browse_cli)
        # Also open browse dialog when clicking on the QLineEdit itself
        original_mouse_press = cliEdit.mousePressEvent
        def mouse_press_event(event):
            browse_cli()
            return original_mouse_press(event)
        cliEdit.mousePressEvent = mouse_press_event
        form.addRow("Tilesets CLI", cliEdit)
        tokenEdit = QLineEdit(settings.value("mts/access_token", ""))
        tokenEdit.setPlaceholderText("...")
        tokenEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tokenEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        form.addRow("Mapbox Access Token", tokenEdit)
        userEdit = QLineEdit(settings.value("mts/username", ""))
        userEdit.setPlaceholderText("...")
        userEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        userEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        form.addRow("Mapbox Username", userEdit)
        sourceEdit = QLineEdit(settings.value("mts/source_name", ""))
        sourceEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sourceEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        # sourceEdit.setPlaceholderText(" ... ")
        # form.addRow("Source Name :", sourceEdit)

        idEdit = QLineEdit()
        idEdit.setPlaceholderText(" ≤ 64 characters ")
        idEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        idEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        # form.addRow("Identifier :", idEdit)

        nameEdit = QLineEdit()
        nameEdit.setPlaceholderText(" ≤ 64 characters ")
        nameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        nameEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        # form.addRow("Tileset Name :", nameEdit)

        # Add the form layout directly
        dlg_layout.addLayout(form)

        # Save settings helper
        def save_settings():
            settings.setValue("mts/cli_path", cliEdit.text())
            settings.setValue("mts/access_token", tokenEdit.text())
            settings.setValue("mts/username", userEdit.text())
            self.manager.configure_mts(
                cliEdit.text(),
                tokenEdit.text(),
                userEdit.text(),
                logger=self.log_message
            )

        # Recipe block
        recipeGroup = QGroupBox("Recipe")
        recipeLayout = QVBoxLayout(recipeGroup)
        from PyQt5.QtWidgets import QHeaderView
        recipeTable = QTableWidget(1, 6)
        recipeTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        recipeTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        recipeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        recipeTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        recipeTable.setHorizontalHeaderLabels(["source", "minzoom", "maxzoom", "layer_name", "fillzoom", "incremental"])
        defaults = [
            f"mapbox://tileset-source/{userEdit.text()}/layer_name-source",
            "0",    # minzoom
            "14",   # maxzoom
            "layer_name",
            "",     # fillzoom
            "false" # incremental
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
        # Save recipe to file
        def on_save_recipe():
            save_settings()
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Recipe", "recipe.json", "JSON Files (*.json)"
            )
            if not path:
                return
            layers = {}
            for i in range(recipeTable.rowCount()):
                minzoom = int(recipeTable.item(i, 0).text())
                maxzoom = int(recipeTable.item(i, 1).text())
                # Clamp maxzoom to allowed maximum of 14
                if maxzoom > 14:
                    maxzoom = 14
                layer_name = recipeTable.item(i, 2).text()
                # Read optional fillzoom
                fillzoom_item = recipeTable.item(i, 3)
                layer_spec = {
                    "minzoom": minzoom,
                    "maxzoom": maxzoom
                }
                if fillzoom_item and fillzoom_item.text().strip():
                    layer_spec["fillzoom"] = int(fillzoom_item.text())
                layers[layer_name] = layer_spec
            # Read global incremental flag from table (first row)
            inc = False
            inc_item = recipeTable.item(0, 4)
            if inc_item and inc_item.text().strip().lower() == "true":
                inc = True
            # Wrap into a valid MTS recipe specification with version and options
            recipe_spec = {
                "version": 1,
                "incremental": inc,
                "layers": layers
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(recipe_spec, f, ensure_ascii=False, indent=2)
            self.currentRecipePath = path
            self.log_message(f"Recipe saved to {path}", "success")

        saveRecBtn.clicked.connect(on_save_recipe)
        openRecBtn.clicked.connect(self.on_open_recipe)
        dlg_layout.addWidget(recipeGroup)

        # Fields below Recipe block
        post_form = QFormLayout()
        post_form.setLabelAlignment(Qt.AlignLeft)
        post_form.setFormAlignment(Qt.AlignLeft)
        # Ensure post-recipe fields expand horizontally
        sourceEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        idEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        nameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        post_form.addRow("Source Name", sourceEdit)
        post_form.addRow("Identifier", idEdit)
        post_form.addRow("Tileset Name", nameEdit)
        dlg_layout.addLayout(post_form)

        # Create & publish
        createBtn = QPushButton("Deploy Tileset")
        pubBtn = QPushButton("Publish")
        createBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pubBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btnsDeploy = QHBoxLayout()
        btnsDeploy.addWidget(createBtn)
        btnsDeploy.addWidget(pubBtn)
        dlg_layout.addLayout(btnsDeploy)

        def on_deploy_tileset():
            save_settings()
            tileset_name = sourceEdit.text().strip()
            if not tileset_name:
                self.log_message("Tileset source name is required", "error")
                return
            try:
                self.log_message(f"Uploading source: {tileset_name}", "info")
                upload_result = self.manager.upload_source(tileset_name)
                self.log_message(f"Upload Source result: {upload_result}", "success")
            except Exception as e:
                self.log_message(f"Upload source failed: {e}", "error")
                return
            try:
                self.log_message(f"Creating tileset: {idEdit.text()}", "info")
                create_result = self.manager.create_tileset(
                    idEdit.text(),
                    getattr(self, 'currentRecipePath', ''),
                    nameEdit.text()
                )
                self.log_message(f"Create Tileset result: {create_result}", "success")
            except Exception as e:
                self.log_message(f"Create tileset failed: {e}", "error")
                return

        createBtn.clicked.connect(on_deploy_tileset)
        pubBtn.clicked.connect(lambda: self.manager.publish_tileset(
            idEdit.text(), status_callback=self.log_message
        ))

        # Persist settings when dialog closes
        dlg.finished.connect(save_settings)
        dlg.exec_()

    def on_open_recipe(self):
        """Open a recipe JSON file into the table."""
        path, _ = QFileDialog.getOpenFileName(self, "Open Recipe", "", "JSON Files (*.json)")
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        # TODO: populate recipeTable from loaded recipe
        self.log_message(f"Recipe loaded from {path}", "info")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load QSS stylesheet
    qss_path = os.path.join(os.path.dirname(__file__), "qt_style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    # Load application fonts
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, "RobotoMono-VariableFont_wght.ttf"))
    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, "RobotoMono-Italic-VariableFont_wght.ttf"))
    editor = GeoJSONEditor()
    editor.show()
    sys.exit(app.exec_())