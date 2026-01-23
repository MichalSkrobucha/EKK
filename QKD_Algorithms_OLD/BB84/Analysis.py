import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from QKD_Algorithms_OLD.Logger import SimLogger
from .SimManager import SimManager
import pandas as pd
import seaborn as sns


class Analysis:
    data_path: str = ''

    def __init__(self, simManager: SimManager, logger: SimLogger, protocol_name="default"):
        self.simManager = simManager
        self.logger = logger
        self.protocol_name = protocol_name
        self.data_path = f'QKD_Algorithms/{protocol_name}/data/'

    def eveDependenceAnalysis(self, n: int = 10) -> None:
        """
        Simulates QKD without/with Eve and shows average QBERs for both
        :param simManager: simulation Manager
        :param n: How many simulations for each scenario
        """
        self.simManager.__init__()
        # Withuot Eve
        avgQberWithoutEve: float = 0
        self.simManager.ifEve = False
        withoutEveResults: list[float] = []

        self.logger.important(f"==== Starting Eve Dependence Analysis for {n} times")

        for i in range(n):
            self.simManager.simLoop()
            avgQberWithoutEve += self.simManager.bob.qber
            withoutEveResults.append(self.simManager.bob.qber)
            self.simManager.clearLists()

        # With Eve
        avgQberWithEve: float = 0
        self.simManager.ifEve = True
        withEveResults: list[float] = []

        for i in range(n):
            self.simManager.simLoop()
            avgQberWithEve += self.simManager.bob.qber
            withEveResults.append(self.simManager.bob.qber)
            self.simManager.clearLists()

        self.logger.important(f"Average QBER without Eve: {avgQberWithoutEve / n}")
        self.logger.important(f"Average QBER with Eve: {avgQberWithEve / n}")

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

    def dumpeningAnalysis(self, dumpeningValues: list[float], channelLengthValues: list[float],
                          n_tests: int = 5) -> None:
        """
            Simulates QKD for specified dumpening and channel length parameters and shows average QBERs
            :param simManager: simulation Manager
            :param dumpeningValues: List of tested dumpening values
            :param channelLengthValues: List of tested channel lengths
            :param n_tests: Number of tests for a given pair of parameters
        """
        self.simManager.__init__()
        self.simManager.ifEve = False
        n: int = len(dumpeningValues)
        m: int = len(channelLengthValues)
        dumpeningValues = sorted(dumpeningValues)
        channelLengthValues = sorted(channelLengthValues)
        dumpeningQBERResults: list[list[float]] = [[0 for _ in range(m)] for _ in range(n)]

        self.logger.important(f"==== Starting Dumpening Parameter Dependence Analysis for {n_tests} times")

        for i in range(n):
            self.simManager.dumpening_per_km = dumpeningValues[i]
            for j in range(m):
                self.simManager.channelLength = channelLengthValues[j]
                for _ in range(n_tests):
                    self.simManager.simLoop()
                    dumpeningQBERResults[i][j] += self.simManager.bob.qber
                    self.simManager.clearLists()
                dumpeningQBERResults[i][j] /= n_tests

        df = pd.DataFrame(
            dumpeningQBERResults,
            index=dumpeningValues,
            columns=channelLengthValues
        )
        self.logger.important(f"Average QBER depending on dumpening and channel length:\n{df}")

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
        plt.savefig(self.data_path + "dumpeningAnalysis.png", dpi=300)
        plt.show()

    def baseTransformAnalysis(self, baseTransformValues: list[float], channelLengthValues: list[float],
                              n_tests: int = 5) -> None:
        """
            Simulates QKD for specified baseTransform and channel length parameters and shows average QBERs
            :param simManager: simulation Manager
            :param baseTransformValues: List of tested base transform values
            :param channelLengthValues: List of tested channel lengths
            :param n_tests: Number of tests for a given pair of parameters
        """
        self.simManager.__init__()
        self.simManager.ifEve = False
        n: int = len(baseTransformValues)
        m: int = len(channelLengthValues)
        baseTransformValues = sorted(baseTransformValues)
        channelLengthValues = sorted(channelLengthValues)
        baseTransformQBERResults: list[list[float]] = [[0 for _ in range(m)] for _ in range(n)]

        self.logger.important(f"==== Starting Base Transform Parameter Dependence Analysis for {n_tests} times")

        for i in range(n):
            self.simManager.base_transform_per_km = baseTransformValues[i]
            for j in range(m):
                self.simManager.channelLength = channelLengthValues[j]
                for _ in range(n_tests):
                    self.simManager.simLoop()
                    baseTransformQBERResults[i][j] += self.simManager.bob.qber
                    self.simManager.clearLists()
                baseTransformQBERResults[i][j] /= n_tests

        df = pd.DataFrame(
            baseTransformQBERResults,
            index=baseTransformValues,
            columns=channelLengthValues
        )
        self.logger.important(f"Average QBER depending on base transform and channel length:\n{df}")

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
        plt.savefig(self.data_path + "/baseTransformAnalysis.png", dpi=300)
        plt.show()

    def bobsErrorEffiecencyAnalysis(self, errorValues: list[float], efficiencyValues: list[float],
                                    n_tests: int = 5) -> None:
        """
            Simulates QKD for specified error and eficiency parameters and shows average QBERs
            :param simManager: simulation Manager
            :param errorValues: List of tested error values
            :param efficiencyValues: List of tested efficiency values
            :param n_tests: Number of tests for a given pair of parameters
        """
        self.simManager.__init__()
        self.simManager.ifEve = False
        n: int = len(errorValues)
        m: int = len(efficiencyValues)
        errorValues = sorted(errorValues)
        efficiencyValues = sorted(efficiencyValues)
        errorQBERResults: list[list[float]] = [[0 for _ in range(m)] for _ in range(n)]

        self.logger.important(f"==== Starting Bob's Error Parameter Dependence Analysis for {n_tests} times")

        for i in range(n):
            self.simManager.bob.error = errorValues[i]
            for j in range(m):
                self.simManager.bob.efficiency = efficiencyValues[j]
                for _ in range(n_tests):
                    self.simManager.simLoop()
                    errorQBERResults[i][j] += self.simManager.bob.qber
                    self.simManager.clearLists()
                errorQBERResults[i][j] /= n_tests

        df = pd.DataFrame(
            errorQBERResults,
            index=errorValues,
            columns=efficiencyValues
        )
        self.logger.important(f"Average QBER depending on error and efficiency:\n{df}")

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
        plt.savefig(self.data_path + "/bobsErrorEffiecencyAnalysis.png", dpi=300)
        plt.show()
