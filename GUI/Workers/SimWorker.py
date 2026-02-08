from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import time


class SimWorker(QObject):
    sig_log_update = pyqtSignal(int, list, bool)
    sig_lock_settings = pyqtSignal(bool)

    def __init__(self, sim_manager):
        super().__init__()
        self.sim_manager = sim_manager
        self.current_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_one_step)
        self.interval = 100

    def run_one_step(self):
        if not self.sim_manager.is_running:
            self.stop_simulation()
            return
        try:
            if self.current_step < self.sim_manager.sim_step:
                current_logs = self._get_history_logs(self.current_step)
                self.sig_log_update.emit(self.current_step, current_logs, True)
            else:
                self.sim_manager.sim_next_step()
                current_logs = self._get_current_logs(self.current_step)
                self.sig_log_update.emit(self.current_step, current_logs, False)
            self.current_step += 1
        except Exception as e:
            print(f"Error: {e}")
            self.stop_simulation()

    def _get_current_logs(self, target_step):
        return self.sim_manager.logger.log_history.get(target_step, [])

    def _get_history_logs(self, end_step, start_step=0):
        full_history = []
        for i in range(start_step, end_step + 1):
            if i in self.sim_manager.logger.log_history:
                full_history.extend(self.sim_manager.logger.log_history[i])
        return full_history

    def handle_play_toggle(self):
        if self.timer.isActive():
            self.pause_simulation()
        else:
            self.start_simulation()

    def start_simulation(self, start_timer: bool = True):
        if not self.sim_manager.is_running:
            self.sim_manager.is_running = True
        self.sig_lock_settings.emit(True)
        if start_timer:
            self.timer.start(self.interval)

    def stop_simulation(self):
        self.timer.stop()
        self.sim_manager.is_running = False
        self.sig_lock_settings.emit(False)

    def pause_simulation(self):
        self.timer.stop()

    def reset_simulation(self):
        self.timer.stop()
        self.sim_manager.is_running = False
        self.sig_lock_settings.emit(False)
        self.sim_manager.clear_simManager()
        self.current_step = 0

    def skip_simulation(self):
        self.start_simulation(False)
        while self.sim_manager.is_running:
            self.run_one_step()
        self.stop_simulation()

    def prev_step_simulation(self):
        self.start_simulation(False)
        self.current_step = max(0, self.current_step - 2)
        self.run_one_step()

    def next_step_simulation(self):
        self.start_simulation(False)
        self.run_one_step()

    def set_speed(self, val):
        self.interval = int(1000 / max(1, val) * 5)
        if self.timer.isActive():
            self.timer.setInterval(self.interval)

    def jump_to_stage_offset(self, offset_from_sim_end):
        sim_end = getattr(self.sim_manager, 'sim_end', 0)
        if sim_end == 0:
            sim_end = getattr(self.sim_manager, 'n_photons', 10)

        target_step = sim_end + offset_from_sim_end

        if target_step < self.current_step:
            self.reset_simulation()

        self.timer.stop()
        self.sim_manager.is_running = True
        self.sig_lock_settings.emit(True)

        while self.current_step < target_step and self.sim_manager.is_running:
            self.sim_manager.sim_next_step()
            self.current_step += 1

        full_logs = self._get_history_logs(self.current_step - 1)
        self.sig_log_update.emit(self.current_step - 1, full_logs, True)
