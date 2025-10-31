import sys
import logging


class SimLogger:
    _instance = None

    def __new__(cls, sim_start: int = 0):  # Singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.sim_time = sim_start
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self, name: str = "MyLogger", level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Konsola
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def set_time(self, time: int) -> None:
        self.sim_time = time

    def log(self, msg: str):
        formatted_msg = f">>> [sim_time: {self.sim_time}] {msg} <<<"
        self.logger.info(formatted_msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)
