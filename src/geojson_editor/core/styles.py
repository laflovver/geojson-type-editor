"""Style management for the GeoJSON Editor application."""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication


def load_fonts(config: Dict[str, Any]) -> None:
    """Load custom fonts for the application.
    
    Args:
        config: Application configuration containing font paths
    """
    fonts_dir = Path(config["paths"]["fonts_dir"])
    if not fonts_dir.exists():
        return

    for font_file in fonts_dir.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))


def load_stylesheet(config: Dict[str, Any]) -> str:
    """Load and process the application stylesheet.
    
    Args:
        config: Application configuration containing style paths
        
    Returns:
        str: The loaded stylesheet as a string, or empty string on error
    """
    styles_dir = Path(config["paths"]["styles_dir"])
    styles_file = styles_dir / "style.qss"
    
    if not styles_file.exists():
        print(f"Warning: Stylesheet not found at {styles_file}")
        return ""
    
    try:
        with open(styles_file, "r", encoding="utf-8") as f:
            stylesheet = f.read()
            
        # Replace any variables in the stylesheet
        stylesheet = stylesheet.replace(
            "{{resources_dir}}", 
            str(styles_dir.parent)
        )
        
        return stylesheet
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""


def get_font(
    font_family: str, 
    point_size: int = 10, 
    weight: int = 400
) -> QFont:
    """Get a QFont with the specified properties.
    
    Args:
        font_family: Name of the font family
        point_size: Font size in points
        weight: Font weight (400=normal, 700=bold)
        
    Returns:
        QFont: Configured font object
    """
    font = QFont(font_family, point_size, weight)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    return font


def set_default_font(config: Dict[str, Any]) -> None:
    """Set the default font for the application.
    
    Args:
        config: Application configuration
    """
    font = get_font('Roboto Mono')
    QApplication.instance().setFont(font)
