import sys
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGridLayout, QFrame, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from style import COLORS


class StatCard(QFrame):
    """Pojedynczy kafelek ze statystyką"""

    def __init__(self, title, initial_value, suffix="", parent=None):
        super().__init__(parent)
        self.suffix = suffix
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_panel']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: {COLORS['secondary']}; font-size: 11px; font-weight: bold; border: none;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_value = QLabel(str(initial_value) + suffix)
        self.lbl_value.setStyleSheet(f"color: {COLORS['accent']}; font-size: 22px; font-weight: bold; border: none;")
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)

    def update_value(self, value):
        if isinstance(value, float):
            txt = f"{value:.2f}"
        else:
            txt = str(value)
        self.lbl_value.setText(txt + self.suffix)


class StatisticsView(QWidget):
    # Sygnał skoku do etapu (offset względem końca transmisji)
    sig_jump_to_stage = pyqtSignal(int)

    def __init__(self, protocol_name, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name

        # Dane wewnętrzne
        self.total_bits = 0
        self.match_bits = 0
        self.error_bits = 0
        self.final_key_len = 0

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. LEWA STRONA: KAFELKI KPI ---
        kpi_widget = QWidget()
        kpi_layout = QGridLayout(kpi_widget)
        kpi_layout.setSpacing(8)
        kpi_layout.setContentsMargins(0, 0, 5, 0)

        self.card_stage = StatCard("CURRENT STAGE", "Idle", "")
        self.card_total = StatCard("TOTAL PHOTONS", 0, "")
        self.card_raw = StatCard("RAW KEY LENGTH", 0, " bits")
        self.card_qber = StatCard("CURRENT QBER", 0.0, "%")
        self.card_final = StatCard("FINAL KEY LEN", 0, " bits")

        # Układ kafelków
        kpi_layout.addWidget(self.card_stage, 0, 0, 1, 2)
        kpi_layout.addWidget(self.card_total, 1, 0)
        kpi_layout.addWidget(self.card_raw, 1, 1)
        kpi_layout.addWidget(self.card_qber, 2, 0)
        kpi_layout.addWidget(self.card_final, 2, 1)

        # --- 2. PRAWA STRONA: WYKRES I PRZYCISKI ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)

        # A) Wykres (Góra)
        self.figure = Figure(figsize=(3.5, 2.5), dpi=100)
        self.figure.patch.set_facecolor(COLORS['bg_dark'])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        lbl_chart = QLabel("Efficiency Breakdown")
        lbl_chart.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: 12px;")

        right_layout.addWidget(lbl_chart)
        right_layout.addWidget(self.canvas, stretch=2)

        # B) Przyciski (Dół)
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_panel']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 6px;
            }}
        """)
        ctrl_layout = QVBoxLayout(ctrl_frame)
        ctrl_layout.setSpacing(5)
        ctrl_layout.setContentsMargins(5, 5, 5, 5)

        lbl_jump = QLabel("JUMP TO STAGE")
        lbl_jump.setStyleSheet(f"color: {COLORS['secondary']}; font-weight: bold; font-size: 10px; border: none;")
        lbl_jump.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ctrl_layout.addWidget(lbl_jump)

        btn_grid = QGridLayout()
        btn_grid.setSpacing(5)
        self._create_stage_buttons(btn_grid)
        ctrl_layout.addLayout(btn_grid)

        right_layout.addWidget(ctrl_frame, stretch=0)

        main_layout.addWidget(kpi_widget, stretch=4)
        main_layout.addWidget(right_widget, stretch=5)

        self.setLayout(main_layout)
        self.update_chart()

    def _create_stage_buttons(self, layout):
        stages = []
        if self.protocol_name == "BB84":
            stages = [
                ("End Transmission", 0),
                ("Basis Exchange", 1),
                ("Sifting", 2),
                ("Sampling (QBER)", 3),
                ("Prep. Error Corr.", 4),
                ("Run Error Corr.", 5),
                ("Privacy Amp.", 6)
            ]
        elif self.protocol_name == "SARG04":
            stages = [
                ("End Transmission", 0),
                ("Announce States", 1),
                ("Sift States", 2),
                ("Sampling (QBER)", 3),
                ("Prep. Error Corr.", 4),
                ("Run Error Corr.", 5),
                ("Privacy Amp.", 6)
            ]
        elif self.protocol_name == "E91":
            stages = [
                ("End Transmission", 0),
                ("CHSH Analysis", 1),
                ("Finalize (EC+PA)", 2)
            ]

        row, col = 0, 0
        for name, offset in stages:
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_dark']};
                    color: {COLORS['text']};
                    border: 1px solid {COLORS['secondary']};
                    padding: 4px;
                    border-radius: 3px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent']};
                    color: {COLORS['button_text']};
                    border: 1px solid {COLORS['accent']};
                }}
            """)
            btn.clicked.connect(lambda checked, o=offset: self.sig_jump_to_stage.emit(o))
            layout.addWidget(btn, row, col)
            col += 1
            if col > 1:  # Max 2 kolumny
                col = 0
                row += 1

    def update_stats(self, stage, total, raw_len, error_count, final_len):
        self.total_bits = total
        self.match_bits = raw_len
        self.error_bits = error_count
        self.final_key_len = final_len

        qber = 0.0
        if raw_len > 0:
            qber = (error_count / raw_len) * 100.0

        self.card_stage.update_value(stage)
        self.card_total.update_value(total)
        self.card_raw.update_value(raw_len)
        self.card_qber.update_value(qber)
        self.card_final.update_value(final_len)

        self.update_chart()

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        lost = max(0, self.total_bits - self.match_bits)
        valid = max(0, self.match_bits - self.error_bits)
        errors = self.error_bits

        sizes = [lost, valid, errors]
        colors = [COLORS['bg_selected'], COLORS['success'], COLORS['error']]

        labels = [f"Lost: {lost}", f"Good: {valid}", f"Error: {errors}"]

        if sum(sizes) == 0:
            sizes = [1]
            colors = [COLORS['bg_selected']]
            wedges, _ = ax.pie(sizes, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.4, edgecolor=COLORS['bg_dark']))
        else:
            wedges, texts, autotexts = ax.pie(
                sizes, colors=colors, startangle=90,
                autopct=lambda p: f'{p:.0f}%' if p > 5 else '',
                pctdistance=0.8,
                wedgeprops=dict(width=0.4, edgecolor=COLORS['bg_dark'])
            )
            for at in autotexts:
                at.set_color('white')
                at.set_fontsize(8)
                at.set_fontweight('bold')

            ax.legend(wedges, labels, loc="center", bbox_to_anchor=(0.5, -0.1),
                      ncol=3, frameon=False, labelcolor=COLORS['text'], fontsize=8)

        ax.text(0, 0, str(self.match_bits), ha='center', va='center',
                color=COLORS['text'], fontsize=12, fontweight='bold')

        self.figure.tight_layout()
        self.canvas.draw()