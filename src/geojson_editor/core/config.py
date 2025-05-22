"""Configuration handling for the GeoJSON Editor application."""

import os
from pathlib import Path
from typing import Dict, Any

from PySide6.QtCore import QSettings


def get_app_dir() -> Path:
    """Get the application directory."""
    return Path(__file__).parent.parent


def get_resources_dir() -> Path:
    """Get the resources directory."""
    return get_app_dir() / "resources"


def get_styles_dir() -> Path:
    """Get the styles directory."""
    return get_resources_dir() / "styles"


def get_fonts_dir() -> Path:
    """Get the fonts directory."""
    return get_resources_dir() / "fonts"


def get_icons_dir() -> Path:
    """Get the icons directory."""
    return get_resources_dir() / "icons"


def load_config() -> Dict[str, Any]:
    """Load the application configuration.
    
    Returns:
        Dict containing application configuration
    """
    return {
        "app_name": "GeoJSON Editor",
        "version": "0.1.0",
        "organization": "GeoJSONTypeEditor",
        "settings": QSettings("GeoJSONTypeEditor", "Settings"),
        "paths": {
            "app_dir": str(get_app_dir()),
            "resources_dir": str(get_resources_dir()),
            "styles_dir": str(get_styles_dir()),
            "fonts_dir": str(get_fonts_dir()),
            "icons_dir": str(get_icons_dir()),
        },
    }


def setup_environment(config: Dict[str, Any]) -> None:
    """Set up the application environment.
    
    Args:
        config: Application configuration
    """
    # Set up environment variables
    os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"
    
    # Load access token if available
    settings = config["settings"]
    access_token = settings.value("mts/access_token", "")
    if access_token:
        os.environ["MAPBOX_ACCESS_TOKEN"] = access_token


if __name__ == "__main__":
    # Test the configuration
    config = load_config()
    print("Configuration loaded:")
    for key, value in config.items():
        if key != "settings":  # Skip printing QSettings object
            print(f"{key}: {value}")
