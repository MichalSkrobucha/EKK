from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QPushButton, QLabel, QSlider, QVBoxLayout, QFormLayout
from PyQt6.QtCore import Qt
from GUI.style import COLORS
from GUI.components.media_button import create_media_btn, update_play_button_visuals


class SimControllerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.is_paused = True
        min_val = 10
        max_val = 200
        default_val = 100

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
        self.speed_slider.valueChanged.connect(self.handle_speed_change)

        playback_layout = QHBoxLayout()
        self.reset = create_media_btn('fa5s.redo', "Reset Simulation")
        self.btn_step_back = create_media_btn('fa5s.step-backward', "Step Back")
        self.btn_play = create_media_btn('fa5s.play', "Start", False)
        self.btn_step = create_media_btn('fa5s.step-forward', "Next Step")
        self.btn_fast_forward = create_media_btn('fa5s.fast-forward', "End Simulation")

        self.btn_play.clicked.connect(self.on_play_clicked)

        # Dodawanie do layoutu
        playback_layout.addWidget(self.reset)
        playback_layout.addWidget(self.btn_step_back)
        playback_layout.addWidget(self.btn_play)
        playback_layout.addWidget(self.btn_step)
        playback_layout.addWidget(self.btn_fast_forward)

        controller_layout.addLayout(slider_layout, stretch=3)
        controller_layout.addStretch(stretch=2)
        controller_layout.addLayout(playback_layout, stretch=3)
        controller_layout.addStretch(stretch=2)
        self.setLayout(controller_layout)

    def handle_speed_change(self, value, step=10):
        rounded_val = round(value / step) * step
        if self.speed_slider.value() != rounded_val:
            self.speed_slider.setValue(rounded_val)
            self.speed_label.setText(f"{rounded_val} %")

    def on_play_clicked(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True
        # Aktualizacja wyglądu
        update_play_button_visuals(self.btn_play, self.is_paused)
