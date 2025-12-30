import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QTextEdit, QGroupBox, QFrame, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt


class TabView(QTabWidget):
    def __init__(self):
        super().__init__()

        self.result_table = QTableWidget(5, 5)  # Przykładowa tabela 5x5
        self.result_table.setStyleSheet("background-color: #282a36; gridline-color: #44475a;")
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setHorizontalHeaderLabels(["Bit", "Base", "Result", "Time", "Info"])