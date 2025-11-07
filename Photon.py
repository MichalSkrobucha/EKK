from random import randint


class Photon:
    def __init__(self, base: int, bit: int) -> None:
        """
        :param base: 0 - prostokatna, 1 - ukośna
        :param bit: 0 - poziomo/skos w prawo , 1 - pionowo/skos w lewo
        """
        self.base: int = base
        self.bit: int = bit

    def measure(self, base: int) -> int:
        if self.base == base:
            return self.bit
        else:
            return randint(0, 1)

    def eavsdrop(self, base: int) -> int:
        # gdy ewa mierzy w złej bazie zmienia ją (na tą pomiarową) i bit (na losowy)
        if self.base != base:
            self.base = base
            self.bit = randint(0, 1)
        return self.bit

