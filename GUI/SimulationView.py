import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QTextEdit, QGroupBox, QFrame, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt

class SimulationView(QWidget):
    """
    To jest widok odpowiadający Twojemu szkicowi 'SIM'.
    Zawiera: Controls, Animation, Result Table, Step Controller, Logs.
    """

    def __init__(self, protocol_name: str):
        super().__init__()

        # Główny Layout całego widoku SIM
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # GÓRNA CZĘŚĆ
        top_section = QHBoxLayout()

        # PANEL CONTROLS
        controls_group = QGroupBox(f"Controls ({protocol_name})")
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(QLabel("Alice"))
        controls_layout.addWidget(QLabel("Is Eve Present?"))
        controls_layout.addWidget(QPushButton("Toggle Eve"))
        controls_layout.addWidget(QLabel("Channel Config"))
        controls_layout.addWidget(QPushButton("Parametry"))
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        controls_group.setFixedWidth(200)
