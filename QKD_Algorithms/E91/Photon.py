import random
import math


class Photon:
    def __init__(self) -> None:
        """
        :param base: 0-360 - base expressed in degrees
        :param bit: 0 - vertical/diagonal to right (| /), 1 - horizontal/diagonal to left (_ \\)   (respecitvely in + and x basis)
        """
        self.base: int | None = None  # base is defined by measure, otherwise it is unknown
        self.bit: int | None = None  # bit is defined by measure, otherwise it is unknown
        self.partner: Photon | None = None

    def set_entangled_pair(self, other_photon) -> None:
        self.partner = other_photon
        other_photon.partner = self

    def measure(self, base: int) -> int:
        """
        'Measures' the photon in given base. If base is the same as photon's - returns proper bit. If not - returns random bit.
        :param base: base in which photon is measured (0 for +, 1 for x)
        :return: photon's bit, depending on it's 'true bit' and whether measurment was done in corect base
        """
        self.base = base
        # CASE 1 - Partner hasn't been measured yet.
        # Bit value is random 50/50
        if self.partner.bit is None:
            self.bit = random.choice([0, 1])
        # CASE 2 - Parent was measured.
        # Bit depends on partner
        else:
            delta_theta = math.radians(self.base - self.partner.base)
            # Prawdopodobieństwo uzyskania RÓŻNEGO wyniku niż partner:
            prob_different = (math.cos(delta_theta)) ** 2

            if random.random() < prob_different:
                self.bit = 1 - self.partner.bit  # Wynik przeciwny do partnera
            else:
                self.bit = self.partner.bit  # Wynik ten sam co partner

        return self.bit
