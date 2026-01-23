from SimManagerE91 import SimManagerE91 as SimManager


def run_simulation() -> None:
    """
    Runs the simulation
    """
    simManager: SimManager = SimManager()
    simManager.logger.enable_logger(True)  # Włączenie logów
    # Simulation test
    simManager.simLoop()


if __name__ == '__main__':
    run_simulation()
