from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time


class SimWorker(QObject):
    # --- SYGNAŁY ---
    sig_step_data = pyqtSignal(dict)
    sig_finished = pyqtSignal()
    sig_error = pyqtSignal(str)

    def __init__(self, sim_manager_class):
        super().__init__()
        self.manager = sim_manager_class()
        self.is_running = False
        self.is_paused = False
        self.speed_delay = 0.1

    def start_simulation(self):
        pass

    def stop_simulation(self):
        pass

    def pause_simulation(self):
        pass

    def resume_simulation(self):
        pass

    def single_step(self):
        pass

    def set_speed(self, value_percentage):
        pass
