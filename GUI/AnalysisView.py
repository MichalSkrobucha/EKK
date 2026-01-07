import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QTextEdit, QGroupBox, QFrame, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt


class AnalysisView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Placeholder na Analizę'))
        self.setLayout(layout)
