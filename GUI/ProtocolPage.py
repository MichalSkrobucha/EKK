import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QTextEdit, QGroupBox, QFrame, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt

from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TabView import TabView


class ProtocolPage(QWidget):
    """
    To jest strona dla konkretnego protokołu (np. BB84).
    Zawiera POZIOME zakładki (SIM, TABLE, GRAPH).
    """

    def __init__(self, protocol_name):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Poziome Zakładki u góry
        self.horiz_tabs = QTabWidget()
        self.horiz_tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Zakładki
        self.sim_view = SimulationView(protocol_name)
        self.horiz_tabs.addTab(self.sim_view, "SIM")
        self.tab_view = TabView()
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.analysis_view = AnalysisView(protocol_name)
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")

        layout.addWidget(self.horiz_tabs)
        self.setLayout(layout)