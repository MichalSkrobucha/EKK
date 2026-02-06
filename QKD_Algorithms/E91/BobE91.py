from typing import override

from .ChannelE91 import ChannelE91 as Channel
import random
from Logger import SimLogger
from .PhotonE91 import PhotonE91 as Photon
from Common.Bob import Bob


class BobE91(Bob):
    results: list[dict] = []

    def __init__(self, avaliable_bases, bases_dict,channel: Channel, logger: SimLogger):
        super().__init__(0, 0, channel, logger)
        self.channel.name = "channel_B"
        self.avaliable_bases = avaliable_bases
        self.bases_dict = bases_dict

    @override
    def clearLists(self) -> None:
        super().clearLists()
        self.results.clear()

    def _choose_base(self):
        base_idx = random.choice([1, 2, 3])
        return base_idx, self.bases[base_idx]

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            photon: Photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx = random.choice(self.avaliable_bases)
            base = self.bases_dict[base_idx]
            bit = photon.measure(base)

            self.logger.log(f'Bob measured bit {bit} in base {base_idx}')

            self.results.append({'base_idx': base_idx, 'base': base, 'bit': bit})
