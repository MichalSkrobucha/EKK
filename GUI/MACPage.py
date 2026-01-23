import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThread
from PyQt6.QtCore import Qt, pyqtSignal

from GUI.StatisticsView import StatisticsView
from SimWorker import SimWorker
from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView


class MACPage(QWidget):
    sig_start_loop = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
