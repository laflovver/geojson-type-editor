"""Tests for the configuration module."""

import os
from pathlib import Path

import pytest

# Skip tests if Qt is not available or causes issues
pyside6 = pytest.importorskip("PySide6")

from geojson_editor.core.config import load_config, setup_environment


def test_load_config():
    """Test loading the application configuration."""
    config = load_config()
    
    # Check required keys exist
    assert "app_name" in config
    assert "version" in config
    assert "organization" in config
    assert "settings" in config
    assert "paths" in config
    
    # Check paths exist and are Path objects
    paths = config["paths"]
    for path_key, path_value in paths.items():
        assert isinstance(path_value, str) or isinstance(path_value, Path)


class MockSettings:
    def value(self, key, default=None):
        if key == "mts/access_token":
            return "test_token"
        return default

def test_setup_environment(monkeypatch):
    """Test setting up the application environment."""
    # Mock environment variables to avoid side effects
    env_vars = {}
    monkeypatch.setattr(os, 'environ', env_vars)
    
    # Create a minimal config with a mock settings object
    config = {
        "settings": MockSettings(),
        "paths": {}
    }
    
    setup_environment(config)
    
    # Check that QT_LOGGING_RULES is set
    assert "QT_LOGGING_RULES" in os.environ
    
    # Check that MAPBOX_ACCESS_TOKEN is set from config
    assert os.environ.get("MAPBOX_ACCESS_TOKEN") == "test_token"
