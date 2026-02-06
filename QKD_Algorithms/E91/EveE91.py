from .ChannelE91 import ChannelE91 as Channel
from .PhotonE91 import PhotonE91 as Photon
from Logger import SimLogger

from random import choice


class EveE91:
    def __init__(self, avaliable_bases, bases_dict, channel: Channel, logger: SimLogger):
        self.channel = channel
        self.channel.name = "channel_E"
        self.avaliable_bases = avaliable_bases
        self.bases_dict = bases_dict

        self.bases_A: list = []
        self.bases_B: list = []

        self.photons: list[Photon] = []
        self.measures: list[tuple[int, int]] = []

        self.key = []

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            self.photons.append(self.channel.read()[0])

    def receive_and_measure(self) -> None:
        if len(self.channel.container) > 0:
            photon: Photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx = choice(self.avaliable_bases)
            base = self.bases_dict[base_idx]
            bit = photon.measure(base)
            self.measures.append((bit, base_idx))

    def eavsdrop_bases(self, baseA, baseB):
        self.bases_A.append(baseA)
        self.bases_B.append(baseB)

    def sieve(self):
        for (a, b, m) in zip(self.bases_A, self.bases_B, self.measures):
            if a == b:
                if m[1] == a:
                    self.key.append(m[0])
                else:
                    self.key.append(-1)

    def sieve_and_measure(self):
        for (a, b, p) in zip(self.bases_A, self.bases_B, self.photons):
            if a == b:
                bit = p.measure(self.bases_dict[a])
                self.key.append(bit)
