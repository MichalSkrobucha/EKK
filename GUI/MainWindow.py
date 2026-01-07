import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QTabWidget

from QKD_Algorithms.BB84.SimManager import SimManager as BB84Manager
from QKD_Algorithms.E91.SimManager import SimManager as E91Manager
from QKD_Algorithms.SARG04.SimManager import SimManager as SARG04Manager
from ProtocolPage import ProtocolPage
from style import STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # -- Layout --
        self.setWindowTitle("QKD Simulator")
        self.resize(1300, 900)
        self.setStyleSheet(STYLESHEET)

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
        self.vertical_tabs.addTab(self.create_protocol_page("BB84"), "BB84")
        self.vertical_tabs.addTab(self.create_protocol_page("SARG04"), "SARG04")
        self.vertical_tabs.addTab(self.create_protocol_page("E91"), "E91")

        main_layout.addWidget(self.vertical_tabs)

    def create_protocol_page(self, protocol_name):
        """Tworzy stronę protokołu dynamicznie w zależności od nazwy"""
        target_manager_class = None

        if protocol_name == "BB84":
            target_manager_class = BB84Manager
        elif protocol_name == "E91":
            target_manager_class = E91Manager
        elif protocol_name == "SARG04":
            target_manager_class = SARG04Manager

        if target_manager_class:
            page = ProtocolPage(protocol_name, target_manager_class)
            return page
        return None
