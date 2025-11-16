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
        Adds list of photons (impulse) to channel (where they are (optionally) dumpened and their basis are transformed)
        :param photons: Alice's photon impulse
        """
        self.container.clear()

        # dumpening
        transmited: list[Photon] = [p for p in photons if random() > self.dumpening]

        # base change
        trasmitted_transformed: list[Photon] = []
        for p in transmited:
            if random() > self.base_transform:
                trasmitted_transformed.append(p)
            else:
                trasmitted_transformed.append(Photon(1 - p.base, randint(0, 1)))

        self.container.extend(trasmitted_transformed)

        logger.log(f"Channel received {len(self.container)} photons")

    def read(self) -> list[Photon]:
        """
        Return list of photons
        :return modified impulse
        """
        logger.log(f"Channel output: {len(self.container)} photons have been read")
        return list(self.container)

    def eavesdrop(self, base: int) -> tuple[list[int], list[int]]:
        """
        Eavesdrops on channel (measurment with possible base change if done in incorrect base)
        :param base: bas ein which Eve eavesdrop on impulse (if there is only 1 photon)
        :return: tuple(bases, bits)
            bases - bases in which photonsd are measured
            bits - measured bits
        """
        # Eaves measures photon and send it
        # To simplify simulation photon does not leave list (impulse)

        # self.container

        bases: list[int] = []
        bits: list[int] = []

        match len(self.container):
            case 0:
                bases.append(-1)
                bits.append(-1)
            case 1:
                photon: Photon = self.container[0]
                bases.append(base)
                bits.append(photon.eavesdrop(base))
            case 2:
                photon: Photon = self.container.pop()
                bases.append(base)
                bits.append(photon.eavesdrop(base))
                bases.append(1 - base)
                bits.append(self.container[0].eavesdrop(1 - base))
            case _:
                photonA : Photon = self.container.pop()
                photonB : Photon = self.container.pop()
                bases.append(base)
                bits.append(photonA.eavesdrop(base))
                bases.append(1 - base)
                bits.append(photonB.eavesdrop(1 - base))

        return (bases, bits)
