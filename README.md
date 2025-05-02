# GeoJSON Blossom

**GeoJSON Blossom** is a minimalist desktop application built with Python and PyQt5 for visually inspecting, converting property types, and extracting routes with naming in GeoJSON files.

---

## ✨ Features

- **Load GeoJSON**: Open files with `.geojson` or `.json` extensions.
- **Route extraction and naming**: Extract routes from GeoJSON features and assign meaningful names.
- **Spreadsheet‑style view**: Features appear as rows, keys as columns, with icons and background colors distinguishing numbers from strings.
- **Column selection**: Click a column header to select a property key for conversion.
- **Type toggling**: Switch all values in the selected column between numeric and string types with one click.
- **Visual feedback**:
  - Convertible columns stay highlighted in translucent blue.
  - Non-convertible columns flash translucent red and revert.
  - Clicking a cell outside the selected column flashes that cell red.
- **Visual log panel**: Displays color-coded messages for actions and errors.
- **Smart save dialog**: Suggested filename defaults to `routeName_string.geojson` or `routeName_number.geojson` based on your last conversion and extracted route name.
- **Modern UI**: Redesigned interface with smooth animations and improved usability.
- **No in-app map**: Map view and style/token fields removed; external browser used for map visualization.

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
  --name GeoJSONBlossom \
  geojson_type_editor.py
```

- **macOS**: find `GeoJSONBlossom.app` in `dist/`.
- **Windows**: find `GeoJSONBlossom.exe` in `dist/GeoJSONBlossom/`.
- Copy the `.app` or `.exe` to your Desktop to launch by double‑click.

### (Optional) Create a DMG on macOS

```bash
hdiutil create -volname "GeoJSONBlossom" \
               -srcfolder dist/GeoJSONBlossom.app \
               -ov -format UDZO GeoJSONBlossom.dmg
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
