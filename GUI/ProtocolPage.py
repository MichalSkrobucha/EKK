import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt

from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TabView import TabView


class ProtocolPage(QWidget):
    """
    To jest strona dla konkretnego protokołu (np. BB84).
    Zawiera POZIOME zakładki (SIM, TABLE, GRAPH).
    """

    def __init__(self, protocol_name, sim_manager):
        super().__init__()
        self.protocol_name = protocol_name
        self.sim_manager = sim_manager
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Poziome Zakładki u góry
        self.horiz_tabs = QTabWidget()
        self.horiz_tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Zakładki
        self.sim_view = SimulationView(protocol_name, sim_manager)
        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        self.tab_view = TabView(protocol_name, sim_manager)
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.analysis_view = AnalysisView(protocol_name, sim_manager)
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")

        layout.addWidget(self.horiz_tabs)
        self.setLayout(layout)
