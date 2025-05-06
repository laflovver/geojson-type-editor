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
    QGroupBox, QLabel, QAction, QStyle, QButtonGroup
)
from PyQt5.QtCore import QSettings
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtGui import QIcon
import os
from logic import GeoJSONManager

# Delegate for opaque editor background
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QColor

# JSON syntax highlighter imports
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp

# JSON Syntax Highlighter
class JSONHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        # Define formats
        self.rules = []
        # String: e.g. "key" or "value"
        fmt_string = QTextCharFormat()
        fmt_string.setForeground(QColor("#D16969"))
        self.rules.append((QRegExp('"(?:[^"\\\\]|\\\\.)*"'), fmt_string))
        # Numbers
        fmt_number = QTextCharFormat()
        fmt_number.setForeground(QColor("#69D169"))
        self.rules.append((QRegExp("\\b[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?\\b"), fmt_number))
        # Boolean and null
        fmt_keyword = QTextCharFormat()
        fmt_keyword.setForeground(QColor("#6970D1"))
        self.rules.append((QRegExp("\\b(true|false|null)\\b"), fmt_keyword))
        # Braces and brackets
        fmt_brace = QTextCharFormat()
        fmt_brace.setForeground(QColor("#CCCCCC"))
        for pattern in ["[{}\\[\\]]", "[:,]"]:
            self.rules.append((QRegExp(pattern), fmt_brace))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text, 0)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)

