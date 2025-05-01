# GeoJSON Type Editor

**GeoJSON Type Editor** is a minimalist desktop application built with Python and PyQt5 for visually inspecting and converting property types in GeoJSON files.

---

## ✨ Features

- **Load GeoJSON**: Open files with `.geojson` or `.json` extensions.
- **Spreadsheet‑style view**: Features appear as rows, keys as columns, with icons and background colors distinguishing numbers from strings.
- **Column selection**: Click a column header to select a property key for conversion.
- **Type toggling**: Switch all values in the selected column between numeric and string types with one click.
- **Visual feedback**:
  - Convertible columns stay highlighted in translucent blue.
  - Non-convertible columns flash translucent red and revert.
  - Clicking a cell outside the selected column flashes that cell red.
- **Smart save dialog**: Suggested filename defaults to `originalName_string.geojson` or `originalName_number.geojson` based on your last conversion.

---

## 🚀 Installation & Running

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/geojson-type-editor.git
   cd geojson-type-editor
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv        # or: python -m venv venv
   source venv/bin/activate    # macOS/Linux
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install PyQt5
   ```

4. **Run the app**
   ```bash
   python geojson_type_editor.py
   ```

---

## 📦 Packaging as a Double‑Click App

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller \
  --windowed \
  --name GeoJSONEditor \
  geojson_type_editor.py
```

- **macOS**: find `GeoJSONEditor.app` in `dist/`.
- **Windows**: find `GeoJSONEditor.exe` in `dist/GeoJSONEditor/`.
- Copy the `.app` or `.exe` to your Desktop to launch by double‑click.

### (Optional) Create a DMG on macOS

```bash
hdiutil create -volname "GeoJSONEditor" \
               -srcfolder dist/GeoJSONEditor.app \
               -ov -format UDZO GeoJSONEditor.dmg
```

---

## 📁 Project Structure

```text
geojson-type-editor/
├── geojson_type_editor.py   # Main application script
├── README.md                # Project documentation
├── LICENSE                  # MIT license
├── .gitignore               # Ignored files and directories
└── dist/                    # Bundled apps/executables (after PyInstaller)
```

---

## 🤝 Contributing & Issues

Please open an [issue](https://github.com/<your-username>/geojson-type-editor/issues) for bug reports or feature requests. Pull requests are welcome!

---

## 📄 License
This project is licensed under the [MIT License](LICENSE). 

