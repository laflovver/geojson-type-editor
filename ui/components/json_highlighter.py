# ui/components/json_highlighter.py
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import QRegExp

class JSONHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        fmt_string = QTextCharFormat()
        fmt_string.setForeground(QColor("#D16969"))
        self.rules.append((QRegExp('"(?:[^"\\\\]|\\\\.)*"'), fmt_string))

        fmt_number = QTextCharFormat()
        fmt_number.setForeground(QColor("#69D169"))
        self.rules.append((QRegExp("\\b[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?\\b"), fmt_number))

        fmt_keyword = QTextCharFormat()
        fmt_keyword.setForeground(QColor("#6970D1"))
        self.rules.append((QRegExp("\\b(true|false|null)\\b"), fmt_keyword))

        fmt_brace = QTextCharFormat()
        fmt_brace.setForeground(QColor("#CCCCCC"))
        for pattern in ["[{}\\[\\]]", "[:,]"]:
            self.rules.append((QRegExp(pattern), fmt_brace))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text, 0)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)