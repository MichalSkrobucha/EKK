from typing import override
from Common.Alice import Alice
from numpy.random import poisson
from random import randint
from Common.Photon import Photon
from Logger import SimLogger
from Common.Channel import Channel


class AliceSARG(Alice):
    """
    """
    def __init__(self, mi: float, channel: Channel, photon_factory, logger: SimLogger):
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param mi: Average amount of photons in impulse
        """
        super().__init__(mi, channel, photon_factory, logger)
        self.possibleStates: list[tuple[int, int]] = []
        self.sendBases: list[int] = []
        self.keyBits: list[int] = []

    @override
    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.message.clear()
        self.possibleStates.clear()
        self.bits.clear()
        self.sendBases.clear()
        self.keyBits.clear()

        self.aliceSample.clear()
        self.bobSample.clear()
        self.sampleIds.clear()

    @override
    def _generate_key(self) -> list[Photon]:
        """
        Generates next bit of key, and returns impulse of photons
        :return: impulse of photons
        """
        n_photons: int = poisson(self.mi)
        photons_list = []

        bitComputational: int = randint(0, 1)
        bitHadamard: int = 1 - bitComputational
        self.possibleStates.append((bitComputational, bitHadamard))
        sendBase: int = randint(0, 1)
        self.sendBases.append(sendBase)
        sendBit: int = bitHadamard if sendBase else bitComputational
        self.bits.append(sendBit)

        for _ in range(n_photons):
            photons_list.append(Photon(sendBase, sendBit))
            self.logger.log(f">>> Photon: [{sendBase}, {sendBit}]")

        self.message.extend(photons_list)
        self.logger.log(f"Alice generated {n_photons} photons")
        return photons_list

    def announceStates(self) -> list[tuple[int, int]]:  # list[tuple[int,int]] - 1 baza prostokatna )bit, 2 - bit z Hadamarda
        """
        Anounces pair of possible states of the Photon
        :return:
        """
        return self.possibleStates

    def getUsedStates(self, states: list[int]) -> None:
        for i in states:
            self.keyBits.append(self.possibleStates[i][self.sendBases[i]])
        self.logger.log(f'Alice got {len(self.keyBits)} bits of key')
