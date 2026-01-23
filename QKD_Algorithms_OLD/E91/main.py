from QKD_Algorithms_OLD.E91.SimManager import SimManager
from QKD_Algorithms_OLD.Logger import SimLogger

logger = SimLogger()


def main() -> None:
    """
    Runs the simulation
    """
    simManager: SimManager = SimManager()
    logger.enable_logger(True)  # Włączenie logów
    simManager.ifEve = False
    # Simulation test
    simManager.simLoop()


if __name__ == '__main__':
    main()
