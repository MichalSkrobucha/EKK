from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import time


class SimWorker(QObject):
    # --- SYGNAŁY ---
    sig_step_data = pyqtSignal(dict)
    sig_finished = pyqtSignal()
    sig_error = pyqtSignal(str)

    def __init__(self, sim_manager):
        super().__init__()
        self.sim_manager = sim_manager
        self.current_step = 0
        self.speed_delay = 0.1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_one_step)

        # w (ms)
        self.interval = 100

    def run_one_step(self):
        if not self.sim_manager.is_running:
            self.stop_simulation()
            return

        try:
            self.sim_manager.sim_next_step()
            # Emitowanie danych
            # self.sig_step_data.emit(self.sim_manager.get_data())

        except Exception as e:
            self.sig_error.emit(str(e))
            self.stop_simulation()

    def handle_play_toggle(self):
        print("Play toggle")
        if self.timer.isActive():
            self.pause_simulation()
        else:
            self.start_simulation()

    def start_simulation(self):
        if not self.sim_manager.is_running:
            self.sim_manager.is_running = True

        print(f"Start simulation with interval: {self.interval}ms")
        self.timer.start(self.interval)

    def stop_simulation(self):
        print("Stopping simulation")
        self.timer.stop()
        self.sim_manager.is_running = False
        self.sig_finished.emit()

    def pause_simulation(self):
        print("Pausing simulation")
        self.sim_manager.is_running = False
        self.timer.stop()

    def reset_simulation(self):
        print("Stopping simulation")
        self.timer.stop()
        self.sim_manager.is_running = False

    def skip_simulation(self):
        self.timer.start(0)
        while self.sim_manager.is_running:
            self.run_one_step()
        print("Skipped simulation")

    def prev_step_simulation(self):
        pass

    def next_step_simulation(self):
        pass

    def set_speed(self, value_percentage):
        val = max(1, value_percentage)
        new_interval = int(1000 / val * 5)
        self.interval = new_interval
        if self.timer.isActive():
            self.timer.setInterval(self.interval)

