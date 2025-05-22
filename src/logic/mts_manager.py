import subprocess
import json
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from src.core.config import MTSConfig

class MTSManager:
    """Mapbox Tiling Service manager."""
    
    def __init__(self, config: MTSConfig):
        self.config = config
        self._validate_cli()
    
    def _validate_cli(self) -> None:
        """Validate that the Tilesets CLI is properly configured."""
        if not self.config.cli_path:
            raise ValueError("Tilesets CLI path is not configured")
            
        if not Path(self.config.cli_path).exists():
            raise ValueError(f"Tilesets CLI not found at: {self.config.cli_path}")
    
    def upload_source(self, source_id: str, geojson_path: str) -> str:
        """Upload a source to Mapbox."""
        cmd = [
            self.config.cli_path,
            "sources",
            "upload",
            source_id,
            geojson_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Upload failed: {result.stderr}")
            return result.stdout.strip()
        except Exception as e:
            raise Exception(f"Error uploading source: {e}")
    
    def create_tileset(self, tileset_id: str, recipe_path: str, name: str) -> str:
        """Create a tileset using a recipe."""
        cmd = [
            self.config.cli_path,
            "tilesets",
            "create",
            tileset_id,
            "--recipe",
            recipe_path,
            "--name",
            name
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Tileset creation failed: {result.stderr}")
            return result.stdout.strip()
        except Exception as e:
            raise Exception(f"Error creating tileset: {e}")
    
    def publish_tileset(self, tileset_id: str) -> str:
        """Publish a tileset."""
        cmd = [
            self.config.cli_path,
            "tilesets",
            "publish",
            tileset_id
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Publish failed: {result.stderr}")
            return result.stdout.strip()
        except Exception as e:
            raise Exception(f"Error publishing tileset: {e}")
    
    def validate_recipe(self, recipe: Dict[str, Any]) -> bool:
        """Validate a recipe configuration."""
        required_keys = ['version', 'layers']
        if not all(key in recipe for key in required_keys):
            return False
            
        for layer in recipe['layers'].values():
            required_layer_keys = ['source', 'minzoom', 'maxzoom', 'layer_name']
            if not all(key in layer for key in required_layer_keys):
                return False
        
        return True
