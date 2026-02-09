from .PhotonE91 import PhotonE91 as Photon
from .PhotonE91 import SharedState
from random import random
from math import sqrt

class Source:
    def __init__(self, n: int = 2, p: float = 1.0):
        self.n = n
        self.p = p
        self.message = []

    def generate(self) -> tuple[Photon, ...]:
        r = random()
        if r <= self.p:
            # entangled
            shared_context = SharedState(n=self.n, amp0=1.0 / sqrt(2), amp1=1.0 / sqrt(2))

            photons = [Photon(shared_state=shared_context) for _ in range(self.n)]
            self.message.extend(photons)
        else:
            # separable
            photons = []
            for _ in range(self.n):
                independent_state = SharedState(n=1, amp0=1.0 / sqrt(2), amp1=1.0 / sqrt(2))
                photons.append(Photon(shared_state=independent_state))
            self.message.extend(photons)
        return tuple(photons)

    def clearLists(self):
        self.message.clear()

