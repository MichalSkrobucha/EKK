from random import randint

from SARG04.Channel import Channel
from Logger import SimLogger

logger = SimLogger()


class Eve:
    channel: Channel

    def __init__(self, channel: Channel):
        """
        :param channel: Channel on which Alice and Bob are communicating
        """
        self.channel = channel
        self.bits: list[list[int]] = []
        self.bases: list[list[int]] = []

        self.aliceStates: list[tuple[int, int]] = []
        self.keyBits: list[int] = []

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.bits.clear()
        self.bases.clear()
        self.aliceStates.clear()
        self.keyBits.clear()

    def eavesdrop(self) -> None:
        """
        Eavesdrops on impulse ALice sent to Bob
        """
        logger.log('Eve eavesdrops on transmission')
        base: int = randint(0, 1)

        bases: list[int]
        bits: list[int]

        (bases, bits) = self.channel.eavesdrop(base)

        self.bases.append(bases)
        self.bits.append(bits)

        logger.log(f'Eve eavesdrops on transmission and measured {len(bases)} photons')

        for (base, bit) in zip(bases, bits):
            if bit >= 0:
                logger.log(f'Eve measured photon in base {base} and got bit {bit}')
            else:
                logger.log('Eve couldn\'t make a measurment')

    def eavesdropStates(self, states: list[tuple[int, int]]) -> None:
       self.aliceStates = states
       logger.log(f'Eve eavsdrops on Alice possible states')


    def eavsdropUsedStates(self, usedStates:list[int]) -> None:
        for i in usedStates:
            if len(self.bits[i]) > 0:
                aliceStates: tuple[int, int] = self.aliceStates[i]
                usedBases: list[int] = self.bases[i]
                gotBits: list[int] = self.bits[i]

                bitFound: bool = False

                for (bit, base) in zip(gotBits, usedBases):
                    if base != -1:
                        if bit != aliceStates[base]:
                            self.keyBits.append(aliceStates[1 - base])
                            # correct bit found
                            bitFound = True
                            break

                if bitFound:
                    continue
                # no bit found
                self.keyBits.append(-1)
            else:
                self.keyBits.append(-1)

        logger.log(f'Eve eavsdrops on Alice possible States')
        logger.log(f'Eve got {len(self.keyBits)} bits of key, out of which she knows only {len([bit for bit in self.keyBits if bit >= 0])}')