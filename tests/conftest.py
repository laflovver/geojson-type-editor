"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest

from geojson_editor.core.config import load_config


@pytest.fixture
def config():
    """Fixture providing application configuration."""
    return load_config()


@pytest.fixture(autouse=True)
def clean_environment():
    """Fixture to clean up environment variables before each test."""
    # Save original environment
    original_env = os.environ.copy()
    
    # Yield control to the test
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
