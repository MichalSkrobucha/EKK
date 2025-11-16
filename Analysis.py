import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from Logger import SimLogger
from SimManager import SimManager
import pandas as pd
import seaborn as sns

logger = SimLogger()


def eveDependenceAnalysis(simManager: SimManager, n: int = 10) -> None:
    """
    Simulates QKD without/with Eve and shows average QBERs for both
    :param simManager: simulation Manager
    :param n: How many simulations for each scenario
    """
    simManager.__init__()
    # Withuot Eve
    avgQberWithoutEve: float = 0
    simManager.ifEve = False
    withoutEveResults: list[float] = []

    logger.important(f"==== Starting Eve Dependence Analysis for {n} times")

    for i in range(n):
        simManager.simLoop()
        avgQberWithoutEve += simManager.bob.qber
        withoutEveResults.append(simManager.bob.qber)
        simManager.clearLists()

    # With Eve
    avgQberWithEve: float = 0
    simManager.ifEve = True
    withEveResults: list[float] = []

    for i in range(n):
        simManager.simLoop()
        avgQberWithEve += simManager.bob.qber
        withEveResults.append(simManager.bob.qber)
        simManager.clearLists()

    logger.important(f"Average QBER without Eve: {avgQberWithoutEve / n}")
    logger.important(f"Average QBER with Eve: {avgQberWithEve / n}")

    # Plot
    x = list(range(1, n + 1))
    plt.figure(figsize=(10, 6))

    plt.scatter(x, withoutEveResults, label="Without Eve", marker='o')
    plt.scatter(x, withEveResults, label="With Eve", marker='x')
    plt.plot(x, withoutEveResults, alpha=0.5)
    plt.plot(x, withEveResults, alpha=0.5)

    plt.title("QBER over trials")
    plt.xlabel("Trial")
    plt.ylabel("QBER")
    plt.legend()
    plt.grid(True)
    plt.show()


def dumpeningAnalysis(simManager: SimManager, dumpeningValues: list[float], channelLengthValues: list[float], n_tests: int = 5) -> None:
    """
        Simulates QKD for specified dumpening and channel length parameters and shows average QBERs
        :param simManager: simulation Manager
        :param dumpeningValues: List of tested dumpening values
        :param channelLengthValues: List of tested channel lengths
        :param n_tests: Number of tests for a given pair of parameters
    """
    simManager.__init__()
    simManager.ifEve = False
    n: int = len(dumpeningValues)
    m: int = len(channelLengthValues)
    dumpeningValues = sorted(dumpeningValues)
    channelLengthValues = sorted(channelLengthValues)
    dumpeningQBERResults: list[list[float]] = [[0 for _ in range(m)] for _ in range(n)]

    logger.important(f"==== Starting Dumpening Parameter Dependence Analysis for {n_tests} times")

    for i in range(n):
        simManager.dumpening_per_km = dumpeningValues[i]
        for j in range(m):
            simManager.channelLength = channelLengthValues[j]
            for _ in range(n_tests):
                simManager.simLoop()
                dumpeningQBERResults[i][j] += simManager.bob.qber
                simManager.clearLists()
            dumpeningQBERResults[i][j] /= n_tests

    df = pd.DataFrame(
        dumpeningQBERResults,
        index=dumpeningValues,
        columns=channelLengthValues
    )
    logger.important(f"Average QBER depending on dumpening and channel length:\n{df}")

    # Plot
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        df,
        annot=True,
        fmt=".3f",
        cmap="viridis",
        cbar_kws={'label': 'QBER'}
    )
    plt.gca().invert_yaxis()
    plt.title("QBER Heatmap: Dumpening vs Channel Length")
    plt.xlabel("Channel Length")
    plt.ylabel("Dumpening")
    plt.savefig("data/dumpeningAnalysis.png", dpi=300)
    plt.show()


def baseTransformAnalysis(simManager: SimManager, baseTransformValues: list[float], channelLengthValues: list[float], n_tests: int = 5) -> None:
    """
        Simulates QKD for specified baseTransform and channel length parameters and shows average QBERs
        :param simManager: simulation Manager
        :param baseTransformValues: List of tested base transform values
        :param channelLengthValues: List of tested channel lengths
        :param n_tests: Number of tests for a given pair of parameters
    """
    simManager.__init__()
    simManager.ifEve = False
    n: int = len(baseTransformValues)
    m: int = len(channelLengthValues)
    baseTransformValues = sorted(baseTransformValues)
    channelLengthValues = sorted(channelLengthValues)
    baseTransformQBERResults: list[list[float]] = [[0 for _ in range(m)] for _ in range(n)]

    logger.important(f"==== Starting Base Transform Parameter Dependence Analysis for {n_tests} times")

    for i in range(n):
        simManager.base_transform_per_km = baseTransformValues[i]
        for j in range(m):
            simManager.channelLength = channelLengthValues[j]
            for _ in range(n_tests):
                simManager.simLoop()
                baseTransformQBERResults[i][j] += simManager.bob.qber
                simManager.clearLists()
            baseTransformQBERResults[i][j] /= n_tests

    df = pd.DataFrame(
        baseTransformQBERResults,
        index=baseTransformValues,
        columns=channelLengthValues
    )
    logger.important(f"Average QBER depending on base transform and channel length:\n{df}")

    # Plot
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        df,
        annot=True,
        fmt=".3f",
        cmap="rocket",
        cbar_kws={'label': 'QBER'}
    )
    plt.gca().invert_yaxis()
    plt.title("QBER Heatmap: Base Transform vs Channel Length")
    plt.xlabel("Channel Length")
    plt.ylabel("Base Transform")
    plt.savefig("data/baseTransformAnalysis.png", dpi=300)
    plt.show()


def bobsErrorEffiecencyAnalysis(simManager: SimManager, errorValues: list[float], efficiencyValues: list[float], n_tests: int = 5) -> None:
    """
        Simulates QKD for specified error and eficiency parameters and shows average QBERs
        :param simManager: simulation Manager
        :param errorValues: List of tested error values
        :param efficiencyValues: List of tested efficiency values
        :param n_tests: Number of tests for a given pair of parameters
    """
    simManager.__init__()
    simManager.ifEve = False
    n: int = len(errorValues)
    m: int = len(efficiencyValues)
    errorValues = sorted(errorValues)
    efficiencyValues = sorted(efficiencyValues)
    errorQBERResults: list[list[float]] = [[0 for _ in range(m)] for _ in range(n)]

    logger.important(f"==== Starting Bob's Error Parameter Dependence Analysis for {n_tests} times")

    for i in range(n):
        simManager.bob.error = errorValues[i]
        for j in range(m):
            simManager.bob.efficiency = efficiencyValues[j]
            for _ in range(n_tests):
                simManager.simLoop()
                errorQBERResults[i][j] += simManager.bob.qber
                simManager.clearLists()
            errorQBERResults[i][j] /= n_tests

    df = pd.DataFrame(
        errorQBERResults,
        index=errorValues,
        columns=efficiencyValues
    )
    logger.important(f"Average QBER depending on error and efficiency:\n{df}")

    # Plot
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        df,
        annot=True,
        fmt=".3f",
        cmap="mako",
        cbar_kws={'label': 'QBER'}
    )
    plt.gca().invert_yaxis()
    plt.title("QBER Heatmap: Error vs Efficiency")
    plt.xlabel("Efficiency")
    plt.ylabel("Error")
    plt.savefig("data/bobsErrorEffiecencyAnalysis.png", dpi=300)
    plt.show()
