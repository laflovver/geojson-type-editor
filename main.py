import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings
from ui import GeoJSONEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont('Roboto Mono', 14))
    # Apply global style sheet from qt_style.qss
    script_dir = os.path.dirname(os.path.realpath(__file__))
    qss_path = os.path.join(script_dir, "qt_style.qss")
    try:
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass
    # Load stored access token into environment for Tilesets CLI
    settings = QSettings("GeoJSONEditor", "MapboxMTS")
    access_token = settings.value("mts/access_token", "")
    if access_token:
        os.environ["MAPBOX_ACCESS_TOKEN"] = access_token
    editor = GeoJSONEditor()
    editor.show()
    sys.exit(app.exec_())