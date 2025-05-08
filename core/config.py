from dataclasses import dataclass
from typing import Optional
from PyQt5.QtCore import QSettings

class Config:
    """Application configuration manager."""
    
    def __init__(self):
        self._settings = QSettings("GeoJSONEditor", "MapboxMTS")
        
    @property
    def mts_cli_path(self) -> Optional[str]:
        return self._settings.value("mts/cli_path", "")
    
    @mts_cli_path.setter
    def mts_cli_path(self, value: str):
        self._settings.setValue("mts/cli_path", value)
    
    @property
    def mts_access_token(self) -> Optional[str]:
        return self._settings.value("mts/access_token", "")
    
    @mts_access_token.setter
    def mts_access_token(self, value: str):
        self._settings.setValue("mts/access_token", value)
    
    @property
    def mts_username(self) -> Optional[str]:
        return self._settings.value("mts/username", "")
    
    @mts_username.setter
    def mts_username(self, value: str):
        self._settings.setValue("mts/username", value)
