from _photon import _photon
from random import random, randint


class _channel:
    def __init__(self, dumpening_ae: float, dumpening_eb: float, base_transform_ae: float,
                 base_transform_eb: float) -> None:
        self.dumpening_ae: float = dumpening_ae
        self.dumpening_eb: float = dumpening_eb
        self.base_transform_ae: float = base_transform_ae
        self.base_transform_eb: float = base_transform_eb

        self.container: list[_photon] = []

    def send(self, photons: list[_photon]) -> None:
        # dumpening
        send_container: list[_photon] = [p for p in photons if random() > self.dumpening_ae]

        # base change
        send_container_transformed: list[_photon] = []
        for p in send_container:
            if random() < self.base_transform_ae:
                p.base = 1 - p.base
                p.bit = randint(0, 1)
            send_container_transformed.append(p)

        self.container = send_container_transformed

    def recieve(self) -> list[_photon]:
        # dumpening
        read_container: list[_photon] = [p for p in self.container if random() > self.dumpening_ae]
        self.container.clear()

        # base change
        read_container_transformed: list[_photon] = []
        for p in read_container:
            if random() < self.base_transform_ae:
                p.base = 1 - p.base
                p.bit = randint(0, 1)
            read_container_transformed.append(p)

        return read_container_transformed

    def eavesdrop(self, base: int) -> tuple[list[int], list[int]]:
        bases: list[int] = []
        bits: list[int] = []

        match len(self.container):
            case 0:
                bases.append(-1)
                bits.append(-1)
            case 1:
                photon: _photon = self.container[0]
                bases.append(base)
                bits.append(photon.eavesdrop(base))
            case 2:
                photon: _photon = self.container.pop()
                bases.append(base)
                bits.append(photon.eavesdrop(base))
                bases.append(1 - base)
                bits.append(self.container[0].eavesdrop(1 - base))
            case _:
                photonA: _photon = self.container.pop()
                photonB: _photon = self.container.pop()
                bases.append(base)
                bits.append(photonA.eavesdrop(base))
                bases.append(1 - base)
                bits.append(photonB.eavesdrop(1 - base))

        return (bases, bits)

    # E91
    # def send(self, photons: list[Photon]) -> None:
    #     """
    #     Adds list of photons (impulse) to channel (where they are (optionally) dumpened and their basis are transformed)
    #     :param photons: Alice's photon impulse
    #     """
    #     self.container.extend(photons)
    #     logger.log(f"Channel {self.name} received {len(self.container)} photons")
    #
    # def read(self) -> list[Photon]:
    #     """
    #     Return list of photons
    #     """
    #     # Płytka kopia listy (list slicing) - przekazuje te same obiekty fotonów
    #     read_container = self.container[:]
    #     self.container.clear()
    #     logger.log(f"Channel {self.name} output: {len(read_container)} photons have been read")
    #     return read_container
