from typing import List, Dict
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

def build_recipe_from_table(table: QTableWidget) -> Dict:
    layers = {}
    for i in range(table.rowCount()):
        source = table.item(i, 0).text()
        minzoom = int(table.item(i, 1).text())
        maxzoom = int(table.item(i, 2).text())
        layer_name = table.item(i, 3).text()
        fill_item = table.item(i, 4)
        spec = {"source": source, "minzoom": minzoom, "maxzoom": maxzoom}
        if fill_item and fill_item.text().strip():
            spec["fillzoom"] = int(fill_item.text())
        inc_item = table.item(i, 5)
        if inc_item and inc_item.text().strip().lower() == "true":
            spec["incremental"] = True
        else:
            spec["incremental"] = False
        layers[layer_name] = spec
    return {"version": 1, "layers": layers}

def populate_table_from_features(table: QTableWidget, features: List[dict], keys: List[str]) -> None:
    table.clear()
    table.setColumnCount(len(keys))
    table.setRowCount(len(features))
    table.setHorizontalHeaderLabels(keys)
    for i, feat in enumerate(features):
        props = feat.get("properties", {})
        for j, key in enumerate(keys):
            val = props.get(key, "")
            item = QTableWidgetItem(str(val))
            table.setItem(i, j, item)
    table.setVisible(True)