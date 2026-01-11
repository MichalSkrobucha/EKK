from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon
from random import randint, binomialvariate, shuffle
from QKD_Algorithms.Common import Bob


class BobBB84(Bob):
    def __init__(self, channel: Channel, efficiency: float, error: float, logger: SimLogger) -> None:
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param efficiency: How often detectors react to photons (properly)
        :param error: How often detectors click without photon
        """
        super().__init__(channel, efficiency, error, logger)

    def sendBases(self) -> list[int]:
        """
        Returns bases in which he measured bits of key
        :return: List of bases (in chronological order)
        """
        self.logger.log("Bob sent his bases to Alice")
        return self.bases

    def receiveBases(self, bases: list[int]) -> None:
        """
        Get's Alice's bases in which she send bits of key
        :param bases: Alice's bases (in chronological order)
        """
        self.aliceBases = bases
        self.logger.log(f"Bob is recieving bases from Alice {bases}")

    def sieveBits(self) -> None:
        """
        Sieves key bits based on his and Alice's bases
        """
        i: int = 0

        for (a, b, bit) in zip(self.aliceBases, self.bases, self.bits):
            if a == b:
                self.sievedBits.append(bit)

        self.logger.log(
            f"Bob sieved his measurments (based on his and Alice's bases) and got {len(self.sievedBits)} bits: {self.sievedBits}")
