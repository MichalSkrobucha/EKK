import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from GUI.components.SettingsPanel import SettingsPanel
from GUI.StatisticsView import StatisticsView  # <--- Import
from style import COLORS, STYLESHEET


class SimulationView(QWidget):
    sig_forward_settings = pyqtSignal(str, object)

    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout()
        # main_layout.setSpacing(0)
        # main_layout.setContentsMargins(0, 0, 0, 0)

        self.setting_layout = SettingsPanel(protocol_name, self)
        self.setting_layout.sig_setting_changed.connect(self.sig_forward_settings)
        main_layout.addWidget(self.setting_layout, stretch=0)

        self.stats_container = QFrame()
        self.stats_container.setStyleSheet(STYLESHEET)
        stats_layout = QVBoxLayout(self.stats_container)

        lbl = QLabel("LIVE SIMULATION METRICS")
        lbl.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; letter-spacing: 1px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(lbl, stretch=0)

        self.statistics_view = StatisticsView(self)
        stats_layout.addWidget(self.statistics_view, stretch=1)

        main_layout.addWidget(self.stats_container, stretch=1)

        self.setLayout(main_layout)

    def sim_lock_settings(self, lock_settings: bool):
        if lock_settings:
            self.setting_layout.lock_settings()
        else:
            self.setting_layout.unlock_settings()

    def update_stats(self, stage, total, raw, error, final):
        self.statistics_view.update_stats(stage, total, raw, error, final)