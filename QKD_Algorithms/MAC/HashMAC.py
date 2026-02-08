from sympy import nextprime as nxtpr, mod_inverse as modinv


class HashMAC:
    # basically only classes that needed nextprime and mod_inv are those that already need hash

    @staticmethod
    @staticmethod
    def next_prime(M: int) -> int:
        return nxtpr(M)

    @staticmethod
    def mod_inv(x: int, p: int) -> int:
        return modinv(x, p)

    @staticmethod
    def find_eq_prob_hashes(M: int, T: int, p: int | None = None, eq_prob_tolerance=0) -> list[tuple[int, int]]:
        if p is None:
            p = HashMAC.next_prime(M)

        eq_prob: int = M // T

        possible_messages = [m for m in range(M)]

        possible_hashes: list[tuple[int, int]] = []

        h: HashMAC = HashMAC(M, T, 0, 0, p)

        for q in range(1, p):
            for r in range(p):
                h.q = q
                h.r = r

                t_ctr: dict[int, int] = {i: 0 for i in range(T)}
                diff: int = 0

                for m in possible_messages:
                    t_ctr[h(m)] += 1

                for v in t_ctr.values():
                    diff += abs(v - eq_prob)

                if diff <= eq_prob_tolerance:
                    possible_hashes.append((q, r))

        return possible_hashes

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
