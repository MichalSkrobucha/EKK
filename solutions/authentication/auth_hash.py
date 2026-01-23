from sympy import nextprime as nxtpr
from sympy import mod_inverse as modinv


class hash:

    @staticmethod
    def next_prime(M: int) -> int:
        return nxtpr(M)

    @staticmethod
    def mod_inv(x: int, p: int) -> int:
        return modinv(x, p)

    def __init__(self, M: int, T: int, q: int, r: int, p: int | None = None):
        self.p: int = p if p else self.next_prime(M)
        self.T: int = T
        self.q: int = q
        self.r: int = r

    def hash(self, m: int) -> int:
        return ((m * self.q + self.r) % self.p) % self.T

    def inv(self, x: int) -> int:
        return self.mod_inv(x, self.p)

    def __call__(self, m: int) -> int:
        return self.hash(m)
