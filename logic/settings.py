from PyQt5.QtCore import QSettings

class SettingsManager:
    def __init__(self):
        self.settings = QSettings("GeoJSONEditor", "MapboxMTS")

    def load(self):
        return {
            "cli_path": self.settings.value("mts/cli_path", ""),
            "access_token": self.settings.value("mts/access_token", ""),
            "username": self.settings.value("mts/username", ""),
            "source_name": self.settings.value("mts/source_name", "")
        }

    def save(self, **kwargs):
        for key, value in kwargs.items():
            self.settings.setValue(f"mts/{key}", value)