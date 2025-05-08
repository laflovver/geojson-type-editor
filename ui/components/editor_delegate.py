# ui/components/editor_delegate.py
from PyQt5.QtWidgets import QStyledItemDelegate

class EditorDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        editor.setAutoFillBackground(True)
        editor.setStyleSheet("background-color: white;")
        return editor