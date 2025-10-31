from Channel import Channel
from Logger import SimLogger

logger = SimLogger()


class Eve:
    channel: Channel

    def __init__(self, channel: Channel):
        self.channel = channel
