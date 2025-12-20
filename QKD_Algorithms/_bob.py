from _channel import _channel


class _bob:
    bases: list[int]
    bits: list[int]
    sievedBits: list[int]
    channel: _channel

    def __init__(self, channel: _channel, efficinecy: float = 0.99, error: float = 0.01) -> None:
        pass

    def clearLists(self):
        self.bases.clear()
        self.bits.clear()
        self.sievedBits.clear()

    def recieve_impulse(self):
        raise NotImplemented

    def send_info(self):
        raise NotImplemented

    def recieve_info(self):
        raise NotImplemented

    def sendSampleIds(self) -> list[int]:
        pass

    def sendSample(self):
        pass

    def recieveSample(self):
        pass

    def calculateQber(self, threshold: float):
        pass
