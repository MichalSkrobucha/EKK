from SimManager import SimManager
from QKD_Algorithms.Logger import SimLogger

logger = SimLogger()


def main() -> None:
    """
    Runs the simulation
    """
    simManager: SimManager = SimManager()
    logger.enable_logger(True)  # Włączenie logów
    # Simulation test
    simManager.simLoop()


if __name__ == '__main__':
    main()
