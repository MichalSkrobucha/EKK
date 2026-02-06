from typing import override

from .ChannelE91 import ChannelE91 as Channel
from Logger import SimLogger
import random
from .PhotonE91 import PhotonE91 as Photon
from Common.Alice import Alice


class AliceE91(Alice):
    results: list[dict] = []

    def __init__(self, avaliable_bases, bases_dict, channel: Channel, logger: SimLogger):
        super().__init__(0, channel, None, logger)
        self.channel.name = "channel_A"
        self.avaliable_bases = avaliable_bases
        self.bases_dict = bases_dict

    @override
    def clearLists(self):
        super().clearLists()
        self.results.clear()

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            photon: Photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx = random.choice(self.avaliable_bases)
            base = self.bases_dict[base_idx]
            bit = photon.measure(base)

            self.logger.log(f'Alice measured bit {bit} in base {base_idx}')

            self.results.append({'base_idx': base_idx, 'base': base, 'bit': bit})
