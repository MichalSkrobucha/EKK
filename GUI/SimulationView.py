import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from GUI.components.SettingsPanel import SettingsPanel


class SimulationView(QWidget):
    sig_forward_settings = pyqtSignal(str, object)

    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout()

        self.setting_layout = SettingsPanel(protocol_name, self)
        self.setting_layout.sig_setting_changed.connect(self.sig_forward_settings)
        main_layout.addWidget(self.setting_layout)

        self.animation_frame = QFrame()
        self.animation_frame.setStyleSheet("background-color: #1e1e2e; border: 2px dashed #6272a4;")

        anim_label = QLabel("VISUALIZATION / ANIMATION AREA", self.animation_frame)
        anim_label.setStyleSheet("color: #f8f8f2; font-weight: bold;")
        anim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        anim_layout = QVBoxLayout(self.animation_frame)
        anim_layout.addWidget(anim_label)

        main_layout.addWidget(self.animation_frame, stretch=1)

        self.setLayout(main_layout)

    def sim_lock_settings(self, lock_settings: bool):
        if lock_settings:
            self.setting_layout.lock_settings()
        else:
            self.setting_layout.unlock_settings()
