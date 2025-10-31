from Logger import SimLogger
from Photon import Photon
from random import random

logger = SimLogger()


class Channel:
    """
    tłumienie (pochłananie, transformowanie?)
    """
    l: float = 0.0
    container: list[Photon] = []

    def __init__(self, l: float):
        self.l: float = l

    def send(self, photons: list[Photon]) -> None:
        """Dodaje do kanału listę fotonów"""
        self.container.clear()
        self.container.extend(photons)
        logger.log(f"Channel received {len(self.container)} photons")

    def read(self) -> list[Photon]:
        """Zwraca listę fotonów w kanale z tłumieniem"""
        transmited = [photon for photon in self.container if random() > self.l]
        logger.log(f"Channel output: {len(transmited)} photons have been read")
        return transmited
