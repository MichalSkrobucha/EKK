from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThread, pyqtSignal

# Importuj swoje widoki
from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView
from SimLogsView import SimLogsView

# Importuj Managery
from DataManagers.TableManager import TableManager
from DataManagers.StatisticsManager import StatisticsManager
from QKD_Algorithms.Common.SimManager import SimManager
from Workers.SimWorker import SimWorker


class ProtocolPage(QWidget):
    sig_start_loop = pyqtSignal()

    def __init__(self, protocol_name, sim_manager: SimManager, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name

        self.sim_manager = sim_manager
        self.tableManager = TableManager()
        self.statsManager = StatisticsManager()

        self.sim_thread = QThread()
        self.worker = SimWorker(sim_manager)
        self.worker.moveToThread(self.sim_thread)

        # --- LAYOUT ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.horiz_tabs = QTabWidget()
        sim_manager_class = type(sim_manager)

        self.sim_view = SimulationView(protocol_name, parent=self)
        self.tab_view = TableView(protocol_name, parent=self)
        self.analysis_view = AnalysisView(protocol_name, sim_manager_class, parent=self)

        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")

        self.side_panel = SimLogsView(protocol_name, parent=self)

        main_layout.addWidget(self.horiz_tabs, stretch=7)
        main_layout.addWidget(self.side_panel, stretch=3)

        self.setLayout(main_layout)

        # --- SIGNALS ---
        self.side_panel.sig_play.connect(self.worker.handle_play_toggle)
        self.side_panel.sig_next.connect(self.worker.next_step_simulation)
        self.side_panel.sig_prev.connect(self.worker.prev_step_simulation)
        self.side_panel.sig_skip.connect(self.worker.skip_simulation)
        self.side_panel.sig_speed.connect(self.worker.set_speed)

        self.side_panel.sig_forward_reset.connect(self.reset_gui_state)
        self.side_panel.sig_forward_reset.connect(self.worker.reset_simulation)

        self.sim_view.sig_jump_request.connect(self.worker.jump_to_stage_offset)

        self.worker.sig_log_update.connect(self.side_panel.update_logs)
        self.worker.sig_log_update.connect(self.update_gui_by_step)

        self.worker.sig_lock_settings.connect(self.sim_view.sim_lock_settings)
        self.sim_view.sig_forward_settings.connect(sim_manager.update_setting)

        self.sim_thread.start()

    def closeEvent(self, event):
        self.worker.stop_simulation()
        self.sim_thread.quit()
        self.sim_thread.wait()
        event.accept()

    def reset_gui_state(self):
        """Przywraca GUI do stanu początkowego (puste)"""
        self.tableManager.clear()
        self.tab_view.update_table(self.tableManager.get_dataframe())
        self.sim_view.update_stats("Idle", 0, 0, 0, 0)

    def update_gui_by_step(self, step_idx, logs, clear_first):
        """Aktualizuje widoki na podstawie numeru kroku (step_idx)."""
        if step_idx < 0:
            self.reset_gui_state()
            return

        # Tabela
        self.tableManager.update_from_simulation(self.sim_manager, self.protocol_name)
        full_df = self.tableManager.get_dataframe()

        sim_end = getattr(self.sim_manager, 'sim_end', 0)
        if sim_end == 0: sim_end = getattr(self.sim_manager, 'n_photons', 10)

        if not full_df.empty:
            if step_idx < sim_end:
                slice_len = step_idx + 1
            else:
                slice_len = sim_end

            final_slice = min(slice_len, len(full_df))
            sliced_df = full_df.iloc[:final_slice]
            self.tab_view.update_table(sliced_df)
        else:
            self.tab_view.update_table(None)

        # Statystyki
        stats = self.statsManager.calculate_statistics(self.sim_manager, self.protocol_name, step_idx)
        self.sim_view.update_stats(
            stage=stats["stage"],
            total=stats["total_photons"],
            raw=stats["raw_key_len"],
            error=stats["error_count"],
            final=stats["final_key_len"]
        )