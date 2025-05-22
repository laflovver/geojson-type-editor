import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import QSettings, QDir
from editor import GeoJSONEditor

def load_fonts():
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    font_files = [
        'RobotoMono-VariableFont_wght.ttf',
        'RobotoMono-Italic-VariableFont_wght.ttf'
    ]
    
    for font_file in font_files:
        font_path = os.path.join(font_dir, font_file)
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load custom fonts
    load_fonts()
    
    # Set application font
    font = QFont('Roboto Mono')
    font.setPointSize(10)  # Slightly smaller default size
    app.setFont(font)
    # Apply global style sheet from qt_style.qss
    script_dir = os.path.dirname(os.path.realpath(__file__))
    qss_path = os.path.join(script_dir, "qt_style.qss")
    
    print(f"Loading styles from: {qss_path}")
    try:
        with open(qss_path, 'r') as f:
            style_sheet = f.read()
            app.setStyleSheet(style_sheet)
            print("Styles loaded successfully")
    except Exception as e:
        print(f"Error loading styles: {e}")
        print("Using default Qt styles")
    # Load stored access token into environment for Tilesets CLI
    settings = QSettings("GeoJSONEditor", "MapboxMTS")
    access_token = settings.value("mts/access_token", "")
    if access_token:
        os.environ["MAPBOX_ACCESS_TOKEN"] = access_token
    editor = GeoJSONEditor()
    editor.show()
    sys.exit(app.exec())