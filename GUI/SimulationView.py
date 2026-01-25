import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from GUI.components.SettingsPanel import SettingsPanel
from GUI.components.SimControllerPanel import SimControllerPanel


class SimulationView(QWidget):
    """
    To jest widok odpowiadający zakładce SIM
    Zawiera: Controls, Animation, Step Controller, Logs.
    """
    sig_forward_settings = pyqtSignal(str, object)

    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name

        # Główny Layout całego widoku SIM
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # GÓRNA CZĘŚĆ
        top_section = QHBoxLayout()

        # SETTINGS PANEL
        self.setting_layout = SettingsPanel(protocol_name, self)
        self.setting_layout.sig_setting_changed.connect(self.sig_forward_settings)

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
        self.controls_layout = SimControllerPanel(self)
        self.sig_play = self.controls_layout.sig_play
        self.sig_reset = self.controls_layout.sig_reset
        self.sig_next = self.controls_layout.sig_next
        self.sig_prev = self.controls_layout.sig_prev
        self.sig_skip = self.controls_layout.sig_skip
        self.sig_speed = self.controls_layout.sig_speed

        # Składanie środka
        sim_layout.addWidget(self.animation_frame, stretch=1)
        sim_layout.addWidget(self.controls_layout, stretch=0)

        # Dodanie lewego i środkowego panelu do górnej sekcji
        top_section.addWidget(self.setting_layout, stretch=0)
        top_section.addLayout(sim_layout, stretch=1)

        # DOLNA CZĘŚĆ (LOGS)
        logs_group = QGroupBox("LOGS")
        logs_layout = QVBoxLayout()
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setText(f"System initialized for {self.protocol_name}...\nWaiting for start...")
        logs_layout.addWidget(self.logs_text)
        logs_group.setLayout(logs_layout)

        # SKŁADANIE CAŁOŚCI
        main_layout.addLayout(top_section, stretch=3)
        main_layout.addWidget(logs_group, stretch=2)

        self.setLayout(main_layout)

    def update_logs(self, current_step: int, logs: list[str], clear_first: bool = False):
        """
        """
        # Krok --
        if clear_first:
            self.logs_text.clear()
        # Krok ++
        for line in logs:
            self.logs_text.append(line)

        sb = self.logs_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def sim_lock_settings(self, lock_settings: bool):
        if lock_settings:
            self.setting_layout.lock_settings()
        else:
            self.setting_layout.unlock_settings()

