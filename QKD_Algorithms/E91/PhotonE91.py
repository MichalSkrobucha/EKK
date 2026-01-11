from random import randint
from EntanglementController import EntanglemetController


class PhotonE91:
    def __init__(self) -> None:
        """
        :param base: 0-360 - base expressed in degrees
        :param bit: 0 - vertical/diagonal to right (| /), 1 - horizontal/diagonal to left (_ \\)   (respecitvely in + and x basis)
        """
        self.base: int | None = None  # base is defined by measure, otherwise it is unknown
        self.bit: int | None = None  # bit is defined by measure, otherwise it is unknown

        self.controller: EntanglemetController | None = None

    def measure(self, base: int) -> int:
        bit: int = -1

        if self.base:
            if base == self.base:
                bit = self.bit
            else:
                bit = randint(0, 1)
        else:
            bit = self.controller.measure_photon(self, base)
            self.bit = bit
            self.base = base

        return bit
