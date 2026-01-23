from QKD_Algorithms.Logger import SimLogger
from ..Common import Alice


class AliceBB84(Alice):
    """

    """
    def __init__(self, mi: float, channel, photon_factory, logger):
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param mi: Average amount of photons in impulse
        """
        super().__init__(mi, channel, photon_factory, logger)

    def sendBases(self) -> list[int]:
        """
        Returns bases in which she send bits of key
        :return: List of bases (in chronological order)
        """
        self.logger.log("Alice sent bases")
        return self.bases

    def receiveBases(self, bases: list[int]) -> None:
        """
        Get's Bobs bases in which he measured bits of key
        :param bases: Bob's bases (in chronological order)
        """
        self.bobBases = bases
        self.logger.log(f"Alice received bases from Bob: {bases}")

    def sieveBits(self) -> None:
        """
        Sieves key bits based on her and Bob's bases
        """
        for (a, b, bit) in zip(self.bases, self.bobBases, self.bits):
            if a == b:
                self.sievedBits.append(bit)

        self.logger.log(
            f"Alice sieved her measurments (based on her and Bob's bases) and got {len(self.sievedBits)} bits: {self.sievedBits}")
