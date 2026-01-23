from typing import override
from Common.Bob import Bob
from Logger import SimLogger
from Common.Channel import Channel
from math import ceil


class BobSARG(Bob):
    def __init__(self, efficiency: float, error: float, channel: Channel, logger: SimLogger) -> None:
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param efficiency: How often detectors react to photons (properly)
        :param error: How often detectors click without photon
        """
        super().__init__(efficiency, error, channel, logger)
        self.aliceStates: list[tuple[int, int]] = []  # 1st - computational basis, 2nd - Hadamard basis
        self.keyIDs: list[int] = []

    @override
    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.bases.clear()
        self.bits.clear()
        self.aliceStates.clear()
        self.keyIDs.clear()
        self.sampleIds.clear()
        self.aliceSample.clear()
        self.bobSample.clear()

    def recieveStates(self, states: list[tuple[int, int]]) -> None:
        self.aliceStates = states

    def sieveStates(self) -> None:
        for (i, (bit, base, alice)) in enumerate(zip(self.bits, self.bases, self.aliceStates)):
            if base != -1:
                # Bob's measured base has different bit than Alice -> it was the other bit
                if alice[base] != bit:
                    self.keyIDs.append(i)
                    self.keyBits.append(alice[1 - base])
        self.logger.log(f'Bob got {len(self.keyBits)} bits of key')

    def announceUsedStates(self) -> list[int]:
        return self.keyIDs
