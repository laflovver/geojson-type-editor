# GeoJSON Type Editor

**GeoJSON Type Editor** is a lightweight desktop application written in Python and PyQt5 for inspecting and converting property types in GeoJSON files.

---

## ✨ Features

- **Load GeoJSON** files (`.geojson` or `.json`) from disk.  
- **Table view**: features as rows, property keys as columns, with icons and background cues for numbers vs. strings.  
- **Column selection**: click a header to pick a property key for conversion.  
- **Type toggling**: convert all values in a column between numeric and string types with one click.  
- **Intuitive highlighting**:  
  - A convertible column stays highlighted in translucent blue.  
  - Non-convertible columns flash translucent red and revert.  
  - Clicking a cell outside the selected column flashes it red.  
- **Smart save dialog**: default filename is `originalName_string.geojson` or `originalName_number.geojson` based on the last conversion.

---

## 🚀 Install & Run

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/geojson-type-editor.git
   cd geojson-type-editor

2. **Create & activate a virtual environment**
    ```python3 -m venv venv
    source venv/bin/activate     # macOS/Linux
    # venv\Scripts\activate      # Windows

3. **Install dependencies**
    ```pip install PyQt5

4. **Run the app**
    ```python geojson_type_editor.py

## 📦 Packaging a Double-Click App
**Using PyInstaller**
    ```pip install pyinstaller
    pyinstaller \
    --windowed \
  --name GeoJSONEditor \
    geojson_type_editor.py

 - On macOS, you’ll find GeoJSONEditor.app in dist/.
 - On Windows, you’ll find GeoJSONEditor.exe in dist/GeoJSONEditor.
 - Copy the .app or .exe to your Desktop to launch by double-click.

**(Optional) Create a DMG on macOS**
    ``` hdiutil create -volname "GeoJSONEditor" \
               -srcfolder dist/GeoJSONEditor.app \
               -ov -format UDZO GeoJSONEditor.dmg

## 📦 Packaging a Double-Click App
geojson-type-editor/
├── geojson_type_editor.py   # Main application script
├── README.md                # This documentation
├── LICENSE                  # MIT license
├── .gitignore               # Ignore build artifacts, venv, etc.
└── dist/                    # Bundled app or executables (after PyInstaller) 


## 🤝 Contributing & Issues

Please open Issues for bug reports or feature requests. Pull requests are very welcome!