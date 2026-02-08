from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt6.QtCore import QThread, pyqtSignal

from GUI.Workers.SimWorker import SimWorker
from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView
from SimLogsView import SimLogsView
from DataManagers.TableManager import TableManager
from Misc.SmartList import SmartList
from QKD_Algorithms.Common.SimManager import SimManager


class ProtocolPage(QWidget):
    sig_start_loop = pyqtSignal()

    def __init__(self, protocol_name, sim_manager: SimManager, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        self.tableManager = TableManager()
        self.sim_manager = sim_manager

        # --- LOCAL COUNTERS FOR STATISTICS ---
        self.stats_total_photons = 0
        self.stats_raw_len = 0
        self.stats_error_count = 0
        self.stats_stage = "Transmission"

        # --- Observable Lists ---
        if protocol_name == "BB84":
            self.sim_manager.alice.bases = SmartList(self.on_list_update, "Alice", "bases")
            self.sim_manager.alice.bits = SmartList(self.on_list_update, "Alice", "bits")
            self.sim_manager.bob.bits = SmartList(self.on_list_update, "Bob", "bits")
            self.sim_manager.bob.bases = SmartList(self.on_list_update, "Bob", "bases")
            self.sim_manager.alice.message = SmartList(self.on_list_update, "Alice", "message")
        elif protocol_name == "SARG04":
            self.sim_manager.alice.sendBases = SmartList(self.on_list_update, "Alice", "bases")
            self.sim_manager.alice.bits = SmartList(self.on_list_update, "Alice", "bits")
            self.sim_manager.bob.bits = SmartList(self.on_list_update, "Bob", "bits")
            self.sim_manager.bob.bases = SmartList(self.on_list_update, "Bob", "bases")
            self.sim_manager.alice.message = SmartList(self.on_list_update, "Alice", "message")
        elif protocol_name == "E91":
            self.sim_manager.alice.results = SmartList(self.on_list_update, "Alice", "results")
            self.sim_manager.bob.results = SmartList(self.on_list_update, "Bob", "results")
            self.sim_manager.source.message = SmartList(self.on_list_update, "Source", "message")

        # Worker setup
        self.sim_thread = QThread()
        self.worker = SimWorker(sim_manager)
        self.worker.moveToThread(self.sim_thread)

        # --- LAYOUT ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # LEWA STRONA: ZAKŁADKI
        self.horiz_tabs = QTabWidget()
        self.horiz_tabs.setTabPosition(QTabWidget.TabPosition.North)

        sim_manager_class = type(sim_manager)

        self.sim_view = SimulationView(protocol_name, parent=self)
        self.tab_view = TableView(protocol_name, parent=self)
        self.analysis_view = AnalysisView(protocol_name, sim_manager_class, parent=self)

        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")

        # LOGI
        self.side_panel = SimLogsView(protocol_name, parent=self)

        main_layout.addWidget(self.horiz_tabs, stretch=7)
        main_layout.addWidget(self.side_panel, stretch=3)

        self.setLayout(main_layout)

        # --- SIGNALS ---
        # Sterowanie
        self.side_panel.sig_play.connect(self.worker.handle_play_toggle)
        self.side_panel.sig_next.connect(self.worker.next_step_simulation)
        self.side_panel.sig_prev.connect(self.worker.prev_step_simulation)
        self.side_panel.sig_skip.connect(self.worker.skip_simulation)
        self.side_panel.sig_speed.connect(self.worker.set_speed)

        # Reset
        self.side_panel.sig_forward_reset.connect(self.reset_gui_state)  # Nowa metoda
        self.side_panel.sig_forward_reset.connect(self.worker.reset_simulation)

        # Logi
        self.worker.sig_log_update.connect(self.side_panel.update_logs)
        self.worker.sig_log_update.connect(self.update_table_view_by_step)

        # Settings lock
        self.worker.sig_lock_settings.connect(self.sim_view.sim_lock_settings)
        self.sim_view.sig_forward_settings.connect(sim_manager.update_setting)

        self.sim_thread.start()

    def closeEvent(self, event):
        self.worker.stop_simulation()
        self.sim_thread.quit()
        self.sim_thread.wait()
        event.accept()

    def reset_gui_state(self):
        """Resetuje tabelę i liczniki statystyk"""
        self.tableManager.clear()
        self.stats_total_photons = 0
        self.stats_raw_len = 0
        self.stats_error_count = 0
        self.stats_stage = "Initializing..."

        # Odśwież widoki
        self.tab_view.update_table(self.tableManager.get_dataframe())
        self.sim_view.update_stats(self.stats_stage, 0, 0, 0, 0)

    def on_list_update(self, owner, data_type, value):
        # Tabela
        if owner == "Alice":
            if data_type == "bits":
                self.tableManager.log_alice_bit(value)
                self.stats_total_photons += 1
            elif data_type == "bases":
                self.tableManager.log_alice_base(value)
            elif data_type == "results":  # E91
                self.tableManager.log_alice_base(value["base"], True)
                self.tableManager.log_alice_bit(value["bit"])
                self.stats_total_photons += 1

        elif owner == "Bob":
            if data_type == "bits":
                self.tableManager.log_bob_bit(value)
            elif data_type == "bases":
                self.tableManager.log_bob_base(value)
            elif data_type == "results":  # E91
                self.tableManager.log_bob_base(value["base"], True)
                self.tableManager.log_bob_bit(value["bit"])

        # Statystyki
        try:
            t_alice_bases = self.tableManager.data["Alice bases"]
            t_bob_bases = self.tableManager.data["Bob bases"]
            t_alice_bits = self.tableManager.data["Alice bits"]
            t_bob_bits = self.tableManager.data["Bob bits"]
            t_raw_key = self.tableManager.data["Key bits"]

            idx = len(t_bob_bits) - 1

            if idx >= 0 and idx < len(t_alice_bases) and idx < len(t_bob_bases):
                # Czy bazy się zgadzają?
                a_base = t_alice_bases[idx]
                b_base = t_bob_bases[idx]

                if str(a_base) == str(b_base):
                    self.stats_raw_len += 1

                    if t_alice_bits[idx] != t_bob_bits[idx]:
                        self.stats_error_count += 1

        except Exception as e:
            pass

        self.sim_view.update_stats(
            self.stats_stage,
            self.stats_total_photons,
            self.stats_raw_len,
            self.stats_error_count,
            0
        )

    def update_table_view_by_step(self, step_idx, logs, clear_first):
        if clear_first:
            self.reset_gui_state()
            return

        full_df = self.tableManager.get_dataframe()
        if full_df.empty: return

        sliced_df = full_df.iloc[:step_idx + 1]
        self.tab_view.update_table(sliced_df)

        self.update_statistics_view_by_step(step_idx, self.worker.current_step)

    def update_statistics_view_by_step(self, step_idx, current_step):
        if step_idx < current_step:
            self.stats_stage = "Transmition"
        elif self.stats_stage == "BB84":
            if step_idx == current_step:
                self.stats_stage = "Bases Exchange"
            if step_idx == current_step + 1:
                self.stats_stage = "Sifting"
            if step_idx == current_step + 2:
                self.stats_stage = "Sampling"
            if step_idx == current_step + 3:
                self.stats_stage = "Error Corection Preparation"
            if step_idx == current_step + 4:
                self.stats_stage = "Error Corection"
            if step_idx == current_step + 5:
                self.stats_stage = "Privacy Amplification"
        elif self.stats_stage == "SARG04":
            if step_idx == current_step:
                self.stats_stage = "Anouncing States"
            if step_idx == current_step + 1:
                self.stats_stage = "Sifting States"
            if step_idx == current_step + 2:
                self.stats_stage = "Sampling"
            if step_idx == current_step + 3:
                self.stats_stage = "Error Corection Preparation"
            if step_idx == current_step + 4:
                self.stats_stage = "Error Corection"
            if step_idx == current_step + 5:
                self.stats_stage = "Privacy Amplification"
        elif self.stats_stage == "E91":
            if step_idx == current_step:
                self.stats_stage = "Analysis"
            elif step_idx == current_step + 1:
                self.stats_stage = "Error Correction"
