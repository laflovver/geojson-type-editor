import os
import json
import tempfile
from logic.mts_controller import MTSController

class GeoJSONManager:
    def __init__(self, cli_path=None, access_token=None, username=None, logger=None):
        self.geojson_data = None
        self.file_path = None
        self.route_name = None
        # Configure Mapbox Tiling Service integration if provided
        if cli_path and access_token and username:
            self.mts = MTSController(cli_path, access_token, username, logger=logger)
        else:
            self.mts = None

    def load(self, path):
        """Load GeoJSON data from a file."""
        self.file_path = path
        with open(path, encoding='utf-8') as f:
            self.geojson_data = json.load(f)
            # Convert route-response JSON (with 'routes') into GeoJSON FeatureCollection
            if isinstance(self.geojson_data, dict) and 'routes' in self.geojson_data:
                routes = self.geojson_data.get('routes') or []
                if routes:
                    route = routes[0]
                    coords = route.get('geometry', {}).get('coordinates', [])
                    # Use route properties (distance, duration, etc.) as feature properties
                    props = {k: v for k, v in route.items() if k not in ('geometry',)}
                    self.geojson_data = {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {"type": "LineString", "coordinates": coords},
                                "properties": props
                            }
                        ]
                    }
                    # Persist converted GeoJSON to a temp file and update file_path
                    tmp = tempfile.NamedTemporaryFile(prefix="geojson_conv_", suffix=".geojson", delete=False, mode="w", encoding="utf-8")
                    json.dump(self.geojson_data, tmp, ensure_ascii=False, indent=2)
                    tmp.flush()
                    tmp.close()
                    self.file_path = tmp.name

    def get_features_and_keys(self):
        """Return the list of features and property keys."""
        if self.geojson_data is None:
            raise ValueError("No GeoJSON loaded. Please load a file first.")
        features = self.geojson_data.get("features", [])
        keys = []
        if features:
            # Gather all unique property keys across features
            key_set = set()
            for feat in features:
                props = feat.get("properties", {})
                key_set.update(props.keys())
            keys = list(key_set)
        return features, keys

    def toggle_type(self, key_index, keys):
        """Toggle the data type of all values in the selected property column and return new type."""
        if self.geojson_data is None:
            raise ValueError("No GeoJSON loaded. Please load a file first.")
        if key_index < 0 or key_index >= len(keys):
            raise IndexError("Property index out of range.")
        key = keys[key_index]
        # Find first non-null value to determine target type
        orig_val = None
        for feat in self.geojson_data.get("features", []):
            val = feat.get("properties", {}).get(key)
            if val is not None:
                orig_val = val
                break
        if orig_val is None:
            raise ValueError(f"No values found for property '{key}'.")
        # Determine new type
        if isinstance(orig_val, (int, float)):
            new_type = "string"
        elif isinstance(orig_val, str):
            if orig_val.isdigit():
                new_type = "integer"
            else:
                try:
                    float(orig_val)
                    new_type = "float"
                except ValueError:
                    raise ValueError(f"Cannot convert value '{orig_val}' to number.")
        else:
            raise ValueError(f"Unsupported value type: {type(orig_val).__name__}")
        # Perform conversion for all features
        for feat in self.geojson_data.get("features", []):
            val = feat.get("properties", {}).get(key)
            if new_type == "string":
                # convert numbers to string
                if isinstance(val, (int, float)):
                    feat["properties"][key] = str(val)
            elif new_type == "integer":
                # convert numeric string to int
                if isinstance(val, str) and val.isdigit():
                    feat["properties"][key] = int(val)
            elif new_type == "float":
                # convert numeric string to float
                if isinstance(val, str):
                    try:
                        feat["properties"][key] = float(val)
                    except ValueError:
                        # leave unmodified if cannot parse
                        pass
        return new_type

    def extract_route(self):
        """Extract a route with start/end points into a new GeoJSON structure."""
        if self.geojson_data is None:
            raise ValueError("No GeoJSON loaded. Please load a file first.")
        # Assume input has LineString geometries in features
        coords = []
        for feat in self.geojson_data.get("features", []):
            geom = feat.get("geometry", {})
            if geom.get("type") == "LineString":
                coords.extend(geom.get("coordinates", []))
        if not coords:
            raise ValueError("No LineString features found to extract route.")
        # Build new GeoJSON: a single LineString feature and two Point features
        route_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": coords[0]},
                    "properties": {"role": "start"}
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": coords[-1]},
                    "properties": {"role": "end"}
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {"name": self.route_name or ""}
                }
            ]
        }
        self.geojson_data = route_geojson

    def save(self, target_path=None):
        """Save the current GeoJSON data to a file."""
        if self.geojson_data is None:
            raise ValueError("No GeoJSON loaded. Please load a file first.")
        # Determine output path
        if target_path:
            out_path = target_path
        else:
            out_path = self.get_default_filename()
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(self.geojson_data, f, ensure_ascii=False, indent=2)
        return out_path

    def get_default_filename(self):
        """Recommend a filename based on original and operations."""
        if self.file_path:
            base, _ = os.path.splitext(os.path.basename(self.file_path))
            suffix = self.route_name or "edited"
            return f"{base}_{suffix}.geojson"
        return "edited.geojson"

    def configure_mts(self, cli_path, access_token, username, logger=None):
        """Configure Mapbox Tiling Service integration."""
        self.mts = MTSController(cli_path, access_token, username, logger=logger)