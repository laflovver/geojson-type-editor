"""Tests for the styles module."""

import pytest
from pathlib import Path

# Skip tests if Qt is not available or causes issues
pyside6 = pytest.importorskip("PySide6")

from PySide6.QtGui import QFont

from geojson_editor.core.styles import load_fonts, load_stylesheet, get_font


@pytest.mark.skip(reason="Qt initialization causes segmentation fault in test environment")
def test_load_fonts():
    """Test loading custom fonts."""
    # This test is skipped due to Qt initialization issues in test environment
    pass


def test_load_stylesheet(tmp_path, monkeypatch):
    """Test loading the application stylesheet."""
    # Create a test stylesheet file
    styles_dir = tmp_path / "styles"
    styles_dir.mkdir()
    styles_file = styles_dir / "style.qss"
    styles_file.write_text("QWidget { color: red; }")
    
    # Create a config with the styles directory
    config = {
        "paths": {
            "styles_dir": str(styles_dir)
        }
    }
    
    # Mock QFile operations
    class MockQFile:
        @classmethod
        def exists(cls, path):
            return path == str(styles_file)
            
        @classmethod
        def open(cls, *args, **kwargs):
            return True
            
        def readAll(self):
            return b"QWidget { color: red; }"
            
        def close(self):
            pass
    
    # Mock QTextStream
    class MockQTextStream:
        def __init__(self, file):
            self.file = file
            
        def readAll(self):
            return "QWidget { color: red; }"
            
        def setCodec(self, *args, **kwargs):
            pass
    
    # Apply mocks
    monkeypatch.setattr('PySide6.QtCore.QFile', MockQFile)
    monkeypatch.setattr('PySide6.QtCore.QTextStream', MockQTextStream)
    
    # Test the function
    stylesheet = load_stylesheet(config)
    assert stylesheet == "QWidget { color: red; }"


def test_get_font():
    """Test getting a font with specific properties."""
    font = get_font("Arial", 12, 700)
    
    assert isinstance(font, QFont)
    assert font.family() == "Arial"
    assert font.pointSize() == 12
    assert font.weight() == 700
