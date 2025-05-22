# GeoJSON Editor

**GeoJSON Editor** is a modern desktop application built with Python and PySide6 for working with GeoJSON files. It provides a user-friendly interface for viewing, editing, and managing GeoJSON data with Mapbox Tilesets (MTS) integration.

---

## ✨ Features

- **Modern UI**: Clean, responsive interface built with PySide6
- **GeoJSON Support**: Load, view, and edit GeoJSON files
- **Mapbox Tilesets Integration**:
  - Configure and manage Mapbox Tilesets
  - Upload sources and create tilesets
  - Monitor job status and publish tilesets
- **Type Conversion**: Toggle between different data types for GeoJSON properties
- **Custom Styling**: Modern QSS-based theming
- **Cross-Platform**: Works on Windows, macOS, and Linux

---

## 🚀 Installation & Running

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Using pip (recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/laflovver/geojson-type-editor.git
   cd geojson-type-editor
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

4. **Run the application**
   ```bash
   python -m geojson_editor
   ```

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run tests**
   ```bash
   pytest
   ```

3. **Format code**
   ```bash
   black .
   isort .
   ```

---

## 📦 Packaging

### Building a standalone executable

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build the application**
   ```bash
   pyinstaller run.py --name GeoJSONEditor --windowed --onefile
   ```

3. **Find the executable**
   - On Windows: `dist/GeoJSONEditor.exe`
   - On macOS: `dist/GeoJSONEditor.app`
   - On Linux: `dist/GeoJSONEditor`

---

## 📁 Project Structure

```
geojson-type-editor/
├── src/
│   └── geojson_editor/      # Main package
│       ├── core/             # Core functionality
│       ├── ui/               # User interface components
│       ├── widgets/          # Custom widgets
│       ├── resources/        # Application resources
│       │   ├── fonts/        # Font files
│       │   ├── icons/        # Application icons
│       │   └── styles/       # QSS stylesheets
│       └── __init__.py       # Package initialization
├── tests/                    # Test files
├── run.py                    # Application entry point
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing & Issues

Please open an [issue](https://github.com/<your-username>/geojson-type-editor/issues) for bug reports or feature requests. Pull requests are welcome!

---

## 📄 License
This project is licensed under the [MIT License](LICENSE). 
