import sys
import logging
from collections import defaultdict


class SimLogger:

    def __init__(self, sim_start: int = 0):
        self.sim_time = sim_start
        self.log_history = defaultdict(list)
        self._setup_logger()

    def _setup_logger(self, name: str = "MyLogger", level=logging.DEBUG):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.propagate = False

        self.full_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.plain_formatter = logging.Formatter('%(message)s')

        # --- CONSOLE HANDLER ---
        existing_console_handlers = [
            h for h in self._logger.handlers
            if isinstance(h, logging.StreamHandler) and not isinstance(h, DictionaryHistoryHandler)
        ]

        if not existing_console_handlers:
            # Nie ma handlera - tworzymy nowy
            self.main_handler = logging.StreamHandler(sys.stdout)
            self.main_handler.setLevel(level)
            self.main_handler.setFormatter(self.full_formatter)
            self._logger.addHandler(self.main_handler)
        else:
            self.main_handler = existing_console_handlers[0]

        # --- HISTORY HANDLER ---
        history_handler = DictionaryHistoryHandler(self)
        history_handler.setFormatter(self.full_formatter)
        self._logger.addHandler(history_handler)

        # --- Important Logger ---
        self.important_logger = logging.getLogger("ImportantSimLogger")
        self.important_logger.setLevel(logging.DEBUG)
        self.important_logger.propagate = False

        if self.important_logger.hasHandlers():
            self.important_logger.handlers.clear()

        ih = logging.StreamHandler(sys.stdout)
        ih.setFormatter(self.plain_formatter)
        self.important_logger.addHandler(ih)

        self.use_plain = False

    def use_plain_format(self, plain: bool = True) -> None:
        self.use_plain = plain
        if self.use_plain:
            self.main_handler.setFormatter(self.plain_formatter)
        else:
            self.main_handler.setFormatter(self.full_formatter)

    def enable_logger(self, enabled: bool = True) -> None:
        if enabled:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.WARNING)

    def set_time(self, time: int) -> None:
        self.sim_time = time

    def msg(self, msg: str, **kwargs) -> None:
        self.use_plain_format(True)
        self._logger.info(msg, **kwargs)

    def log(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        formatted_msg = f">>> [sim_time: {self.sim_time}] {msg} <<<"
        self._logger.info(formatted_msg, **kwargs)

    def debug(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self._logger.debug(msg, **kwargs)

    def info(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self._logger.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self._logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self._logger.error(msg, **kwargs)

    def important(self, msg):
        self.important_logger.info(msg)


class DictionaryHistoryHandler(logging.Handler):
    def __init__(self, sim_logger_instance):
        super().__init__()
        self.sim_logger = sim_logger_instance

    def emit(self, record):
        log_entry = self.format(record)
        current_sim_time = self.sim_logger.sim_time

        if current_sim_time not in self.sim_logger.log_history:
            self.sim_logger.log_history[current_sim_time] = []

        self.sim_logger.log_history[current_sim_time].append(log_entry)
