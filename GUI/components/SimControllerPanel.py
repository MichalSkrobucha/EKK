from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QPushButton, QLabel, QSlider, QVBoxLayout, QFormLayout
from PyQt6.QtCore import Qt, pyqtSignal
from GUI.style import COLORS
from GUI.components.media_button import create_media_btn, update_play_button_visuals


class SimControllerPanel(QWidget):
    # --- Signals ---
    sig_play = pyqtSignal()
    sig_reset = pyqtSignal()
    sig_next = pyqtSignal()
    sig_prev = pyqtSignal()
    sig_skip = pyqtSignal()
    sig_speed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False

        # --- Layout ---
        self.create_layout()

    def create_layout(self, min_val=10, max_val=500, default_val=100):
        self.min_val = min_val
        self.max_val = max_val

        # --- LAYOUT ---
        controller_frame = QFrame()
        controller_frame.setStyleSheet(f"background-color: {COLORS['bg_selected']}; border-radius: 5px;")
        controller_layout = QHBoxLayout(controller_frame)
        controller_layout.setContentsMargins(10, 2, 10, 2)
        controller_layout.addWidget(QLabel("Simulation speed: "))

        slider_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(min_val, max_val)
        self.speed_slider.setValue(default_val)
        self.speed_slider.setSingleStep(10)
        self.speed_slider.setPageStep(10)
        slider_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel(f"{default_val} %")
        slider_layout.addWidget(self.speed_label)
        self.speed_slider.valueChanged.connect(self.sig_speed.emit)
        self.speed_slider.valueChanged.connect(self.handle_speed_change)

        playback_layout = QHBoxLayout()
        self.btn_reset = create_media_btn('fa5s.redo', "Reset Simulation")
        self.btn_next = create_media_btn('fa5s.step-backward', "Step Back")
        self.btn_play = create_media_btn('fa5s.play', "Start", False)
        self.btn_prev = create_media_btn('fa5s.step-forward', "Next Step")
        self.btn_skip = create_media_btn('fa5s.fast-forward', "Skip to End")

        # Action
        self.btn_play.clicked.connect(self.on_play_clicked)
        self.btn_reset.clicked.connect(self.sig_reset.emit)
        self.btn_prev.clicked.connect(self.sig_prev.emit)
        self.btn_next.clicked.connect(self.sig_next.emit)
        self.btn_skip.clicked.connect(self.sig_skip.emit)

        # Dodawanie do layoutu
        playback_layout.addWidget(self.btn_reset)
        playback_layout.addWidget(self.btn_prev)
        playback_layout.addWidget(self.btn_play)
        playback_layout.addWidget(self.btn_next)
        playback_layout.addWidget(self.btn_skip)

        controller_layout.addLayout(slider_layout, stretch=3)
        controller_layout.addStretch(stretch=2)
        controller_layout.addLayout(playback_layout, stretch=3)
        controller_layout.addStretch(stretch=2)
        self.setLayout(controller_layout)

    def handle_speed_change(self, value, step=100):
        rounded_val = round(value / step) * step
        if self.speed_slider.value() != rounded_val:
            self.speed_slider.setValue(min(max(self.min_val, rounded_val), self.max_val))
            self.speed_label.setText(f"{rounded_val} %")

    def on_play_clicked(self):
        self.is_running = not self.is_running
        self.sig_play.emit()
        # Aktualizacja wyglądu
        update_play_button_visuals(self.btn_play, self.is_running)

    def on_reset_clicked(self):
        pass

