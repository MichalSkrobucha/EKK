from abc import abstractmethod
from random import randint

from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon


class Eve:
    channel: Channel

    def __init__(self, channel: Channel, logger: SimLogger):
        """
        :param channel: Channel on which Alice and Bob are communicating
        """
        self.logger = logger

        self.channel = channel
        self.bits: list[list[int]] = []
        self.bases: list[list[int]] = []

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.bits.clear()
        self.bases.clear()

    @abstractmethod
    def eavesdrop(self) -> None:
        """

        :return:
        """
        pass
