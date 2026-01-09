import qtawesome as qta
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QPushButton
from GUI.style import COLORS, MEDIA_BUTTON_SHEET


def create_media_btn(icon_name, tooltip="", noFocus=True):
    btn = QPushButton()
    btn.setIcon(qta.icon(icon_name, color=COLORS['icon_color'], color_active=COLORS['icon_active']))
    btn.setIconSize(QSize(20, 20))
    btn.setToolTip(tooltip)
    if noFocus:
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setStyleSheet(MEDIA_BUTTON_SHEET)
    btn.setFixedSize(32, 32)
    return btn


def update_play_button_visuals(btn_play, is_running):
    if is_running:
        btn_play.setIcon(qta.icon('fa5s.pause', color=COLORS['icon_active']))
        btn_play.setToolTip("Start Simulation")
    else:
        btn_play.setIcon(qta.icon('fa5s.play', color=COLORS['icon_color']))
        btn_play.setToolTip("Resume Simulation")
