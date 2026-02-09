from PyQt6.QtCore import QObject, pyqtSignal
from GUI.DataManagers.TableManager import TableManager
from GUI.DataManagers.StatisticsManager import StatisticsManager


class GuiDataWorker(QObject):
    sig_data_ready = pyqtSignal(object, dict, int, list)

    def __init__(self, sim_manager, protocol_name):
        super().__init__()
        self.sim_manager = sim_manager
        self.protocol_name = protocol_name
        self.tableManager = TableManager(protocol_name)
        self.statsManager = StatisticsManager()

    def process_data(self, step_idx, logs):
        self.tableManager.update_from_simulation(self.sim_manager)
        full_df = self.tableManager.get_dataframe()

        sim_end = getattr(self.sim_manager, 'sim_end', 0)
        if sim_end == 0:
            sim_end = getattr(self.sim_manager, 'n_photons', 10)

        sliced_df = None
        if not full_df.empty:
            if step_idx >= 0:
                if step_idx < sim_end:
                    slice_len = step_idx + 1
                else:
                    slice_len = sim_end

                final_slice = min(slice_len, len(full_df))
                sliced_df = full_df.iloc[:final_slice]

        stats = self.statsManager.calculate_statistics(self.sim_manager, self.protocol_name, step_idx)

        self.sig_data_ready.emit(sliced_df, stats, step_idx, logs)