# Delegate that provides an opaque editor to clear previous text artifacts.
class EditorDelegate(QStyledItemDelegate):
    """Delegate that provides an opaque editor to clear previous text artifacts."""
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        # Ensure opaque white background
        editor.setAutoFillBackground(True)
        editor.setStyleSheet("background-color: white;")
        return editor

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
        layout.addLayout(btn_layout)

        # Feature table
        self.table = QTableWidget()
        # Install delegate to ensure cell editors have opaque background
        self.table.setItemDelegate(EditorDelegate(self.table))
        layout.addWidget(self.table)

        # Code view for raw GeoJSON
        self.code_view = QTextEdit()
        self.code_view.setReadOnly(False)
        self.code_view.setVisible(False)
        layout.addWidget(self.code_view)

        # Apply JSON syntax highlighting to raw GeoJSON view
        self.json_highlighter = JSONHighlighter(self.code_view.document())

        # Map preview (hidden by default) within a container
        self.map_view = QWebEngineView()
        self.map_view.setVisible(False)
        map_container = QWidget()
        map_layout = QGridLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 10)
        map_layout.addWidget(self.map_view, 0, 0)
        layout.addWidget(map_container)

        # View mode buttons at bottom in a single container with active states
        self.table_btn = QPushButton("Table")
        self.json_btn = QPushButton("JSON")
        self.map_btn = QPushButton("Map")
        # Make buttons checkable for active state
        self.table_btn.setCheckable(True)
        self.json_btn.setCheckable(True)
        self.map_btn.setCheckable(True)
        # Initially disabled until data loaded
        self.table_btn.setEnabled(False)
        self.json_btn.setEnabled(False)
        self.map_btn.setEnabled(False)
        # Group buttons for exclusive selection
        view_group = QButtonGroup(self)
        view_group.addButton(self.table_btn)
        view_group.addButton(self.json_btn)
        view_group.addButton(self.map_btn)
        view_group.setExclusive(True)
        # Default to Table view when enabled
        self.table_btn.setChecked(True)
        view_layout = QHBoxLayout()
        view_layout.addWidget(self.table_btn)
        view_layout.addWidget(self.json_btn)
        view_layout.addWidget(self.map_btn)
        layout.addLayout(view_layout)

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
        self.table_btn.clicked.connect(self.show_table_view)
        self.json_btn.clicked.connect(self.show_json_view)
        self.map_btn.clicked.connect(self.show_map_view)
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
            # Store raw GeoJSON for code view
            try:
                self.manager.raw_data = self.manager._load_raw_json(path)
            except AttributeError:
                with open(path, "r", encoding="utf-8") as f:
                    self.manager.raw_data = json.load(f)
            features, keys = self.manager.get_features_and_keys()
            self.populate_table(features, keys)
            self.log_message(f"Loaded GeoJSON: {path}", "success")
            # Enable actions now that data is loaded
            self.toggle_btn.setEnabled(True)
            self.extract_btn.setEnabled(True)
            self.table_btn.setEnabled(True)
            self.json_btn.setEnabled(True)
        self.code_view.setVisible(False)

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
            # Only extract route if user confirmed
            try:
                self.manager.extract_route()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
                self.log_message(f"Error extracting route: {e}", "error")
                return
            # Show map preview
            self._show_map_preview()
            self.log_message("Route prepared successfully", "success")
            self.map_btn.setEnabled(True)
            # Automatically switch to Map view
            self.show_map_view()
            self.map_btn.setChecked(True)
        else:
            # User cancelled; do nothing
            return

    def _show_map_preview(self):
        # Hide table, show map
        self.table.setVisible(False)
        self.map_view.setVisible(True)
        # Enable the Map view button now that preview is available
        self.map_btn.setEnabled(True)

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


    def show_table_view(self):
        self.code_view.setVisible(False)
        self.map_view.setVisible(False)
        self.table.setVisible(True)

    def show_json_view(self):
        self.table.setVisible(False)
        self.map_view.setVisible(False)
        self.code_view.setVisible(True)
        # Populate JSON view
        raw = getattr(self.manager, "raw_data", None)
        if raw is not None:
            self.code_view.setPlainText(json.dumps(raw, indent=2))
            # Refresh syntax highlighting
            self.json_highlighter.rehighlight()

    def show_map_view(self):
        # Only show map if available
        self.code_view.setVisible(False)
        self.table.setVisible(False)
        self.map_view.setVisible(True)

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
        # Tilesets CLI Path with browse icon
        cliEdit = QLineEdit(settings.value("mts/cli_path", ""))
        cliEdit.setPlaceholderText("Tilesets CLI Path")
        cliEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cliEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        # Browse helper
        def browse_cli():
            directory = QFileDialog.getExistingDirectory(self, "Select Tilesets CLI Directory")
            if directory:
                cliEdit.setText(directory)
        # Embed custom browse icon from ui/folder-add.png
        base_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(base_dir, "ui", "folder-add.png")
        browseIcon = QIcon(icon_path)
        browseAction = QAction(browseIcon, "", cliEdit)
        browseAction.setToolTip("Browse for Tilesets CLI directory")
        cliEdit.addAction(browseAction, QLineEdit.TrailingPosition)
        browseAction.triggered.connect(browse_cli)
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
        idEdit.setPlaceholderText("≤ 32 characters ")
        idEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        idEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        # form.addRow("Identifier :", idEdit)

        nameEdit = QLineEdit()
        nameEdit.setPlaceholderText("≤ 64 characters ")
        nameEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        nameEdit.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #ccc;")
        # form.addRow("Tileset Name :", nameEdit)

        # Update recipe 'source' when Source Name changes
        def update_recipe_source(text):
            # Construct new source URI
            uri = f"mapbox://tileset-source/{userEdit.text()}/{text}"
            # Update table cell and JSON view if visible
            recipeTable.setItem(0, 0, QTableWidgetItem(uri))
            if recipeCodeView.isVisible():
                # Refresh JSON view
                show_recipe_json()
        sourceEdit.textChanged.connect(update_recipe_source)

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
        # Apply same delegate to recipe table
        recipeTable.setItemDelegate(EditorDelegate(recipeTable))
        recipeTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        recipeTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        recipeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        recipeTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        recipeTable.setHorizontalHeaderLabels(["source", "minzoom", "maxzoom", "layer_name", "fillzoom", "incremental"])
        defaults = [
            f"mapbox://tileset-source/{userEdit.text()}/{sourceEdit.text()}",
            "0",    # minzoom
            "14",   # maxzoom
            "layer_name",
            "",     # fillzoom
            "false" # incremental
        ]
        for col, val in enumerate(defaults):
            recipeTable.setItem(0, col, QTableWidgetItem(val))
        # Hide source column in recipe table
        recipeTable.hideColumn(0)
        recipeLayout.addWidget(recipeTable)

        # Add JSON view for recipe and toggle buttons
        recipeCodeView = QTextEdit()
        recipeCodeView.setReadOnly(False)
        recipeCodeView.setVisible(False)
        recipeLayout.addWidget(recipeCodeView)

        # Apply JSON syntax highlighting to recipe view
        self.recipe_highlighter = JSONHighlighter(recipeCodeView.document())

        # Buttons to toggle recipe display
        toggleRecipeBtnLayout = QHBoxLayout()
        showRecTableBtn = QPushButton("Table View")
        showRecJsonBtn = QPushButton("JSON View")
        showRecTableBtn.setCheckable(True)
        showRecJsonBtn.setCheckable(True)
        showRecTableBtn.setChecked(True)
        recBtnGroup = QButtonGroup(self)
        recBtnGroup.addButton(showRecTableBtn)
        recBtnGroup.addButton(showRecJsonBtn)
        toggleRecipeBtnLayout.addWidget(showRecTableBtn)
        toggleRecipeBtnLayout.addWidget(showRecJsonBtn)
        recipeLayout.addLayout(toggleRecipeBtnLayout)

        # Handlers to switch recipe views
        def show_recipe_table():
            # Parse JSON from code view back into table
            try:
                data = json.loads(recipeCodeView.toPlainText())
                layers = data.get("layers", {})
                recipeTable.clearContents()
                recipeTable.setRowCount(len(layers))
                for row, (layer_name, spec) in enumerate(layers.items()):
                    # source column
                    recipeTable.setItem(row, 0, QTableWidgetItem(spec.get("source", "")))
                    recipeTable.setItem(row, 1, QTableWidgetItem(str(spec.get("minzoom", ""))))
                    recipeTable.setItem(row, 2, QTableWidgetItem(str(spec.get("maxzoom", ""))))
                    recipeTable.setItem(row, 3, QTableWidgetItem(layer_name))
                    recipeTable.setItem(row, 4, QTableWidgetItem(str(spec.get("fillzoom", ""))))
                    recipeTable.setItem(row, 5, QTableWidgetItem(str(spec.get("incremental", ""))))
            except Exception as e:
                self.log_message(f"Error parsing JSON: {e}", "error")
                return
            recipeCodeView.setVisible(False)
            recipeTable.setVisible(True)
        def show_recipe_json():
            # Build JSON from table (first sync table -> JSON)
            layers = {}
            for i in range(recipeTable.rowCount()):
                source = recipeTable.item(i, 0).text()
                minz = int(recipeTable.item(i, 1).text())
                maxz = int(recipeTable.item(i, 2).text())
                layer_name = recipeTable.item(i, 3).text()
                fillzoom_item = recipeTable.item(i, 4)
                spec = {"source": source, "minzoom": minz, "maxzoom": maxz}
                if fillzoom_item and fillzoom_item.text().strip():
                    spec["fillzoom"] = int(fillzoom_item.text())
                inc = recipeTable.item(i, 5).text().strip().lower() == "true"
                spec["incremental"] = inc
                layers[layer_name] = spec
            recipe_spec = {"version": 1, "layers": layers}
            recipeCodeView.setReadOnly(False)
            recipeCodeView.setPlainText(json.dumps(recipe_spec, indent=2))
            # Refresh recipe syntax highlighting
            self.recipe_highlighter.rehighlight()
            recipeTable.setVisible(False)
            recipeCodeView.setVisible(True)

        showRecTableBtn.clicked.connect(show_recipe_table)
        showRecJsonBtn.clicked.connect(show_recipe_json)
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
        # Allow post-form fields to expand horizontally
        post_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
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
            # Auto-generate recipe if not specified
            recipe_path = getattr(self, 'currentRecipePath', '')
            if not recipe_path:
                import tempfile, json
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
                layers = {}
                for i in range(recipeTable.rowCount()):
                    # Hidden 'source' column skipped
                    minzoom = int(recipeTable.item(i, 1).text())
                    maxzoom = int(recipeTable.item(i, 2).text())
                    layer_name = recipeTable.item(i, 3).text()
                    fill_item = recipeTable.item(i, 4)
                    # Use full Mapbox tileset-source URI
                    spec = {
                        "source": f"mapbox://tileset-source/{userEdit.text()}/{sourceEdit.text()}",
                        "minzoom": minzoom,
                        "maxzoom": maxzoom
                    }
                    if fill_item and fill_item.text().strip():
                        spec["fillzoom"] = int(fill_item.text())
                    inc = False
                    inc_item = recipeTable.item(i, 5)
                    if inc_item and inc_item.text().strip().lower() == "true":
                        inc = True
                    spec["incremental"] = inc
                    layers[layer_name] = spec
                recipe_spec = {"version":1, "layers": layers}
                json.dump(recipe_spec, tmp, ensure_ascii=False, indent=2)
                tmp.flush()
                tmp.close()
                recipe_path = tmp.name
                self.currentRecipePath = recipe_path
                self.log_message(f"Auto-generated recipe at {recipe_path}", "info")
            try:
                self.log_message(f"Creating tileset: {idEdit.text()}", "info")
                create_result = self.manager.create_tileset(
                    idEdit.text(),
                    recipe_path,
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