import json
from typing import Optional, Dict, Any, List
from pathlib import Path

class GeoJSONManager:
    """Manager for GeoJSON data."""
    
    def __init__(self):
        self.raw_data: Optional[Dict[str, Any]] = None
        self.file_path: Optional[str] = None
        self.route_name: Optional[str] = None
    
    def load(self, path: str) -> None:
        """Load GeoJSON data from file."""
        self.file_path = path
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
    
    def get_features_and_keys(self) -> tuple[List[Dict[str, Any]], List[str]]:
        """Get features and property keys from GeoJSON."""
        if not self.raw_data:
            return [], []
            
        features = self.raw_data.get('features', [])
        if not features:
            return [], []
            
        # Get all unique property keys
        keys = set()
        for feature in features:
            props = feature.get('properties', {})
            keys.update(props.keys())
        
        return features, sorted(list(keys))
    
    def toggle_type(self, column_index: int, keys: List[str]) -> None:
        """Toggle data type in a specific column."""
        if not self.raw_data:
            return
            
        key = keys[column_index]
        features = self.raw_data.get('features', [])
        
        for feature in features:
            props = feature.get('properties', {})
            if key in props:
                value = props[key]
                if isinstance(value, str):
                    try:
                        props[key] = int(value)
                    except ValueError:
                        try:
                            props[key] = float(value)
                        except ValueError:
                            pass
                elif isinstance(value, (int, float)):
                    props[key] = str(value)
    
    def extract_route(self) -> None:
        """Extract route from GeoJSON data."""
        if not self.raw_data:
            raise ValueError("No GeoJSON data loaded")
            
        if not self.route_name:
            raise ValueError("Route name not specified")
            
        features = []
        for feature in self.raw_data.get('features', []):
            if feature.get('geometry', {}).get('type') == 'LineString':
                features.append(feature)
        
        if not features:
            raise ValueError("No route data found in GeoJSON")
            
        self.raw_data = {
            'type': 'FeatureCollection',
            'features': features
        }
    
    def get_default_filename(self) -> str:
        """Get default filename for saving."""
        if not self.file_path:
            return "untitled.geojson"
            
        return Path(self.file_path).stem + "_edited.geojson"
    
    def save(self, path: str) -> None:
        """Save GeoJSON data to file."""
        if not self.raw_data:
            raise ValueError("No GeoJSON data to save")
            
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.raw_data, f, ensure_ascii=False, indent=2)
