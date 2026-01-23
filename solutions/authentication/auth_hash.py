class hash:

    @staticmethod
    def next_prime(M : int) -> int:
        return 17

    def __init__(self, M : int, T: int, q : int, r : int):
        self.p : int = self.next_prime(M)
        self.T : int = T
        self.q : int = q
        self.r : int = r

    def hash(self, m: int) -> int:
        return ((m * self.q + self.r) % self.p) % self.T