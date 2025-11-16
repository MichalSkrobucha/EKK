from Logger import SimLogger
import logging
from SimManager import SimManager
from Analysis import *

logger = SimLogger()


def main() -> None:
    """
    Runs the simulation
    """
    simManager: SimManager = SimManager()
    logger.enable_logger(True)  # Włączenie logów
    # Simulation test
    simManager.simLoop()
    simManager.printTable()

    # Analysis
    logger.enable_logger(False)  # Wyłącznie logów
    eveDependenceAnalysis(simManager, 30)
    dumpeningAnalysis(simManager, [0.05, 0.2, 0.6, 0.90], [0.5, 8, 40, 200], 20)
    baseTransformAnalysis(simManager, [0, 0.05, 0.2, 0.9],[0.5, 8, 40, 200], 20)
    bobsErrorEffiecencyAnalysis(simManager, [0, 0.05, 0.2, 0.9], [0.05, 0.2, 0.5, 0.99], 20)


if __name__ == '__main__':
    main()
