import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThread
from PyQt6.QtCore import Qt, pyqtSignal

from GUI.StatisticsView import StatisticsView
from SimWorker import SimWorker
from GUI.AnalysisView import AnalysisView
from SimulationView import SimulationView
from TableView import TableView
from DataManagers.TableManager import TableManager
from Misc.SmartList import SmartList

from QKD_Algorithms.Common.SimManager import SimManager


class ProtocolPage(QWidget):
    """
    To jest strona dla konkretnego protokołu (np. BB84).
    Zawiera POZIOME zakładki (SIM, TABLE, GRAPH).
    """
    sig_start_loop = pyqtSignal()

    def __init__(self, protocol_name, sim_manager: SimManager, parent=None):
        super().__init__(parent)
        self.protocol_name = protocol_name
        # sim_manager.logger.enable_logger(False)
        self.tableManager = TableManager()
        self.sim_manager = sim_manager

        # --- Observable Lists ---
        # ALICE
        self.sim_manager.alice.bits = SmartList(self.on_list_update, "Alice", "bits")
        self.sim_manager.alice.bases = SmartList(self.on_list_update, "Alice", "bases")
        # BOB
        self.sim_manager.bob.bits = SmartList(self.on_list_update, "Bob", "bits")
        self.sim_manager.bob.bases = SmartList(self.on_list_update, "Bob", "bases")

        # --- KONFIGURACJA WĄTKU ---
        self.sim_thread = QThread()
        self.worker = SimWorker(sim_manager)

        # Przenosimy Workera do wątku
        self.worker.moveToThread(self.sim_thread)

        # --- LAYOUT ---
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Poziome Zakładki u góry
        self.horiz_tabs = QTabWidget()
        self.horiz_tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Zakładki
        self.sim_view = SimulationView(protocol_name, parent=self)
        self.horiz_tabs.addTab(self.sim_view, "SIMULATION")
        self.tab_view = TableView(parent=self)
        self.horiz_tabs.addTab(self.tab_view, "TABLE")
        self.analysis_view = AnalysisView(parent=self)
        self.horiz_tabs.addTab(self.analysis_view, "ANALYSIS")
        self.statistics_view = StatisticsView(parent=self)
        self.horiz_tabs.addTab(self.statistics_view, "STATISTICS")

        layout.addWidget(self.horiz_tabs)
        self.setLayout(layout)

        self.sim_view.sig_play.connect(self.worker.handle_play_toggle)
        self.sim_view.sig_reset.connect(self.worker.reset_simulation)
        self.sim_view.sig_next.connect(self.worker.next_step_simulation)
        self.sim_view.sig_prev.connect(self.worker.prev_step_simulation)
        self.sim_view.sig_skip.connect(self.worker.skip_simulation)
        self.sim_view.sig_speed.connect(self.worker.set_speed)

        self.worker.sig_log_update.connect(self.sim_view.update_logs)
        self.worker.sig_log_update.connect(self.update_table_view_by_step)
        self.worker.sig_lock_settings.connect(self.sim_view.sim_lock_settings)

        self.sim_view.sig_forward_settings.connect(sim_manager.update_setting)
        self.sim_view.sig_forward_reset.connect(self.worker.reset_simulation)

        self.sim_thread.start()

    def closeEvent(self, event):
        self.worker.stop_simulation()
        self.sim_thread.quit()
        self.sim_thread.wait()
        event.accept()

    def on_list_update(self, owner, value):
        """
        Ta funkcja jest wywoływana automatycznie, gdy SimManager zrobi .append().
        Działa jak "most" między SimManagerem a TableManagerem.
        """
        if owner == "Alice":
            try:
                bit = self.sim_manager.alice.bits[-1]
                base = self.sim_manager.alice.bases[-1]

                self.tableManager.log_alice(bit, base)
            except IndexError:
                return  # Czekamy aż druga lista (np. bases) też dostanie append w następnej linijce kodu

        elif owner == "Bob":
            try:
                bit = self.sim_manager.bob.bits[-1]
                base = self.sim_manager.bob.bases[-1]
                self.tableManager.log_bob(bit, base)
            except IndexError:
                return

        elif owner == "Eve":
            pass

        # Update View
        df = self.tableManager.get_dataframe()
        self.tab_view.update_table(df)

    def update_table_view_by_step(self, step_idx, logs, clear_first):
        """
        Pobiera pełne dane, przycina je do aktualnego kroku i wysyła do tabeli.
        """
        full_df = self.tableManager.get_dataframe()

        if full_df.empty:
            return

        sliced_df = full_df.iloc[:step_idx + 1]
        self.tab_view.update_table(sliced_df)
