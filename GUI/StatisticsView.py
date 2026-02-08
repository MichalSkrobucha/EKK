import sys
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGridLayout, QFrame, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from style import COLORS


class StatCard(QFrame):
    """Pojedynczy kafelek ze statystyką (np. QBER: 0.5%)"""
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
        self.lbl_title.setStyleSheet(f"color: {COLORS['secondary']}; font-size: 12px; font-weight: bold; border: none;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_value = QLabel(str(initial_value) + suffix)
        self.lbl_value.setStyleSheet(f"color: {COLORS['accent']}; font-size: 24px; font-weight: bold; border: none;")
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
    def __init__(self, parent=None):
        super().__init__(parent)

        # Główne dane
        self.total_bits = 0
        self.match_bits = 0  # Raw Key (bazy zgodne)
        self.error_bits = 0  # Błędne bity w Raw Key
        self.final_key_len = 0

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(10)

        self.card_stage = StatCard("CURRENT STAGE", "Transmission", "")
        self.card_total = StatCard("TOTAL PHOTONS", 0, "")
        self.card_raw = StatCard("RAW KEY LENGTH", 0, " bits")
        self.card_qber = StatCard("CURRENT QBER", 0.0, "%")
        self.card_final = StatCard("FINAL KEY LEN", 0, " bits")

        kpi_layout.addWidget(self.card_stage, 0, 0, 1, 2)
        kpi_layout.addWidget(self.card_total, 1, 0)
        kpi_layout.addWidget(self.card_raw, 1, 1)
        kpi_layout.addWidget(self.card_qber, 2, 0)
        kpi_layout.addWidget(self.card_final, 2, 1)

        kpi_widget = QWidget()
        kpi_widget.setLayout(kpi_layout)

        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)

        self.figure = Figure(figsize=(3, 3), dpi=100)
        self.figure.patch.set_facecolor(COLORS['bg_dark'])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")

        plot_layout.addWidget(QLabel("<b>Efficiency Breakdown</b>"))
        plot_layout.addWidget(self.canvas)

        self.update_chart()

        main_layout.addWidget(kpi_widget, stretch=2)
        main_layout.addWidget(plot_widget, stretch=1)

        self.setLayout(main_layout)

    def update_stats(self, stage, total, raw_len, error_count, final_len):
        """Metoda wywoływana przez ProtocolPage przy każdym kroku"""
        self.total_bits = total
        self.match_bits = raw_len
        self.error_bits = error_count
        self.final_key_len = final_len

        # Obliczenie QBER
        qber = 0.0
        if raw_len > 0:
            qber = (error_count / raw_len) * 100.0

        # Aktualizacja kafelków
        self.card_stage.update_value(stage)
        self.card_total.update_value(total)
        self.card_raw.update_value(raw_len)
        self.card_qber.update_value(qber)
        self.card_final.update_value(final_len)

        self.update_chart()

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Dane do wykresu: [Lost/Discarded, Valid Raw Key, Errors]
        # Lost = Total - Raw
        lost = max(0, self.total_bits - self.match_bits)
        valid = max(0, self.match_bits - self.error_bits)
        errors = self.error_bits

        sizes = [lost, valid, errors]
        labels = ["Lost", "Good Key", "Errors"]
        colors = [COLORS['bg_selected'], COLORS['success'], COLORS['error']]

        if sum(sizes) == 0:
            sizes = [1]
            colors = [COLORS['bg_selected']]
            labels = [""]

        wedges, texts = ax.pie(sizes, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.3, edgecolor=COLORS['bg_dark']))

        # Stylizacja
        ax.text(0, 0, f"{self.match_bits}", ha='center', va='center', fontsize=12,
                color=COLORS['text'], fontweight='bold')

        self.canvas.draw()
