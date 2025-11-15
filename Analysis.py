import matplotlib.pyplot as plt

from Logger import SimLogger
from SimManager import SimManager

logger = SimLogger()


def eveDependenceAnalysis(simManager: SimManager, n: int = 10) -> None:
    """
    Simulates QKD without/with Eve and shows average QBERs for both
    :param simManager: simulation Manager
    :param n: How many simulations for each scenario
    """

    # Withuot Eve
    simManager.__init__()
    avgQberWithoutEve: float = 0
    simManager.ifEve = False

    logger.important(f"==== Starting Eve Dependence Analysis for {n} times")

    for i in range(n):
        simManager.simLoop()
        avgQberWithoutEve += simManager.bob.qber
        simManager.clearLists()

    # With Eve
    simManager.__init__()
    avgQberWithEve: float = 0
    simManager.ifEve = True

    for i in range(n):
        simManager.simLoop()
        avgQberWithEve += simManager.bob.qber
        simManager.clearLists()

    logger.important(f"Average QBER without Eve: {avgQberWithoutEve / n}")
    logger.important(f"Average QBER with Eve: {avgQberWithEve / n}")


def dumpeningAnalysis(simManager: SimManager):
    pass


def baseTransformAnalysis(simManager: SimManager):
    pass


def bobsErrorAnalysis(simManager: SimManager):
    pass


def bobsEfficiencyAnalysis(simManager: SimManager):
    pass
