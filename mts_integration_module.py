import subprocess
import os
import threading
import time
from pathlib import Path
import re

class MapboxTilingService:
    """
    Integration with Mapbox Tiling Service CLI (tilesets).
    Provides methods to upload sources, create tilesets, publish and poll status.
    """
    def __init__(self, cli_path: str, access_token: str, username: str, logger=None):
        # self.cli_path = cli_path
        self.access_token = access_token
        self.username = username
        # Logger should be a callable that takes a string (e.g., UI log widget append)
        self.logger = logger or print

        # Determine CLI binary and working directory
        if os.path.isdir(cli_path):
            # If 'tilesets' binary exists in the directory, use it; otherwise assume 'tilesets' in PATH
            candidate = os.path.join(cli_path, 'tilesets')
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                self.cli_binary = candidate
            else:
                self.cli_binary = 'tilesets'
            self.cli_dir = cli_path
        else:
            self.cli_binary = cli_path
            self.cli_dir = os.path.dirname(cli_path)

    def upload_source(self, tileset_name: str, geojson_path: str):
        """
        Upload a GeoJSON source to Mapbox Tilesets.
        """
        cmd = [
            self.cli_binary, "upload-source",
            "--token", self.access_token,
            self.username, tileset_name, geojson_path
        ]
        env = os.environ.copy()
        env["MAPBOX_ACCESS_TOKEN"] = self.access_token
        return self._run_command(cmd, env)

    def create_tileset(self, identifier: str, recipe_path: str, name: str):
        """
        Create a new (empty) tileset with a given recipe file.
        identifier: <=32 chars, no username prefix
        name: human-readable title, <=64 chars
        """
        full_id = f"{self.username}.{identifier}"
        cmd = [
            self.cli_binary, "create",
            "--token", self.access_token,
            full_id,
            "--recipe", recipe_path,
            "--name", name
        ]
        env = os.environ.copy()
        env["MAPBOX_ACCESS_TOKEN"] = self.access_token
        return self._run_command(cmd, env)

    def publish_tileset(self, identifier: str, status_callback=None, interval: int = 30):
        """
        Publish an existing tileset and optionally poll its status.
        status_callback(status_str) called every `interval` seconds.
        """
        full_id = f"{self.username}.{identifier}"
        env = os.environ.copy()
        env["MAPBOX_ACCESS_TOKEN"] = self.access_token
        result = self._run_command([
            self.cli_binary, "publish",
            "--token", self.access_token,
            full_id
        ], env)
        # Extract Mapbox job ID from CLI output
        job_id = None
        match = re.search(r"tilesets job \S+ (\S+)", result)
        if match:
            job_id = match.group(1)
            self.logger(f"Detected job ID: {job_id}")
        # Poll job status if a callback and job_id are available
        if status_callback and job_id:
            thread = threading.Thread(
                target=self._poll_job_status,
                args=(full_id, job_id, status_callback, interval),
                daemon=True
            )
            thread.start()
        return result

    def get_status(self, identifier: str):
        """
        Get the current processing status of a tileset.
        Returns the raw CLI output (string).
        """
        full_id = f"{self.username}.{identifier}"
        env = os.environ.copy()
        env["MAPBOX_ACCESS_TOKEN"] = self.access_token
        return self._run_command([
            self.cli_binary, "status",
            "--token", self.access_token,
            full_id
        ], env)

    def _poll_status(self, full_id: str, callback, interval: int):
        while True:
            time.sleep(interval)
            status_output = self.get_status(full_id)
            callback(status_output)
            if "success" in status_output.lower():
                break

    def _poll_job_status(self, full_id: str, job_id: str, callback, interval: int):
        """
        Poll the status of a tileset job using `tilesets job` command.
        """
        while True:
            time.sleep(interval)
            cmd = [
                self.cli_binary, "job",
                full_id, job_id,
                "--token", self.access_token
            ]
            status_output = self._run_command(cmd)
            callback(status_output)
            if "success" in status_output.lower():
                break

    def _run_command(self, cmd: list, env: dict = None) -> str:
        """
        Execute a CLI command, capture stdout/stderr, log, and return output.
        """
        try:
            completed = subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, env=env, text=True, cwd=self.cli_dir)
            self.logger(completed.stdout)
            return completed.stdout
        except subprocess.CalledProcessError as err:
            self.logger(err.stdout)
            return err.stdout
