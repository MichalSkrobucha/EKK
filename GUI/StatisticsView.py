import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, QFrame
from PyQt6.QtCore import Qt


class StatisticsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Statistics"))
        self.setLayout(layout)
