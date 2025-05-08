


from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QGroupBox, QTableWidget, QTextEdit, QHBoxLayout, QFileDialog,
    QLabel, QMessageBox, QAbstractScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon


class MTSIntegrationDialog(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("MTS Integration")
        self.setMinimumSize(800, 600)

        self.settings = QSettings("GeoJSONEditor", "MapboxMTS")
        self.layout = QVBoxLayout(self)

        self._build_form()
        self._build_buttons()

    def _build_form(self):
        form_layout = QFormLayout()
        self.cli_path_edit = QLineEdit(self.settings.value("mts/cli_path", ""))
        self.token_edit = QLineEdit(self.settings.value("mts/access_token", ""))
        self.username_edit = QLineEdit(self.settings.value("mts/username", ""))
        self.source_name_edit = QLineEdit(self.settings.value("mts/source_name", ""))

        form_layout.addRow("Tilesets CLI Path:", self.cli_path_edit)
        form_layout.addRow("Access Token:", self.token_edit)
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Source Name:", self.source_name_edit)

        self.layout.addLayout(form_layout)

    def _build_buttons(self):
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Settings")
        self.deploy_btn = QPushButton("Deploy Tileset")
        self.publish_btn = QPushButton("Publish")

        self.save_btn.clicked.connect(self._save_settings)
        self.deploy_btn.clicked.connect(self._deploy_tileset)
        self.publish_btn.clicked.connect(self._publish_tileset)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.deploy_btn)
        button_layout.addWidget(self.publish_btn)

        self.layout.addLayout(button_layout)

    def _save_settings(self):
        self.settings.setValue("mts/cli_path", self.cli_path_edit.text())
        self.settings.setValue("mts/access_token", self.token_edit.text())
        self.settings.setValue("mts/username", self.username_edit.text())
        self.settings.setValue("mts/source_name", self.source_name_edit.text())

        self.manager.configure_mts(
            cli_path=self.cli_path_edit.text(),
            access_token=self.token_edit.text(),
            username=self.username_edit.text()
        )
        QMessageBox.information(self, "Saved", "MTS settings saved successfully.")

    def _deploy_tileset(self):
        QMessageBox.information(self, "Deploy", "Tileset deployment not implemented yet.")

    def _publish_tileset(self):
        QMessageBox.information(self, "Publish", "Tileset publishing not implemented yet.")