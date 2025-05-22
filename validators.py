from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

class EnglishTextValidator(QRegularExpressionValidator):
    def __init__(self, parent=None):
        # Allow English letters, numbers, spaces, and common punctuation
        regex = QRegularExpression(r"^[A-Za-z0-9\s.,;:'\"()\[\]{}<>!?@#$%^&*+=-_/\\]*$")
        super().__init__(regex, parent)
