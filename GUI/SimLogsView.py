from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from GUI.components.SimControllerPanel import SimControllerPanel


class SimLogsView(QWidget):
    sig_forward_reset = pyqtSignal()

    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name

        self.layout = QVBoxLayout()

        # STEP CONTROLLER
        self.controls_panel = SimControllerPanel(self)

        # Przekazywanie sygnałów
        self.sig_play = self.controls_panel.sig_play
        self.sig_reset = self.controls_panel.sig_reset
        self.sig_next = self.controls_panel.sig_next
        self.sig_prev = self.controls_panel.sig_prev
        self.sig_skip = self.controls_panel.sig_skip
        self.sig_speed = self.controls_panel.sig_speed

        self.controls_panel.sig_reset.connect(self.sim_reset)

        # DOLNA CZĘŚĆ (LOGS)
        logs_group = QGroupBox("LOGS")
        logs_layout = QVBoxLayout()
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setText(f"System initialized for {self.protocol_name}...\nWaiting for start...")
        logs_layout.addWidget(self.logs_text)
        logs_group.setLayout(logs_layout)

        self.layout.addWidget(self.controls_panel)
        self.layout.addWidget(logs_group)

        self.setLayout(self.layout)

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

    def sim_reset(self):
        self.logs_text.clear()
        self.logs_text.setText(f"System initialized for {self.protocol_name}...\nWaiting for start...")
        self.sig_forward_reset.emit()