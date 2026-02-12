from MAC.HashMAC import HashMAC as Hash
from collections import Counter
from random import choice, shuffle


class EveMAC:
    def __init__(self, M: int, T: int, p: int, possible_hashes: list[tuple[int, int]]):
        self.M: int = M
        self.T: int = T
        self.p: int = p

        self.possible_hashes: set[tuple[int, int]] = set(possible_hashes)
        self.eavesdropped_mt: list[tuple[int, int]] = []
        self.mt_pairs: set[tuple[tuple[int, int], tuple[int, int]]] = set()

        self.hash: hash = Hash(M, T, 0, 0, p)

    def eavesdrop(self, mt: tuple[int, int]):
        for emt in self.eavesdropped_mt:
            if emt[0] == mt[0]:
                return
        else:
            self.eavesdropped_mt.append(mt)

    def gen_mt_pairs(self):
        for i in range(len(self.eavesdropped_mt)):
            mt1 = self.eavesdropped_mt[i]
            for j in range(i + 1, len(self.eavesdropped_mt)):
                mt2 = self.eavesdropped_mt[j]

                self.mt_pairs.add((mt1, mt2))

    def narrow_possible_hashes(self):
        ctr: int = 1

        self.gen_mt_pairs()

        for (mt1, mt2) in self.mt_pairs:
            possible_qrs: set[tuple[int, int]] = set()

            for k1 in range(mt1[1], self.p, self.T):
                for k2 in range(mt2[1], self.p, self.T):
                    # if k1 == k2:
                    #     continue

                    dk: int = k2 - k1
                    dm: int = (mt2[0] - mt1[0]) % self.p

                    q: int = (dk * Hash.mod_inv(dm, self.p)) % self.p
                    r: int = (k1 - q * mt1[0]) % self.p

                    possible_qrs.add((q, r))

            self.possible_hashes &= possible_qrs
            # print(
            #     f'After comparing mt-pair n.{ctr} of mts Eve narrow count possible hashes to {len(self.possible_hashes)}')

            if len(self.possible_hashes) == 1:
                return ctr

            ctr += 1

    def forge_mtags(self, messages: list[int]) -> list[tuple[int, int]]:
        # zwraca od najprawdopodobniejszych do najmniej prawdopodobnych

        forgeries: list[[tuple[tuple[int, int], float]]] = []

        for m in messages:
            possible_tags: list[int] = [Hash(self.M, self.T, q, r, self.p)(m) for (q, r) in self.possible_hashes]

            if len(possible_tags) == 1:
                forgeries.append(((m, possible_tags[0]), 1.0))
            else:
                ctr: Counter = Counter(possible_tags)
                max_count: int = max(ctr.values())

                guesses: list[int] = [k for (k, v) in ctr.items() if v == max_count]
                forgeries.append(((m, choice(guesses)), max_count / len(possible_tags)))

        shuffle(forgeries)

        forgeries.sort(key=lambda x: x[1], reverse=True)

        return [mt for (mt, p) in forgeries]
