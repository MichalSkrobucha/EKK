import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal


class AnalysisWorker(QObject):
    """
    Worker wykonujący symulacje w osobnym wątku.
    """
    sig_progress = pyqtSignal(int, int)  # (current, total)
    sig_log = pyqtSignal(str)
    sig_finished = pyqtSignal()

    # Sygnały wyników
    sig_result_eve = pyqtSignal(pd.DataFrame)
    sig_result_heatmap = pyqtSignal(pd.DataFrame, str, str)  # df, xlabel, ylabel

    def __init__(self, sim_manager_cls, protocol_name):
        super().__init__()
        self.SimManagerCls = sim_manager_cls
        self.protocol_name = protocol_name
        self.is_running = False

    def stop(self):
        self.is_running = False

    def run_eve_analysis(self, n_trials: int):
        self.is_running = True
        self.sig_log.emit(f"Starting Eve Analysis ({n_trials} trials)...")

        sim = self.SimManagerCls()
        sim.qberThreshhold = 1
        results = []
        total_steps = n_trials * 2

        # Bez Ewy
        sim.ifEve = False
        for i in range(n_trials):
            if not self.is_running: break
            sim.simLoop()
            results.append({"Trial": i + 1, "QBER": sim.bob.qber, "Scenario": "Without Eve"})
            sim.clear_simManager()
            self.sig_progress.emit(i + 1, total_steps)

        # Z Ewą
        sim.ifEve = True
        for i in range(n_trials):
            if not self.is_running: break
            sim.simLoop()
            results.append({"Trial": i + 1, "QBER": sim.bob.qber, "Scenario": "With Eve"})
            sim.clear_simManager()
            self.sig_progress.emit(n_trials + i + 1, total_steps)

        if self.is_running:
            df = pd.DataFrame(results)
            self.sig_result_eve.emit(df)
            self.sig_log.emit("Eve Analysis Finished.")
        else:
            self.sig_log.emit("Analysis Aborted.")

        self.sig_finished.emit()
        self.is_running = False

    def run_parameter_sweep(self, param1_name: str, param1_vals: list,
                            param2_name: str, param2_vals: list,
                            n_avg: int):

        self.is_running = True
        self.sig_log.emit(f"Starting Sweep: {param1_name} vs {param2_name}...")

        sim = self.SimManagerCls()
        sim.qberThreshhold = 1
        sim.ifEve = False

        data_matrix = []
        total_steps = len(param1_vals) * len(param2_vals)
        current_step = 0

        p1_sorted = sorted(param1_vals)
        p2_sorted = sorted(param2_vals)

        for p1 in p1_sorted:
            row_data = []
            if hasattr(sim, param1_name):
                setattr(sim, param1_name, p1)

            for p2 in p2_sorted:
                if not self.is_running: break

                if hasattr(sim, param2_name):
                    setattr(sim, param2_name, p2)

                temp_qber = 0
                for _ in range(n_avg):
                    sim.simLoop()
                    temp_qber += sim.bob.qber
                    sim.clear_simManager()

                avg_qber = temp_qber / n_avg
                row_data.append(avg_qber)

                current_step += 1
                self.sig_progress.emit(current_step, total_steps)

            data_matrix.append(row_data)

        if self.is_running:
            df = pd.DataFrame(data_matrix, index=p1_sorted, columns=p2_sorted)
            self.sig_result_heatmap.emit(df, param2_name, param1_name)  # X label, Y label
            self.sig_log.emit("Sweep Finished.")
        else:
            self.sig_log.emit("Sweep Aborted.")

        self.sig_finished.emit()
        self.is_running = False