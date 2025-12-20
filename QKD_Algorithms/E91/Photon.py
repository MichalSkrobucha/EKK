from random import randint, random


class Photon:
    def __init__(self) -> None:
        """
        :param base: 0-360 - base expressed in degrees
        :param bit: 0 - vertical/diagonal to right (| /), 1 - horizontal/diagonal to left (_ \\)   (respecitvely in + and x basis)
        """
        self.base: int | None = None  # base is defined by measure, otherwise it is unknown
        self.bit: int | None = None  # bit is defined by measure, otherwise it is unknown

        self.controller: Entanglemet_Controller | None = None

    def measure(self, base: int) -> int:
        bit: int = -1

        if self.base:
            if base == self.base:
                bit = self.bit
            else:
                bit = randint(0, 1)
        else:
            bit = self.controller.measure_photon(self, base)
            self.bit = bit
            self.base = base

        return bit


class Entanglemet_Controller:
    def __init__(self, photons: list[Photon], distribution: list[float]):
        self.photons: list[Photon] = photons
        self.distribution: list[float] = distribution

        for ph in self.photons:
            ph.controller = self

    def measure_photon(self, photon: Photon, base: int):
        id = self.photons.index(photon)
        self.photons.remove(photon)

        # states in which given photon has given value
        states0: list[float] = []
        states1: list[float] = []

        # probability of photon having value
        p0: float = 0.0
        p1: float = 0.0

        for (state, p) in enumerate(self.distribution):
            bit_in_state: int = (state // (2 ** id)) % 2

            if bit_in_state == 0:
                p0 += p
                states0 += [p]
            else:
                p1 += p
                states1 += [p]

        bit: int = 1

        if random() <= p0:
            bit = 0

        s: float = 0.0

        if bit == 0:
            s = sum(states0)
            self.distribution = states0
        else:
            s = sum(states1)
            self.distribution = states1

        for i in range(len(self.distribution)):
            self.distribution[i] = self.distribution[i] / s

        return bit
