from Logger import SimLogger
from Photon import Photon
from random import random, randint

logger = SimLogger()


class Channel:
    """
    tłumienie (pochłananie, transformowanie?)
    """
    l: float = 0.0
    container: list[Photon] = []

    def __init__(self, dumpening: float, base_transform: float):
        self.dumpening: float = dumpening
        self.base_transform : float = base_transform

    def send(self, photons: list[Photon]) -> None:
        """Dodaje do kanału listę fotonów"""
        self.container.clear()
        self.container.extend(photons)
        logger.log(f"Channel received {len(self.container)} photons")

    def read(self) -> list[Photon]:
        """Zwraca listę fotonów w kanale z tłumieniem"""
        # tłumienie
        transmited : list[Photon] = [p for p in self.container if random() > self.dumpening]

        # zmiana bazy
        trasmitted_transformed : list[Photon] = []
        for p in transmited:
            if random() > self.base_transform:
                trasmitted_transformed.append(p)
            else:
                trasmitted_transformed.append(Photon(1 - p.base, randint(0, 1)))

        logger.log(f"Channel output: {len(trasmitted_transformed)} photons have been read")
        return trasmitted_transformed

    def eavesdrop(self, base: int) -> int:
        # Ewa mierzy foton i wysyła go dalej
        # dla uproszczenia symulacji, foton nie opuszcza pakietu
        if len(self.container) > 0:
            p : Photon = self.container[0]
            bit: int = p.eavesdrop(base)
            return bit
        else:
            return -1

