from .Photon import Photon
from random import randint, random


class EntanglemetController:
    def __init__(self, photons: list[Photon], distribution: list[float]):
        self.photons: list[Photon] = photons
        self.distribution: list[float] = distribution

        for ph in self.photons:
            ph.controller = self

    def measure_photon(self, photon: Photon):
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