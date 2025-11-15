from Logger import SimLogger
from Photon import Photon
from random import random, randint

logger = SimLogger()


class Channel:
    l: float = 0.0
    container: list[Photon] = []

    def __init__(self, dumpening: float, base_transform: float):
        """
        :param dumpening: How often photon disappears
        :param base_transform: How often photon changes basis (and bit to random)
        """
        self.dumpening: float = dumpening
        self.base_transform: float = base_transform

    def send(self, photons: list[Photon]) -> None:
        """
        Adds list of photons (impulse) to channel
        :param photons: Alice's photon impulse
        """
        self.container.clear()
        self.container.extend(photons)
        logger.log(f"Channel received {len(self.container)} photons")

    def read(self) -> list[Photon]:
        """
        Return list of photons (after dumpening and change of base)
        :return modified impulse
        """
        # dumpening
        transmited: list[Photon] = [p for p in self.container if random() > self.dumpening]

        # base change
        trasmitted_transformed: list[Photon] = []
        for p in transmited:
            if random() > self.base_transform:
                trasmitted_transformed.append(p)
            else:
                trasmitted_transformed.append(Photon(1 - p.base, randint(0, 1)))

        logger.log(f"Channel output: {len(trasmitted_transformed)} photons have been read")
        return trasmitted_transformed

    def eavesdrop(self, base: int) -> int:
        """
        Eavesdrops on channel (measurment with possible base change if done in incorrect base)
        :param base: bas ein which Eve eavesdrop on impulse
        :return: photon's bit (change if measured in wrong base)
        """
        # Eaves measures photon and send it
        # To simplify simulation photon does not leave list (impulse)
        if len(self.container) > 0:
            p: Photon = self.container[0]
            bit: int = p.eavesdrop(base)
            return bit
        else:
            return -1
