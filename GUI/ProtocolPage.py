from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThread, pyqtSignal

# Importuj swoje widoki
from GUI.StatisticsView import StatisticsView
from GUI.Workers.SimWorker import SimWorker
from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView
from SimLogsView import SimLogsView
from DataManagers.TableManager import TableManager
from Misc.SmartList import SmartList
from QKD_Algorithms.Common.SimManager import SimManager
# from GUI.SimLogsView import SimLogsView


class ProtocolPage(QWidget):
    sig_start_loop = pyqtSignal()

    def __init__(self, protocol_name, sim_manager: SimManager, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        self.tableManager = TableManager()
        self.sim_manager = sim_manager

        # --- Observable Lists ---

        if protocol_name == "BB84":
            self.sim_manager.alice.bases = SmartList(self.on_list_update, "Alice", "bases")
            self.sim_manager.alice.bits = SmartList(self.on_list_update, "Alice", "bits")
            self.sim_manager.bob.bits = SmartList(self.on_list_update, "Bob", "bits")
            self.sim_manager.bob.bases = SmartList(self.on_list_update, "Bob", "bases")
        elif protocol_name == "SARG04":
            self.sim_manager.alice.sendBases = SmartList(self.on_list_update, "Alice", "bases")
            self.sim_manager.alice.bits = SmartList(self.on_list_update, "Alice", "bits")
            self.sim_manager.bob.bits = SmartList(self.on_list_update, "Bob", "bits")
            self.sim_manager.bob.bases = SmartList(self.on_list_update, "Bob", "bases")
        elif protocol_name == "E91":
            self.sim_manager.alice.results = SmartList(self.on_list_update, "Alice", "results")
            self.sim_manager.bob.results = SmartList(self.on_list_update, "Bob", "results")

        self.sim_thread = QThread()
        self.worker = SimWorker(sim_manager)
        self.worker.moveToThread(self.sim_thread)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.horiz_tabs = QTabWidget()
        self.horiz_tabs.setTabPosition(QTabWidget.TabPosition.North)

        sim_manager_class = type(sim_manager)

        self.sim_view = SimulationView(protocol_name, parent=self)
        self.tab_view = TableView(protocol_name, parent=self)
        self.analysis_view = AnalysisView(protocol_name, sim_manager_class, parent=self)
        self.statistics_view = StatisticsView(parent=self)

        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")
        self.horiz_tabs.addTab(self.statistics_view, "STATISTICS")

        self.side_panel = SimLogsView(protocol_name, parent=self)

        main_layout.addWidget(self.horiz_tabs, stretch=7)
        main_layout.addWidget(self.side_panel, stretch=3)

        self.setLayout(main_layout)

        self.side_panel.sig_play.connect(self.worker.handle_play_toggle)
        self.side_panel.sig_next.connect(self.worker.next_step_simulation)
        self.side_panel.sig_prev.connect(self.worker.prev_step_simulation)
        self.side_panel.sig_skip.connect(self.worker.skip_simulation)
        self.side_panel.sig_speed.connect(self.worker.set_speed)

        self.side_panel.sig_forward_reset.connect(self.clear_table_view)
        self.worker.sig_log_update.connect(self.side_panel.update_logs)

        self.side_panel.sig_forward_reset.connect(self.worker.reset_simulation)
        self.worker.sig_log_update.connect(self.update_table_view_by_step)
        self.worker.sig_lock_settings.connect(self.sim_view.sim_lock_settings)
        self.sim_view.sig_forward_settings.connect(sim_manager.update_setting)

        self.sim_thread.start()

    def closeEvent(self, event):
        self.worker.stop_simulation()
        self.sim_thread.quit()
        self.sim_thread.wait()
        event.accept()

    def on_list_update(self, owner, data_type, value):
        if owner == "Alice":
            if data_type == "bits":
                self.tableManager.log_alice_bit(value)
            elif data_type == "bases":
                self.tableManager.log_alice_base(value)
            elif data_type == "results":
                base = value["base"]
                bit = value["bit"]
                self.tableManager.log_alice_base(base, True)
                self.tableManager.log_alice_bit(bit)

        elif owner == "Bob":
            if data_type == "bits":
                self.tableManager.log_bob_bit(value)
            elif data_type == "bases":
                self.tableManager.log_bob_base(value)
            elif data_type == "results":
                base = value["base"]
                bit = value["bit"]
                self.tableManager.log_bob_base(base, True)
                self.tableManager.log_bob_bit(bit)
        elif owner == "Eve":
            pass

    def update_table_view_by_step(self, step_idx, logs, clear_first):
        full_df = self.tableManager.get_dataframe()
        if full_df.empty:
            return

        sliced_df = full_df.iloc[:step_idx + 1]
        self.tab_view.update_table(sliced_df)

    def clear_table_view(self):
        self.tableManager.clear()
        full_df = self.tableManager.get_dataframe()
        self.tab_view.update_table(full_df)
