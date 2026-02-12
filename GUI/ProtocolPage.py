from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThread, pyqtSignal, QTimer

from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView
from SimLogsView import SimLogsView

from QKD_Algorithms.Common.SimManager import SimManager
from Workers.SimWorker import SimWorker
from Workers.GuiDataWorker import GuiDataWorker


class ProtocolPage(QWidget):
    sig_start_loop = pyqtSignal()
    sig_request_data_processing = pyqtSignal(int, list)

    def __init__(self, protocol_name, sim_manager: SimManager, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        self.sim_manager = sim_manager

        self._pending_step_idx = -1
        self._pending_logs = []
        self._is_data_processing = False

        self.sim_thread = QThread()
        self.worker = SimWorker(sim_manager)
        self.worker.moveToThread(self.sim_thread)

        self.data_thread = QThread()
        self.data_worker = GuiDataWorker(sim_manager, protocol_name)
        self.data_worker.moveToThread(self.data_thread)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.horiz_tabs = QTabWidget()
        sim_manager_class = type(sim_manager)

        self.sim_view = SimulationView(protocol_name, parent=self)
        self.tab_view = TableView(protocol_name, parent=self)
        self.analysis_view = AnalysisView(protocol_name, sim_manager_class, parent=self)

        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        if protocol_name != "MAC":
            self.horiz_tabs.addTab(self.tab_view, "TABLE")
        if protocol_name not in ["MAC", "E91"]:
            self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")

        self.side_panel = SimLogsView(protocol_name, parent=self)

        main_layout.addWidget(self.horiz_tabs, stretch=7)
        main_layout.addWidget(self.side_panel, stretch=3)

        self.setLayout(main_layout)

        self.side_panel.sig_play.connect(self.worker.handle_play_toggle)
        self.side_panel.sig_next.connect(self.worker.next_step_simulation)
        self.side_panel.sig_prev.connect(self.worker.prev_step_simulation)
        self.side_panel.sig_skip.connect(self.worker.skip_simulation)
        self.side_panel.sig_speed.connect(self.worker.set_speed)

        self.side_panel.sig_forward_reset.connect(self.reset_gui_state)
        self.side_panel.sig_forward_reset.connect(self.worker.reset_simulation)

        self.sim_view.sig_jump_request.connect(self.worker.jump_to_stage_offset)

        self.worker.sig_log_update.connect(self.on_sim_step_finished)

        self.sig_request_data_processing.connect(self.data_worker.process_data)
        self.data_worker.sig_data_ready.connect(self.apply_gui_updates)

        self.worker.sig_lock_settings.connect(self.sim_view.sim_lock_settings)
        self.sim_view.sig_forward_settings.connect(sim_manager.update_setting)

        self.gui_refresh_timer = QTimer()
        self.gui_refresh_timer.setInterval(0)
        self.gui_refresh_timer.timeout.connect(self.trigger_data_processing)
        self.gui_refresh_timer.start()

        self.sim_thread.start()
        self.data_thread.start()

    def closeEvent(self, event):
        self.gui_refresh_timer.stop()
        self.worker.stop_simulation()
        self.sim_thread.quit()
        self.sim_thread.wait()
        self.data_thread.quit()
        self.data_thread.wait()
        event.accept()

    def reset_gui_state(self):
        self._pending_step_idx = -1
        self._pending_logs = []

        self.tab_view.update_table(None)
        self.sim_view.update_stats("Idle", 0, 0, 0, 0)
        self.side_panel.update_logs(-1, [], True)

    def on_sim_step_finished(self, step_idx, logs, clear_first):
        if clear_first:
            self.reset_gui_state()
            self._pending_step_idx = step_idx
            self._pending_logs = logs
            self.side_panel.update_logs(step_idx, logs, True)
        else:
            self._pending_step_idx = step_idx
            self._pending_logs = logs

    def trigger_data_processing(self):
        if self._is_data_processing:
            return

        if self._pending_step_idx < 0:
            return

        self._is_data_processing = True
        self.sig_request_data_processing.emit(self._pending_step_idx, self._pending_logs)

    def apply_gui_updates(self, df, stats, step_idx, logs):
        self.tab_view.update_table(df)

        self.sim_view.update_stats(
            stage=stats["stage"],
            total=stats["total_photons"],
            raw=stats["raw_key_len"],
            error=stats["error_count"],
            final=stats["final_key_len"]
        )

        if logs:
            self.side_panel.update_logs(step_idx, logs, False)

        self._is_data_processing = False
