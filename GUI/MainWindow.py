import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QTabWidget

from QKD_Algorithms import BB84
from QKD_Algorithms import SARG04
from QKD_Algorithms import E91
from ProtocolPage import ProtocolPage
from style import STYLESHEET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QKD Simulator")
        self.resize(1300, 900)
        self.setStyleSheet(STYLESHEET)
        # SiM INIT
        self.bb84_sim = BB84.SimManager
        self.sarg_sim = SARG04.SimManager
        self.e91_sim = E91.SimManager

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
        self.vertical_tabs.addTab(ProtocolPage("BB84", self.bb84_sim), "BB84")
        self.vertical_tabs.addTab(ProtocolPage("SARG04", self.sarg_sim), "SARG04")
        self.vertical_tabs.addTab(ProtocolPage("E91", self.e91_sim), "E91")

        main_layout.addWidget(self.vertical_tabs)
