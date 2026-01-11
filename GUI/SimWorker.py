from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time


class SimWorker(QObject):
    # --- SYGNAŁY ---
    sig_step_data = pyqtSignal(dict)
    sig_finished = pyqtSignal()
    sig_error = pyqtSignal(str)

    def __init__(self, sim_manager):
        super().__init__()
        self.sim_manager = sim_manager
        self.is_paused = False
        self.current_step = 0
        self.speed_delay = 0.1

    def handle_play_toggle(self):
        if self.sim_manager.is_running:
            if self.is_paused:
                self.resume_simulation()
            else:
                self.pause_simulation()
        else:
            self.start_simulation()

    def start_simulation(self):
        self.sim_manager.is_running = True
        # Główna petla symulacji
        while self.sim_manager.is_running:
            if self.is_paused:
                time.sleep(self.speed_delay)
                continue
            try:
                self.sim_manager.sim_next_step()
            except Exception as e:
                pass  # TODO
            time.sleep(self.speed_delay)

    def stop_simulation(self):
        pass

    def pause_simulation(self):
        self.is_paused = True

    def resume_simulation(self):
        self.is_paused = False

    def reset_simulation(self):
        self.is_paused = True

    def skip_simulation(self):
        pass

    def prev_step_simulation(self):
        pass

    def next_step_simulation(self):
        pass

    def set_speed(self, value_percentage):
        pass
