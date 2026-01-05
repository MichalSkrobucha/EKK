import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, QFrame
from PyQt6.QtCore import Qt

from GUI.components.SettingsPanel import SettingsPanel
from GUI.components.SimControllerPanel import SimControllerPanel


class SimulationView(QWidget):
    """
    To jest widok odpowiadający zakładce SIM
    Zawiera: Controls, Animation, Step Controller, Logs.
    """

    def __init__(self, protocol_name: str, sim_manager):
        super().__init__()
        self.protocol_name = protocol_name
        self.sim_manager = sim_manager

        # Główny Layout całego widoku SIM
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # GÓRNA CZĘŚĆ
        top_section = QHBoxLayout()

        # PANEL CONTROLS
        setting_layout = SettingsPanel(protocol_name, sim_manager)

        # ŚRODKOWY OBSZAR (ANIMATION + CONTROLLER)
        sim_layout = QVBoxLayout()

        # SIM ANIMATION
        self.animation_frame = QFrame()
        self.animation_frame.setStyleSheet("background-color: #000; border: 2px dashed #50fa7b;")
        anim_label = QLabel("SIM ANIMATION AREA", self.animation_frame)
        anim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anim_layout = QVBoxLayout(self.animation_frame)
        anim_layout.addWidget(anim_label)

        # STEP CONTROLLER
        controls_layout = SimControllerPanel(sim_manager)

        # Składanie środka
        sim_layout.addWidget(self.animation_frame, stretch=1)
        sim_layout.addWidget(controls_layout, stretch=0)

        # Dodanie lewego i środkowego panelu do górnej sekcji
        top_section.addWidget(setting_layout, stretch=0)
        top_section.addLayout(sim_layout, stretch=1)

        # DOLNA CZĘŚĆ (LOGS)
        logs_group = QGroupBox("LOGS")
        logs_layout = QVBoxLayout()
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setText(f"System initialized for {protocol_name}...\nWaiting for start...")
        logs_layout.addWidget(self.logs_text)
        logs_group.setLayout(logs_layout)

        # SKŁADANIE CAŁOŚCI
        main_layout.addLayout(top_section, stretch=3)
        main_layout.addWidget(logs_group, stretch=1)

        self.setLayout(main_layout)