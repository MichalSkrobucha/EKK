# from .Analysis import *
from SimManagerSARG import SimManagerSARG as SimManager


def run_simulation() -> None:
    """
    Runs the simulation
    """
    simManager: SimManager = SimManager()
    simManager.logger.enable_logger(True)  # Włączenie logów
    simManager.ifEve = False
    # Simulation test
    simManager.simLoop()
    # simManager.printTable()
    #
    # Analysis
    # logger.enable_logger(False)  # Wyłącznie logów
    # eveDependenceAnalysis(simManager, 30)
    # dumpeningAnalysis(simManager, [0.05, 0.2, 0.6, 0.90], [0.5, 8, 40, 200], 20)
    # baseTransformAnalysis(simManager, [0, 0.05, 0.2, 0.9], [0.5, 8, 40, 200], 20)
    # bobsErrorEffiecencyAnalysis(simManager, [0, 0.05, 0.2, 0.9], [0.05, 0.2, 0.5, 0.99], 20)


if __name__ == '__main__':
    run_simulation()
