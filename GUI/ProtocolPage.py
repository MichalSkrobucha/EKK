import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThread
from PyQt6.QtCore import Qt

from SimWorker import SimWorker
from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView


class ProtocolPage(QWidget):
    """
    To jest strona dla konkretnego protokołu (np. BB84).
    Zawiera POZIOME zakładki (SIM, TABLE, GRAPH).
    """
    def __init__(self, protocol_name, sim_manager, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name

        # --- KONFIGURACJA WĄTKU ---
        self.sim_thread = QThread()
        self.worker = SimWorker(sim_manager)

        # Przenosimy Workera do wątku
        self.worker.moveToThread(self.sim_thread)
        # --- LAYOUT ---
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Poziome Zakładki u góry
        self.horiz_tabs = QTabWidget()
        self.horiz_tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Zakładki
        self.sim_view = SimulationView(protocol_name, parent=self)
        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        self.tab_view = TableView(parent=self)
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.analysis_view = AnalysisView(parent=self)
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")

        layout.addWidget(self.horiz_tabs)
        self.setLayout(layout)
