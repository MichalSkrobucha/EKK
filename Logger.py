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

        # standardowy handler
        self.full_handler = logging.StreamHandler(sys.stdout)
        self.full_handler.setLevel(level)
        full_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.full_handler.setFormatter(full_formatter)
        self.logger.addHandler(self.full_handler)

        # plain handler
        self.plain_handler = logging.StreamHandler(sys.stdout)
        self.plain_handler.setLevel(level)
        plain_formatter = logging.Formatter('%(message)s')
        self.plain_handler.setFormatter(plain_formatter)
        self.logger.addHandler(self.plain_handler)

        # always handler
        self.important_logger = logging.getLogger("ImportantSimLogger")
        self.important_logger.setLevel(logging.DEBUG)
        ih = logging.StreamHandler(sys.stdout)
        ih.setFormatter(logging.Formatter('%(message)s'))
        self.important_logger.addHandler(ih)

        self.use_plain = False
        self.use_plain_format(self.use_plain)

    def _update_handlers(self) -> None:
        # Włącza tylko jeden z handlerów
        self.full_handler.setLevel(logging.DEBUG if not self.use_plain else logging.WARNING)
        self.plain_handler.setLevel(logging.DEBUG if self.use_plain else logging.WARNING)

    def use_plain_format(self, plain: bool = True) -> None:
        self.use_plain = plain
        self._update_handlers()

    def enable_logger(self,enabled: bool = True) -> None:
        if enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    def set_time(self, time: int) -> None:
        self.sim_time = time

    def msg(self,msg: str, **kwargs) -> None:
        self.use_plain_format(True)
        self.logger.info(msg, **kwargs)

    def log(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        formatted_msg = f">>> [sim_time: {self.sim_time}] {msg} <<<"
        self.logger.info(formatted_msg, **kwargs)

    def debug(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.debug(msg, **kwargs)

    def info(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs) -> None:
        self.use_plain_format(False)
        self.logger.error(msg, **kwargs)

    def important(self, msg):
        self.important_logger.info(msg)
