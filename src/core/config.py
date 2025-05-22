from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import json

class Config:
    """Application configuration manager."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".geojson_editor"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self._config = {}
        else:
            self._config = {}
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        self._save_config()

@dataclass
class MTSConfig:
    """Mapbox Tiling Service configuration."""
    cli_path: str = ""
    access_token: str = ""
    username: str = ""
    
    def to_dict(self) -> dict:
        return {
            'cli_path': self.cli_path,
            'access_token': self.access_token,
            'username': self.username
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MTSConfig':
        return cls(
            cli_path=data.get('cli_path', ''),
            access_token=data.get('access_token', ''),
            username=data.get('username', '')
        )
