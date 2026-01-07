from random import randint

from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon

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
        self.sieved_bits: list[int] = []

        self.photons: list[Photon | None] = []
        self.after_sieving = False

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.bits.clear()
        self.bases.clear()
        self.sieved_bits.clear()

        self.photons.clear()

    def eavesdrop(self) -> None:
        """
        Eavesdrops on impulse ALice sent to Bob
        """

        if self.after_sieving:
            container: list[Photon] = self.channel.container

            match len(container):
                case 0:
                    logger.log('Eve detected no photons on channel')
                    self.photons.append(None)
                case 1:
                    logger.log('Eve detected only one photon on channel - it will not pass')
                    container.clear()
                    self.photons.append(None)
                case _:
                    logger.log('Eve detected many photons on channel - she keeps one')
                    self.photons.append(container.pop())

        else:
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

    def eavesdrop_bases(self, basesA: list[int], basesB: list[int]) -> None:
        """
        Eavesdrops on base exchange (and sieves her bits)
        :param basesA: Alice's basis
        :param basesB: Bob;s basis
        """

        logger.log('Eve is eavesdropping on base exchange')

        if self.after_sieving:
            for (a, b, ph) in zip(basesA, basesB, self.photons):
                if a == b:
                    if ph is not None:
                        self.sieved_bits.append(ph.measure(a))
                    else:
                        self.sieved_bits.append(-1)
        else:
            for (a, b, bases, bits) in zip(basesA, basesB, self.bases, self.bits):

                # Eve knows Alice and Bob will use this bit to make key
                if a == b:
                    # She looks through her list to find matching one
                    for (base, bit) in zip(bases, bits):
                        # She found one of matching base
                        if base == a:
                            self.sieved_bits.append(bit)
                            break
                    # She does not have matching base (unknown bit)
                    else:
                        self.sieved_bits.append(-1)

    def print_sieved_bits(self) -> None:
        """
        Prints bits Eve has sieved (for debug)
        """
        logger.log(f'Eve has {len(self.sieved_bits)} bits: {self.sieved_bits}')
        logger.log(f'Out of which she does not know {len([p for p in self.sieved_bits if p == -1])} of them')
