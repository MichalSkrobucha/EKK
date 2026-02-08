import sys
import matplotlib

matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QComboBox, QGroupBox,
                             QProgressBar, QSplitter, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from DataManagers.AnalysisManager import AnalysisManager
from Workers.AnalysisWorker import AnalysisWorker
from style import COLORS


class AnalysisView(QWidget):
    sig_start_eve = pyqtSignal(int, int)
    sig_start_sweep = pyqtSignal(int, str, list, str, list, int)

    def __init__(self, protocol_name, sim_manager_cls, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        self.sim_manager_cls = sim_manager_cls
        self.manager = AnalysisManager()
        self.init_ui()
        self.setup_worker()

    def setup_worker(self):
        self.sim_thread = QThread()
        self.worker = AnalysisWorker(self.sim_manager_cls, self.protocol_name)
        self.worker.moveToThread(self.sim_thread)

        self.sim_thread.started.connect(self.execute_worker_task)
        self.worker.sig_finished.connect(self.on_worker_finished)
        self.worker.sig_progress.connect(self.update_progress)
        self.worker.sig_log.connect(self.lbl_status.setText)
        self.worker.sig_result_eve.connect(self.plot_eve_results)
        self.worker.sig_result_heatmap.connect(self.plot_heatmap_results)

        self.sig_start_eve.connect(self.worker.run_eve_analysis)
        self.sig_start_sweep.connect(self.worker.run_parameter_sweep)

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # --- CONTROLS ---
        controls_widget = QWidget()
        ctrl_layout = QVBoxLayout(controls_widget)

        ctrl_layout.addWidget(QLabel("<b>Analysis Type:</b>"))
        self.combo_mode = QComboBox()
        # Dodajemy nowe tryby analizy
        self.combo_mode.addItems([
            "Eve Presence Check",
            "Dampening vs Distance",
            "Base Transform vs Distance",
            "Bob Error vs Efficiency"
        ])
        self.combo_mode.currentIndexChanged.connect(self.update_ui_mode)
        ctrl_layout.addWidget(self.combo_mode)

        self.group_params = QGroupBox("Configuration")
        self.params_layout = QVBoxLayout()
        self.group_params.setLayout(self.params_layout)
        ctrl_layout.addWidget(self.group_params)

        self.create_input_widgets()

        self.btn_run = QPushButton("START ANALYSIS")
        self.btn_run.clicked.connect(self.start_analysis)
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.clicked.connect(self.stop_analysis)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet(f"background-color: {COLORS['error']}; color: {COLORS['text']}")

        self.progress = QProgressBar()
        self.lbl_status = QLabel("Ready.")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(f"color: {COLORS['secondary']}; font-style: italic;")

        ctrl_layout.addWidget(self.btn_run)
        ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addWidget(self.progress)
        ctrl_layout.addWidget(self.lbl_status)
        ctrl_layout.addStretch()

        # --- PLOT ---
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor(COLORS['bg_dark'])
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: transparent; border: none;")
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(controls_widget)
        splitter.addWidget(plot_widget)
        splitter.setStretchFactor(1, 4)
        main_layout.addWidget(splitter)

        self.update_ui_mode()

    def create_input_widgets(self):
        # Bits
        self.n_bits = QWidget()
        l_bits = QVBoxLayout(self.n_bits)
        l_bits.setContentsMargins(0, 0, 0, 0)
        l_bits.addWidget(QLabel("Key length (Bits):"))
        self.spin_bits = QSpinBox()
        self.spin_bits.setRange(5, 100000)
        self.spin_bits.setValue(100)
        l_bits.addWidget(self.spin_bits)

        # ---  Eve Inputs ---
        self.wid_eve = QWidget()
        l_eve = QVBoxLayout(self.wid_eve)
        l_eve.setContentsMargins(0, 0, 0, 0)
        l_eve.addWidget(QLabel("Trials (N):"))
        self.spin_trials = QSpinBox()
        self.spin_trials.setRange(1, 5000)
        self.spin_trials.setValue(10)
        l_eve.addWidget(self.spin_trials)

        # --- Shared Heatmap Inputs (Dampening, Base, Error, Efficiency, Distance) ---
        self.wid_heatmap = QWidget()
        l_hm = QVBoxLayout(self.wid_heatmap)
        l_hm.setContentsMargins(0, 0, 0, 0)

        self.lbl_param_y = QLabel("Param Y:")
        self.input_y = QLineEdit()
        l_hm.addWidget(self.lbl_param_y)
        l_hm.addWidget(self.input_y)

        self.lbl_param_x = QLabel("Param X:")
        self.input_x = QLineEdit()
        l_hm.addWidget(self.lbl_param_x)
        l_hm.addWidget(self.input_x)

        l_hm.addWidget(QLabel("Avg per point (N):"))
        self.spin_avg = QSpinBox()
        self.spin_avg.setRange(1, 100)
        self.spin_avg.setValue(5)
        l_hm.addWidget(self.spin_avg)

        self.params_layout.addWidget(self.n_bits)
        self.params_layout.addWidget(self.wid_eve)
        self.params_layout.addWidget(self.wid_heatmap)

    def update_ui_mode(self):
        idx = self.combo_mode.currentIndex()

        if idx == 0:
            self.wid_eve.setVisible(True)
            self.wid_heatmap.setVisible(False)

        else:
            self.wid_eve.setVisible(False)
            self.wid_heatmap.setVisible(True)

            if idx == 1:  # Dampening vs Distance
                self.lbl_param_y.setText("Dampening [dB/km]:")
                self.input_y.setText("0.0, 0.1, 0.2, 0.5")
                self.lbl_param_x.setText("Distance [km]:")
                self.input_x.setText("10, 20, 50, 80, 100")

            elif idx == 2:  # Base Transform vs Distance
                self.lbl_param_y.setText("Base Transform Probability:")
                self.input_y.setText("0.0, 0.05, 0.1, 0.2")
                self.lbl_param_x.setText("Distance [km]:")
                self.input_x.setText("10, 20, 50, 80")

            elif idx == 3:  # Bob Error vs Efficiency
                self.lbl_param_y.setText("Bob Error (Internal):")
                self.input_y.setText("0.0, 0.01, 0.05, 0.1")
                self.lbl_param_x.setText("Bob Efficiency:")
                self.input_x.setText("0.1, 0.5, 0.8, 1.0")

    def parse_list_input(self, text: str) -> list:
        try:
            parts = text.split(',')
            values = [float(p.strip()) for p in parts if p.strip()]
            return sorted(values)  # Sortujemy dla porządku na wykresie
        except ValueError:
            return []

    def start_analysis(self):
        idx = self.combo_mode.currentIndex()

        if idx > 0:  # Heatmap modes
            y_vals = self.parse_list_input(self.input_y.text())
            x_vals = self.parse_list_input(self.input_x.text())

            if not y_vals or not x_vals:
                QMessageBox.warning(self, "Input Error", "Please enter valid comma-separated numbers.")
                return

            self._temp_params = {
                'y_vals': y_vals,
                'x_vals': x_vals,
                'n_avg': self.spin_avg.value()
            }

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.figure.clear()
        self.figure.patch.set_facecolor(COLORS['bg_dark'])
        self.canvas.draw()
        self.progress.setValue(0)

        if not self.sim_thread.isRunning():
            self.sim_thread.start()

    def execute_worker_task(self):
        """Mapowanie wybranego trybu na parametry Workera"""
        mode = self.combo_mode.currentIndex()

        if mode == 0:  # Eve
            self.sig_start_eve.emit(self.spin_bits.value(), self.spin_trials.value())

        elif mode == 1:  # Dampening vs Distance
            self.sig_start_sweep.emit(
                self.spin_bits.value(),
                "dumpening_per_km",
                self._temp_params['y_vals'],
                "channelLength",
                self._temp_params['x_vals'],
                self._temp_params['n_avg']
            )

        elif mode == 2:  # Base Transform vs Distance
            self.sig_start_sweep.emit(
                self.spin_bits.value(),
                "base_transform_per_km",
                self._temp_params['y_vals'],
                "channelLength",  # X
                self._temp_params['x_vals'],
                self._temp_params['n_avg']
            )

        elif mode == 3:  # Bob Error vs Efficiency
            self.sig_start_sweep.emit(
                self.spin_bits.value(),
                "bob.error",
                self._temp_params['y_vals'],
                "bob.efficiency",
                self._temp_params['x_vals'],
                self._temp_params['n_avg']
            )

    def stop_analysis(self):
        self.worker.stop()
        self.lbl_status.setText("Stopping...")

    def on_worker_finished(self):
        self.sim_thread.quit()
        self.sim_thread.wait()
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText("Analysis Finished.")

    def update_progress(self, current, total):
        if total > 0:
            val = int((current / total) * 100)
            self.progress.setValue(val)

    # --- PLOTTING ---
    def plot_eve_results(self, df):
        self.manager.set_eve_data(df)
        ax = self.figure.add_subplot(111)
        sns.scatterplot(data=df, x="Trial", y="QBER", hue="Scenario", style="Scenario", ax=ax, s=80, palette="deep")
        sns.lineplot(data=df, x="Trial", y="QBER", hue="Scenario", ax=ax, alpha=0.3, legend=False, palette="deep")
        self._style_plot(ax, "QBER Analysis: Eve Presence")
        self.canvas.draw()

    def plot_heatmap_results(self, df, xlabel, ylabel):
        self.manager.set_heatmap_data(df)
        ax = self.figure.add_subplot(111)

        sns.heatmap(df, annot=True, fmt=".3f", cmap="mako", ax=ax, cbar_kws={'label': 'QBER'})
        ax.invert_yaxis()

        ax.set_xlabel(self._beautify_label(xlabel))
        ax.set_ylabel(self._beautify_label(ylabel))

        self._style_plot(ax, f"QBER Heatmap: {self._beautify_label(ylabel)} vs {self._beautify_label(xlabel)}")

        if ax.collections:
            cbar = ax.collections[0].colorbar
            cbar.ax.yaxis.set_tick_params(color=COLORS['text'])
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=COLORS['text'])
            cbar.set_label('QBER', color=COLORS['text'])

        self.canvas.draw()

    def _beautify_label(self, label):
        mapping = {
            "channelLength": "Distance [km]",
            "dumpening_per_km": "Dampening [dB/km]",
            "base_transform_per_km": "Base Transform Prob.",
            "bob.error": "Bob Internal Error",
            "bob.efficiency": "Bob Efficiency"
        }
        return mapping.get(label, label)

    def _style_plot(self, ax, title):
        ax.set_title(title, color=COLORS['text'], pad=20, fontweight='bold')
        ax.grid(True, color=COLORS['gridline'], alpha=0.3)
        ax.set_facecolor(COLORS['bg_dark'])
        ax.tick_params(colors=COLORS['text'], which='both')
        ax.xaxis.label.set_color(COLORS['text'])
        ax.yaxis.label.set_color(COLORS['text'])
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS['secondary'])
        legend = ax.get_legend()
        if legend:
            frame = legend.get_frame()
            frame.set_facecolor(COLORS['bg_panel'])
            frame.set_edgecolor(COLORS['secondary'])
            for text in legend.get_texts():
                text.set_color(COLORS['text'])