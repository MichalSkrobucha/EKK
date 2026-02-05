from random import randint, random

from math import cos, radians


class PhotonE91:
    def __init__(self) -> None:
        """
        :param polarisation: 0-360 - base expressed in degrees
        """
        self.polarisation: float | None = None
        self.entagled: list['Photon'] = []

    def measure(self, base: float) -> int:
        """
        bit: 0 - if measurment is like given base (0, 22.5, 45, 67.5), 1 - if orthogonal (90, 112.5, 135, 157.5)
        """
        if self.polarisation is None:
            b: int = randint(0, 1)

            if b == 0:
                self.polarisation = base
            else:
                self.polarisation = base + 90.0

            for ph in self.entagled:
                ph.set_polarisation(self.polarisation, self)

            return b

        else:
            if self.polarisation == base:
                return 0
            else:
                sq_cos: float = cos(radians(self.polarisation - base)) ** 2
                r: float = random()

                if r <= sq_cos:
                    # measured same as base
                    self.polarisation = base
                    return 0
                else:
                    self.polarisation = base + 90.0
                    return 1

    def entangle(self, others: list['Photon']) -> None:
        self.entagled = list(others)

        try:
            self.entagled.remove(self)
        except:
            pass

    def set_polarisation(self, polarisation: float, ph: 'Photon') -> None:
        if self.polarisation is None:
            self.polarisation = polarisation

        try:
            self.entagled.remove(ph)
        except:
            pass
