from random import randint
from typing import override

from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon
from QKD_Algorithms.Common import Eve


class EveBB84(Eve):
    def __init__(self, channel: Channel, logger: SimLogger):
        """
        :param channel: Channel on which Alice and Bob are communicating
        """
        super().__init__(channel, logger)
        self.logger = logger
        self.sieved_bits: list[int] = []

        self.photons: list[Photon | None] = []
        self.after_sieving = False

    @override
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
                    self.logger.log('Eve detected no photons on channel')
                    self.photons.append(None)
                case 1:
                    self.logger.log('Eve detected only one photon on channel - it will not pass')
                    container.clear()
                    self.photons.append(None)
                case _:
                    self.logger.log('Eve detected many photons on channel - she keeps one')
                    self.photons.append(container.pop())

        else:
            self.logger.log('Eve eavesdrops on transmission')
            base: int = randint(0, 1)

            bases: list[int]
            bits: list[int]

            (bases, bits) = self.channel.eavesdrop(base)

            self.bases.append(bases)
            self.bits.append(bits)

            self.logger.log(f'Eve eavesdrops on transmission and measured {len(bases)} photons')

            for (base, bit) in zip(bases, bits):
                if bit >= 0:
                    self.logger.log(f'Eve measured photon in base {base} and got bit {bit}')
                else:
                    self.logger.log('Eve couldn\'t make a measurment')
