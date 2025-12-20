from _channel import _channel


class _alice:
    bases: list[int]
    bits: list[int]
    sievedBits: list[int]
    channel: _channel

    def __init__(self, channel: _channel, mi: float = 0.5) -> None:
        pass

    def clearLists(self):
        self.bases.clear()
        self.bits.clear()
        self.sievedBits.clear()

    def generate_key(self):
        raise NotImplemented

    def send_impulse(self):
        raise NotImplemented

    def send_info(self):
        raise NotImplemented

    def recieve_info(self):
        raise NotImplemented

    def getSampleIds(self, ids: list[int]):
        pass

    def sendSample(self):
        pass

    def recieveSample(self):
        pass

    def calculateQber(self, threshold: float):
        pass
