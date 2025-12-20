from random import randint, random


class Photon:
    def __init__(self) -> None:
        """
        :param base: 0-360 - base expressed in degrees
        :param bit: 0 - vertical/diagonal to right (| /), 1 - horizontal/diagonal to left (_ \\)   (respecitvely in + and x basis)
        """
        self.base: int | None = None  # base is defined by measure, otherwise it is unknown
        self.bit: int | None = None  # bit is defined by measure, otherwise it is unknown
        # self.partner: Photon | None = None

        self.controller: Entanglemet_Controller | None = None

    # def set_entangled_pair(self, other_photon) -> None:
    #     self.partner = other_photon
    #     other_photon.partner = self

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
        # """
        # 'Measures' the photon in given base. If base is the same as photon's - returns proper bit. If not - returns random bit.
        # :param base: base in which photon is measured (0 for +, 1 for x)
        # :return: photon's bit, depending on it's 'true bit' and whether measurment was done in corect base
        # """
        # self.base = base
        # # CASE 1 - Partner hasn't been measured yet.
        # # Bit value is random 50/50
        # if self.partner.bit is None:
        #     self.bit = random.choice([0, 1])
        # # CASE 2 - Parent was measured.
        # # Bit depends on partner
        # else:
        #     delta_theta = math.radians(self.base - self.partner.base)
        #     # Prawdopodobieństwo uzyskania RÓŻNEGO wyniku niż partner:
        #     prob_different = (math.cos(delta_theta)) ** 2
        #
        #     if random.random() < prob_different:
        #         self.bit = 1 - self.partner.bit  # Wynik przeciwny do partnera
        #     else:
        #         self.bit = self.partner.bit  # Wynik ten sam co partner
        #
        # return self.bit


class Entanglemet_Controller:
    def __init__(self, photons: list[Photon], distribution: list[float]):
        self.photons: list[Photon] = photons
        self.distribution: list[float] = distribution

        for ph in self.photons:
            ph.controller = self

    def measure_photon(self, photon: Photon, base: int):
        id = self.photons.index(photon)
        self.photons.remove(photon)

        # states in which given photon has given value
        states0: list[float] = []
        states1: list[float] = []

        # probability of photon having value
        p0: float = 0.0
        p1: float = 0.0

        for (state, p) in enumerate(self.distribution):
            bit_in_state: int = (state // (2 ** id)) % 2

            if bit_in_state == 0:
                p0 += p
                states0 += [p]
            else:
                p1 += p
                states1 += [p]

        bit: int = 1

        if random() <= p0:
            bit = 0

        s: float = 0.0

        if bit == 0:
            s = sum(states0)
            self.distribution = states0
        else:
            s = sum(states1)
            self.distribution = states1

        for i in range(len(self.distribution)):
            self.distribution[i] = self.distribution[i] / s

        return bit
