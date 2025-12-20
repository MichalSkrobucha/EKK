from _channel import _channel


class _eve:
    bases: list[int]
    bits: list[int]
    sievedBits: list[int]
    channel: _channel

    def __init__(self, channel: _channel) -> None:
        pass

    def clearLists(self):
        self.bases.clear()
        self.bits.clear()
        self.sievedBits.clear()

    def eavesdrop_impulse(self):
        raise NotImplemented

    def eavesdrop_info(self):
        raise NotImplemented
