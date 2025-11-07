import matplotlib.pyplot as plt

from Logger import SimLogger
from SimManager import SimManager

logger = SimLogger()


def eveDependenceAnalysis(simManager: SimManager):
    n = 10

    # Bez Ewy
    simManager.__init__()
    avgQberWithoutEve: float = 0
    simManager.ifEve = False

    logger.important(f"==== Starting Eve Dependence Analysis for {n} times")

    for i in range(n):
        simManager.simLoop()
        avgQberWithoutEve += simManager.bob.qber

    logger.important(f"Average QBER without Eve: {avgQberWithoutEve/n}")

    # # Z Ewą
    simManager.__init__()
    avgQberWithEve: float = 0
    simManager.ifEve = True

    for i in range(n):
        simManager.simLoop()
        avgQberWithEve += simManager.bob.qber

    logger.important(f"Average QBER with Eve: {avgQberWithEve/n}")


def dumpeningAnalysis(simManager: SimManager):
    pass


def baseTransformAnalysis(simManager: SimManager):
    pass


def bobsErrorAnalysis(simManager: SimManager):
    pass


def bobsEfficiencyAnalysis(simManager: SimManager):
    pass