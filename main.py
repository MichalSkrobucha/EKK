from Analysis import *

logger = SimLogger()


def main() -> None:
    """
    Runs the simulation
    """
    simManager: SimManager = SimManager()
    logger.enable_logger(True)  # Wyłącznie logów
    eveDependenceAnalysis(simManager, 30)


if __name__ == '__main__':
    main()
