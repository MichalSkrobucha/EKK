from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import time


class SimWorker(QObject):
    # --- SYGNAŁY ---
    # sig_step_data = pyqtSignal(dict)
    # sig_finished = pyqtSignal()
    # sig_error = pyqtSignal(str)
    sig_log_update = pyqtSignal(int, list, bool)
    sig_lock_settings = pyqtSignal(bool)

    def __init__(self, sim_manager):
        super().__init__()
        self.sim_manager = sim_manager
        self.current_step = 0
        self.speed_delay = 0.1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_one_step)

        # w (ms)
        self.base_interval = 500
        self.interval = 500

    def run_one_step(self):
        if not self.sim_manager.is_running:
            self.stop_simulation()
            return
        try:
            if self.current_step < self.sim_manager.sim_step:  # Jest się w przeszłości
                current_logs = self._get_history_logs(self.current_step)
                self.sig_log_update.emit(self.current_step, current_logs, True)
            else:  # Teraźniejszość / Przyszłość
                self.sim_manager.sim_next_step()
                current_logs = self._get_current_logs(self.current_step)
                self.sig_log_update.emit(self.current_step, current_logs, False)
            self.current_step += 1
        except Exception as e:
            # self.sig_error.emit(str(e))
            print(f"Simulation Error: {e}")
            self.stop_simulation()

    def _get_current_logs(self, target_step):
        return self.sim_manager.logger.log_history.get(target_step, [])

    def _get_history_logs(self, end_step, start_step=0):
        """Pobiera logi od kroku start_step do end_step włącznie"""
        full_history_text = []
        for i in range(start_step, end_step + 1):
            if i in self.sim_manager.logger.log_history:
                full_history_text.extend(self.sim_manager.logger.log_history[i])
        return full_history_text

    def handle_play_toggle(self):
        print("Play toggle")
        if self.timer.isActive():
            self.pause_simulation()
        else:
            self.start_simulation()

    def start_simulation(self, start_timer: bool = True):
        if not self.sim_manager.is_running:
            self.sim_manager.is_running = True

        self.sig_lock_settings.emit(True)
        if start_timer:
            # print(f"Start simulation with interval: {self.interval}ms")
            self.timer.start(self.interval)

    def stop_simulation(self):
        print("Stopping simulation")
        self.timer.stop()
        self.sim_manager.is_running = False
        self.sig_lock_settings.emit(False)

    def pause_simulation(self):
        print("Pausing simulation")
        self.timer.stop()

    def reset_simulation(self):
        print("Reseting simulation")
        self.timer.stop()
        self.sim_manager.is_running = False
        self.sig_lock_settings.emit(False)
        self.sim_manager.clear_simManager()
        self.current_step = 0

    def skip_simulation(self):
        self.start_simulation(False)
        self.timer.start(0)
        while self.sim_manager.is_running:
            self.run_one_step()
        self.timer.stop()
        print("Skipped simulation")

    def prev_step_simulation(self):
        self.start_simulation(False)
        self.current_step -= 2
        self.current_step = max(0, self.current_step)
        self.run_one_step()

    def next_step_simulation(self):
        self.start_simulation(False)
        self.timer.stop()
        self.run_one_step()

    def jump_to_stage_offset(self, offset_from_sim_end):
        """
        Inteligentny skok do etapu.
        Jeśli etap był już obliczony -> cofa/przesuwa widok (bez resetu).
        Jeśli etap jest w przyszłości -> wykonuje szybkie obliczenia.
        """
        sim_end = getattr(self.sim_manager, 'sim_end', 0)
        if sim_end == 0:
            sim_end = getattr(self.sim_manager, 'n_photons', 10)

        target_step = sim_end + offset_from_sim_end

        self.timer.stop()

        if not self.sim_manager.is_running:
            self.sim_manager.is_running = True
        self.sig_lock_settings.emit(True)

        if target_step < self.sim_manager.sim_step:
            print(f"Jumping to HISTORY: {target_step}")
            self.current_step = target_step

            view_idx = max(0, self.current_step - 1)
            full_logs = self._get_history_logs(view_idx)

            self.sig_log_update.emit(view_idx, full_logs, True)

        else:
            # --- Fast Forward ---
            print(f"Calculating forwards to: {target_step}")

            while self.current_step < target_step and self.sim_manager.is_running:
                if self.current_step < self.sim_manager.sim_step:
                    pass
                else:
                    self.sim_manager.sim_next_step()

                self.current_step += 1

            view_idx = max(0, self.current_step - 1)
            full_logs = self._get_history_logs(view_idx)
            self.sig_log_update.emit(view_idx, full_logs, True)

    def set_speed(self, value):
        val = value/100
        new_interval = int(self.base_interval/val)
        self.interval = new_interval
        if self.timer.isActive():
            self.timer.setInterval(self.interval)