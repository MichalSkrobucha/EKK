from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal


class MACPage(QWidget):
    sig_start_loop = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
