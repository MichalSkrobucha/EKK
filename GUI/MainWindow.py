import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QTabWidget

from GUI.MACPage import MACPage
from QKD_Algorithms.BB84.SimManagerBB84 import SimManagerBB84
from QKD_Algorithms.E91.SimManagerE91 import SimManagerE91
from QKD_Algorithms.SARG04.SimManagerSARG import SimManagerSARG
from ProtocolPage import ProtocolPage
from style import STYLESHEET, STYLESHEET_LIGHT


class MainWindow(QMainWindow):
    def __init__(self, parent=None, dark_theme=True):
        super().__init__(parent)

        # -- Layout --
        self.setWindowTitle("QKD Simulator")
        self.resize(1300, 900)
        if dark_theme:
            self.setStyleSheet(STYLESHEET)
        else:
            self.setStyleSheet(STYLESHEET_LIGHT)

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

        self.vertical_tabs.addTab(self.create_protocol_page("BB84"), "BB84")
        self.vertical_tabs.addTab(self.create_protocol_page("SARG04"), "SARG04")
        self.vertical_tabs.addTab(self.create_protocol_page("E91"), "E91")
        self.vertical_tabs.addTab(MACPage(), "MAC")

        main_layout.addWidget(self.vertical_tabs)

    def create_protocol_page(self, protocol_name):
        """Tworzy stronę protokołu dynamicznie w zależności od nazwy"""
        sim_manager = None

        if protocol_name == "BB84":
            sim_manager = SimManagerBB84()
        elif protocol_name == "E91":
            sim_manager = SimManagerE91()
        elif protocol_name == "SARG04":
            sim_manager = SimManagerSARG()

        if sim_manager:
            page = ProtocolPage(protocol_name, sim_manager)
            return page
        return None
