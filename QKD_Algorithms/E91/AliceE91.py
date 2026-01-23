from .ChannelE91 import ChannelE91 as Channel
from Logger import SimLogger
import random
from .PhotonE91 import PhotonE91 as Photon
from Common.Alice import Alice


class AliceE91(Alice):
    bases: dict = {}
    results: list[dict] = []

    def __init__(self, bases: dict, channel: Channel, logger: SimLogger):
        super().__init__(0, channel, None, logger)
        self.channel.name = "channel_A"
        self.bases: dict = bases

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            photon: Photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx = random.choice([1, 2, 3])
            base = self.bases[base_idx]
            bit = photon.measure(base)
            self.results.append({'base_idx': base_idx, 'base': base, 'bit': bit})
