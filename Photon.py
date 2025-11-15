from random import randint


class Photon:
    def __init__(self, base: int, bit: int) -> None:
        """
        :param base: 0 - computational base (+), 1 - Hadamard base (x)
        :param bit: 0 - vertical/diagonal to right (| /), 1 - horizontal/diagonal to left (_ \)   (respecitvely in + and x basis)
        """
        self.base: int = base
        self.bit: int = bit

    def measure(self, base: int) -> int:
        """
        'Measures' the photon in given base. If base is the same as photon's - returns proper bit. If not - returns random bit.
        :param base: base in which photon is measured (0 for +, 1 for x)
        :return: photon's bit, depending on it's 'true bit' and whether measurment was done in corect base
        """
        if self.base == base:
            return self.bit
        else:
            return randint(0, 1)

    def eavesdrop(self, base: int) -> int:
        """
        'Eavesdrops' the photon in given base. If base is the same as photon's - returns proper bit. If not - returns random bit and changes base to measured (and bit to the returned one)
        :param base: base in which photon is measured (0 for +, 1 for x)
        :return: photon's bit, depending on it's 'true bit' and whether measurment was done in corect base
        """
        if self.base != base:
            self.base = base
            self.bit = randint(0, 1)
        return self.bit
