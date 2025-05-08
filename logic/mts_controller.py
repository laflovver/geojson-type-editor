

from logic.mts_manager import MapboxTilingService
# logic/mts_controller.py
# ... existing imports ...
from logic.mts_manager import MapboxTilingService

class MTSController:
    def __init__(self, cli_path, access_token, username, log_callback=None):
        # Pass the log_callback to MapboxTilingService
        self.mts = MapboxTilingService(cli_path, access_token, username, log_callback=log_callback)

    def upload_source(self, tileset_name, file_path):
        return self.mts.upload_source(tileset_name, file_path)

    def create_tileset(self, identifier, recipe_path, name):
        return self.mts.create_tileset(identifier, recipe_path, name)

    def publish_tileset(self, identifier, status_callback=None, interval=30):
        return self.mts.publish_tileset(
            identifier, status_callback=status_callback, interval=interval
        )

    def get_status(self, identifier):
        return self.mts.get_status(identifier)

class MTSController:
    def __init__(self, cli_path, access_token, username, logger=None):
        self.mts = MapboxTilingService(cli_path, access_token, username, logger=logger)

    def upload_source(self, tileset_name, file_path):
        return self.mts.upload_source(tileset_name, file_path)

    def create_tileset(self, identifier, recipe_path, name):
        return self.mts.create_tileset(identifier, recipe_path, name)

    def publish_tileset(self, identifier, status_callback=None, interval=30):
        return self.mts.publish_tileset(
            identifier, status_callback=status_callback, interval=interval
        )

    def get_status(self, identifier):
        return self.mts.get_status(identifier)