from random import randint

from Channel import Channel
from Logger import SimLogger

logger = SimLogger()


class Eve:
    channel: Channel

    def __init__(self, channel: Channel):
        self.channel = channel
        self.bits : list[int] = []
        self.bases: list[int] = []
        self.sieved_bits : list[int] = []

    def eavesdrop(self):
        logger.log('Eve eavesdrops on transmission')
        base: int = randint(0,1)
        bit = self.channel.eavesdrop(base)

        self.bases.append(base)
        self.bits.append(bit)

        if bit >= 0:
            logger.log(f'Eve measured photon in base {base} and got bit {bit}')
        else:
            logger.log('Eve couldn\'t make a measurment')

    def eavesdrop_bases(self, basesA: list[int], basesB: list[int]):
        logger.log('Eve is eavesdropping on base exchange')
        for (a,b, bit) in zip(basesA, basesB, self.bits):
            if a == b:
                self.sieved_bits.append(bit)

    def print_sieved_bits(self):
        logger.log(f'Eve has {len(self.sieved_bits)} bits: {self.sieved_bits}')
        logger.log(f'Out of which she does not know {len([p for p in self.sieved_bits if p == -1])} of them')


