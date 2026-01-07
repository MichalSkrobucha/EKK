import sys
from PyQt6.QtWidgets import (QVBoxLayout, QTabWidget,QTableWidget)
from style import COLORS


class TableView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.result_table = QTableWidget(5, 5)
        self.result_table.setStyleSheet(f"background-color: {COLORS['bg_table']}; "
                                        f"gridline-color: {COLORS['gridline']};")
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setHorizontalHeaderLabels(["Bit", "Base", "Result", "Time", "Info"])
        layout.addWidget(self.result_table)
        self.setLayout(layout)

    def update_table(self, data):
        pass