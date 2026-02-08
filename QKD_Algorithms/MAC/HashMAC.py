from sympy import nextprime as nxtpr, mod_inverse as modinv


class HashMAC:
    # basically only classes that needed nextprime and mod_inv are those that already need hash
    @staticmethod
    def next_prime(M: int) -> int:
        return nxtpr(M)

    @staticmethod
    def mod_inv(x: int, p: int) -> int:
        return modinv(x, p)

    @staticmethod
    def find_eq_prob_hashes(M : int, T: int) -> list[tuple[int, int]]:
        pass

    def __init__(self, M: int, T: int, q: int, r: int, p: int | None = None):
        self.p: int = p if p else self.next_prime(M)
        self.T: int = T
        self.q: int = q
        self.r: int = r

    def inv(self, x: int) -> int:
        return self.mod_inv(x, self.p)

    def hash(self, m: int) -> int:
        return ((m * self.q + self.r) % self.p) % self.T

    def __call__(self, m: int) -> int:
        return self.hash(m)
