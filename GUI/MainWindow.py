import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QTextEdit, QGroupBox, QFrame, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from ProtocolPage import ProtocolPage


def load_stylesheet(filename: str) -> str:
    """Wczytuje style z zewnętrznego pliku qss"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku style.qss!")
        return ""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QKD Simulator")
        self.resize(1100, 700)
        self.setStyleSheet(load_stylesheet("style.qss"))

        # Główny widget centralny
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Główny layout: Pasek boczny + Reszta
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Główne pionowe zakładki protokołów
        self.vertical_tabs = QTabWidget()
        self.vertical_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.vertical_tabs.setMovable(False)

        # Dodawanie stron protokołów
        # Każda strona to osobna instancja ProtocolPage
        self.vertical_tabs.addTab(ProtocolPage("BB84"), "BB84")
        self.vertical_tabs.addTab(ProtocolPage("SARG04"), "SARG04")
        self.vertical_tabs.addTab(ProtocolPage("E91"), "E91")

        main_layout.addWidget(self.vertical_tabs)
