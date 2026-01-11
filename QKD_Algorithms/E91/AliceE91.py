import random
from .Channel import Channel
from .Photon import Photon


class AliceE91:
    channel: Channel
    bases: dict = {}
    results: list[dict] = []

    def __init__(self, channel: Channel, bases: dict):
        self.channel = channel
        self.channel.name = "channel_A"
        self.bases = bases

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            photon: Photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx = random.choice([1, 2, 3])
            base = self.bases[base_idx]
            bit = photon.measure(base)
            self.results.append({'base_idx': base_idx, 'base': base, 'bit': bit})