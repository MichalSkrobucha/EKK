from Logger import SimLogger
import logging
from SimManager import SimManager
from Analysis import *

logger = SimLogger()


def main() -> None:
    simManager = SimManager()
    logger.enable_logger(False)  # Wyłącznie logów
    eveDependenceAnalysis(simManager)

if __name__ == '__main__':
    main()
