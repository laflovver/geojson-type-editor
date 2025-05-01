#!/usr/bin/env python3
import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel,
                             QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QHeaderView)
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QTimer

class GeoJSONEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoJSON Type Editor")
        self.resize(900, 600)

        # Create icons for types
        self.num_icon = self.create_icon('#')
        self.str_icon = self.create_icon('“')

        self.geojson_data = None
        self.keys = []

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Controls
        ctrl_layout = QHBoxLayout()
        layout.addLayout(ctrl_layout)

        self.load_btn = QPushButton("Load GeoJSON")
        self.load_btn.clicked.connect(self.load_geojson)
        ctrl_layout.addWidget(self.load_btn)

        self.toggle_btn = QPushButton("Toggle Type")
        self.toggle_btn.clicked.connect(self.toggle_type)
        self.toggle_btn.setEnabled(False)
        ctrl_layout.addWidget(self.toggle_btn)

        self.save_btn = QPushButton("Save As...")
        self.save_btn.clicked.connect(self.save_geojson)
        self.save_btn.setEnabled(False)
        ctrl_layout.addWidget(self.save_btn)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.update_status)
        layout.addWidget(self.table)

        # Column selection
        self.selected_col = None
        hheader = self.table.horizontalHeader()
        hheader.sectionClicked.connect(self.select_key)
        self.table.cellClicked.connect(self.handle_cell_click)

        # Status bar
        self.status_label = QLabel("Type: ")
        self.statusBar().addPermanentWidget(self.status_label)

    def create_icon(self, char):
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        font = QFont('Arial', 12)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(Qt.black)
        painter.drawText(pix.rect(), Qt.AlignCenter, char)
        painter.end()
        return QIcon(pix)

    def load_geojson(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open GeoJSON", filter="GeoJSON Files (*.geojson *.json)")
        if not path:
            return
        self.loaded_path = path
        self.loaded_dir, filename = os.path.split(path)
        basename, ext = os.path.splitext(filename)
        self.loaded_basename = basename
        self.loaded_ext = ext
        with open(path, 'r', encoding='utf-8') as f:
            self.geojson_data = json.load(f)
        features = self.geojson_data.get('features', [])
        key_set = set()
        for feat in features:
            key_set.update(feat.get('properties', {}).keys())
        self.keys = sorted(key_set)
        self.toggle_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.populate_table()

    def populate_table(self):
        features = self.geojson_data.get('features', [])
        self.table.clear()
        self.table.setRowCount(len(features))
        self.table.setColumnCount(len(self.keys))
        self.table.setHorizontalHeaderLabels(self.keys)
        feature_labels = []
        for idx, feat in enumerate(features):
            fid = feat.get('id', str(idx))
            feature_labels.append(str(fid))
        self.table.setVerticalHeaderLabels(feature_labels)
        hheader = self.table.horizontalHeader()
        hheader.setSectionResizeMode(QHeaderView.ResizeToContents)
        hheader.setStretchLastSection(True)
        vheader = self.table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeToContents)
        for i, feat in enumerate(features):
            props = feat.get('properties', {})
            for j, key in enumerate(self.keys):
                val = props.get(key, '')
                item = QTableWidgetItem(str(val))
                if isinstance(val, (int, float)):
                    item.setIcon(self.num_icon)
                    bg = QColor(220, 245, 220)
                else:
                    item.setIcon(self.str_icon)
                    bg = QColor(225, 225, 245)
                item.setBackground(bg)
                item.setData(Qt.UserRole, bg)
                item.setToolTip(type(val).__name__)
                self.table.setItem(i, j, item)

    def update_status(self):
        item = self.table.currentItem()
        if not item or not self.geojson_data:
            self.status_label.setText("Type: ")
            return
        row, col = item.row(), item.column()
        key = self.keys[col]
        val = self.geojson_data['features'][row]['properties'].get(key)
        self.status_label.setText(f"Type: {type(val).__name__}")

    def select_key(self, index):
        features = self.geojson_data.get('features', [])
        key = self.keys[index]
        sample = None
        for feat in features:
            if key in feat.get('properties', {}):
                sample = feat['properties'][key]
                break
        can_toggle = False
        if isinstance(sample, (int, float)):
            can_toggle = True
        elif isinstance(sample, str):
            try:
                float(sample)
                can_toggle = True
            except:
                can_toggle = False
        if self.selected_col is not None:
            for r in range(self.table.rowCount()):
                prev = self.table.item(r, self.selected_col)
                if prev:
                    prev.setBackground(prev.data(Qt.UserRole))
        if can_toggle:
            self.selected_col = index
            blue = QColor(0, 120, 215, 100)
            for r in range(self.table.rowCount()):
                item = self.table.item(r, index)
                if item:
                    item.setBackground(blue)
            self.status_label.setText(f"Selected key: {key}")
            self.toggle_btn.setEnabled(True)
        else:
            red1 = QColor(255, 0, 0, 120)
            for r in range(self.table.rowCount()):
                it = self.table.item(r, index)
                if not it: continue
                orig = it.data(Qt.UserRole)
                it.setBackground(red1)
                QTimer.singleShot(300, lambda it=it, bg=orig: it.setBackground(bg))
            self.status_label.setText(f"Cannot toggle key: {key}")
            self.toggle_btn.setEnabled(False)

    def handle_cell_click(self, row, col):
        if self.selected_col is not None and col == self.selected_col:
            return
        item = self.table.item(row, col)
        if not item:
            return
        orig = item.data(Qt.UserRole)
        flash1 = QColor(255, 0, 0, 150)
        flash2 = QColor(255, 0, 0, 50)
        item.setBackground(flash1)
        QTimer.singleShot(200, lambda it=item, bg=flash2: it.setBackground(bg))
        QTimer.singleShot(400, lambda it=item, bg=orig: it.setBackground(bg))

    def toggle_type(self):
        if not self.geojson_data or self.selected_col is None:
            return
        key = self.keys[self.selected_col]
        features = self.geojson_data.get('features', [])
        sample = next((f['properties'].get(key) for f in features if key in f['properties']), None)
        to_string = isinstance(sample, (int, float))
        # track last conversion type for default save name
        self.last_conversion = 'string' if to_string else 'number'
        for i, feat in enumerate(features):
            props = feat.get('properties', {})
            if key not in props:
                continue
            val = props[key]
            try:
                new_val = str(val) if to_string else (int(val) if isinstance(val, str) and val.isdigit() else float(val))
            except:
                new_val = val
            props[key] = new_val
            item = self.table.item(i, self.selected_col)
            item.setText(str(new_val))
            if isinstance(new_val, (int, float)):
                item.setIcon(self.num_icon)
                item.setBackground(QColor(220, 245, 220))
            else:
                item.setIcon(self.str_icon)
                item.setBackground(QColor(225, 225, 245))
            item.setToolTip(type(new_val).__name__)

    def save_geojson(self):
        # Prepare default filename
        initial_name = getattr(self, 'loaded_basename', 'output')
        if hasattr(self, 'last_conversion'):
            initial_name += '_' + self.last_conversion
        initial_path = os.path.join(getattr(self, 'loaded_dir', ''), initial_name + getattr(self, 'loaded_ext', '.geojson'))
        path, _ = QFileDialog.getSaveFileName(self, "Save GeoJSON As", initial_path, filter="GeoJSON Files (*.geojson *.json)")
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.geojson_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Roboto Mono', 14))
    app.setStyle('Fusion')
    qss = '''
QMainWindow { background-color: #ffffff; }
QWidget { font-family: 'Roboto Mono'; font-size: 14px; color: #333333; }
QPushButton { background-color: #e0e0e0; color: #333333; border: none; border-radius: 3px; padding: 4px 8px; }
QPushButton:hover { background-color: #d5d5d5; }
QTableWidget { background-color: #ffffff; gridline-color: #dddddd; alternate-background-color: #f9f9f9; }
QHeaderView::section { background-color: #f0f0f0; border: none; padding: 4px; }
QTableWidget::item:selected { background-color: #c0c0c0; color: #000000; }
'''
    app.setStyleSheet(qss)
    editor = GeoJSONEditor()
    editor.show()
    sys.exit(app.exec_())