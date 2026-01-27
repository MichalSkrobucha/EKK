from typing import override

from .ChannelE91 import ChannelE91 as Channel
import random
from Logger import SimLogger
from .PhotonE91 import PhotonE91 as Photon
from Common.Bob import Bob


class BobE91(Bob):
    bases: dict = {}
    results: list[dict] = []

    def __init__(self, bases: dict, channel: Channel, logger: SimLogger):
        super().__init__(0, 0, channel, logger)
        self.channel.name = "channel_B"
        self.bases: dict = bases

    @override
    def clearLists(self) -> None:
        super().clearLists()
        self.results.clear()

    def _choose_base(self):
        base_idx = random.choice([1, 2, 3])
        return base_idx, self.bases[base_idx]

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx, angle = self._choose_base()
            bit = photon.measure(angle)
            self.results.append({'base_idx': base_idx, 'base': angle, 'bit': bit})
