import sys
import logging
from collections import defaultdict


class SimLogger:

    def __init__(self, sim_start: int = 0):
        self.sim_time = sim_start
        self.log_history = defaultdict(list)
        self._setup_logger()

    def _setup_logger(self, name: str = "MyLogger", level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.logger.propagate = False

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.main_handler = logging.StreamHandler(sys.stdout)
        self.main_handler.setLevel(level)
        self.logger.addHandler(self.main_handler)

        self.full_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.plain_formatter = logging.Formatter('%(message)s')

        # --- Konfiguracja Important Logger ---
        self.important_logger = logging.getLogger("ImportantSimLogger")
        self.important_logger.setLevel(logging.DEBUG)
        self.important_logger.propagate = False

        if self.important_logger.hasHandlers():
            self.important_logger.handlers.clear()

        ih = logging.StreamHandler(sys.stdout)
        ih.setFormatter(logging.Formatter('%(message)s'))
        self.important_logger.addHandler(ih)

        # Ustawiamy domyślny format
        self.use_plain = False
        self.use_plain_format(self.use_plain)

    def use_plain_format(self, plain: bool = True) -> None:
        self.use_plain = plain
        if self.use_plain:
            self.main_handler.setFormatter(self.plain_formatter)
        else:
            self.main_handler.setFormatter(self.full_formatter)

    def enable_logger(self, enabled: bool = True) -> None:
        if enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    def set_time(self, time: int) -> None:
        self.sim_time = time

    def msg(self, msg: str, **kwargs) -> None:
        self.use_plain_format(True)
        self.logger.info(msg, **kwargs)
        self.log_history[self.sim_time].append(msg)

    def log(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        formatted_msg = f">>> [sim_time: {self.sim_time}] {msg} <<<"
        self.logger.info(formatted_msg, **kwargs)
        self.log_history[self.sim_time].append(msg)

    def debug(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.debug(msg, **kwargs)
        self.log_history[self.sim_time].append(msg)

    def info(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.info(msg, **kwargs)
        self.log_history[self.sim_time].append(msg)

    def warning(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.warning(msg, **kwargs)
        self.log_history[self.sim_time].append(msg)

    def error(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.error(msg, **kwargs)
        self.log_history[self.sim_time].append(msg)

    def important(self, msg):
        self.important_logger.info(msg)
        self.log_history[self.sim_time].append(msg)