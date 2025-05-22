import os
import json
from PySide6.QtCore import QSettings

class MTSManager:
    def __init__(self, logger=None):
        self.settings = QSettings("GeoJSONEditor", "MapboxMTS")
        self.logger = logger or print
        
    def get_settings(self):
        """Get all MTS settings."""
        return {
            'cli_path': self.settings.value("mts/cli_path", ""),
            'access_token': self.settings.value("mts/access_token", ""),
            'username': self.settings.value("mts/username", ""),
            'source_name': self.settings.value("mts/source_name", ""),
            'layer_name': self.settings.value("mts/layer_name", "")
        }

    def save_settings(self, settings):
        """Save MTS settings."""
        for key, value in settings.items():
            self.settings.setValue(f"mts/{key}", value)

    def update_recipe(self, username, source_name, layer_name):
        """Update the recipe file with current settings."""
        try:
            recipe_path = 'recipe.json'
            recipe = {
                "version": 1,
                "layers": {
                    layer_name: {
                        "source": f"mapbox://tileset-source/{username}/{source_name}-source",
                        "minzoom": 0,
                        "maxzoom": 14
                    }
                }
            }
            
            with open(recipe_path, 'w') as f:
                json.dump(recipe, f, ensure_ascii=False, indent=2)
            
            self.logger("Updated recipe JSON", "info")
            return True
        except Exception as e:
            self.logger(f"Error updating recipe: {e}", "error")
            return False

    def save_recipe(self, path):
        """Save the current recipe to a file."""
        try:
            settings = self.get_settings()
            recipe = {
                "version": 1,
                "layers": {
                    settings['layer_name']: {
                        "source": f"mapbox://tileset-source/{settings['username']}/{settings['source_name']}-source",
                        "minzoom": 0,
                        "maxzoom": 14
                    }
                }
            }
            
            with open(path, 'w') as f:
                json.dump(recipe, f, ensure_ascii=False, indent=2)
            
            self.logger(f"Saved recipe to {path}", "success")
            return True
        except Exception as e:
            self.logger(f"Error saving recipe: {e}", "error")
            return False
