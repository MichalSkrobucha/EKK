from auth_hash import hash
from random import choice


class eve:
    def __init__(self, M: int, T: int, hashes: list[tuple[int, int]]):
        self.M: int = M
        self.T: int = T

        self.possible_hashes: list[tuple[int, int]] = hashes
        self.eavesdropped_mt: list[tuple[int, int]] = []

    def eavesdrop(self, mt: tuple[int, int]):
        for emt in self.eavesdropped_mt:
            if emt[0] == mt[0]:
                return
        else:
            self.eavesdropped_mt.append(mt)

    def narrow_possible_hashes(self):
        possible_hashes: list[tuple[int, int]] = []

        for (q, r) in self.possible_hashes:
            h: hash = hash(self.M, self.T, q, r)

            for (m, t) in self.eavesdropped_mt:
                if h(m) != t:
                    break
                else:
                    pass
            else:
                possible_hashes.append((q, r))

        self.possible_hashes = possible_hashes

    def guess_tag_for_given_message(self, m: int) -> tuple[tuple[int, int], float]:
        possible_tags: dict[int, int] = {t: 0 for t in range(self.T)}
        total_count: int = 0

        for (q, r) in self.possible_hashes:
            possible_tags[hash(self.M, self.T, q, r)(m)] += 1
            total_count += 1

        max_val: int = max(possible_tags.items(), key=lambda tc: tc[1])[1]

        tags: list[int] = [t for (t, c) in possible_tags.items() if c == max_val]

        return ((m, choice(tags)), max_val / total_count)

    def guess_tag_for_message_of_your_choice(self, alice_unused_messages: list[int]) -> tuple[tuple[int, int], float]:
        possible_pairs: list[tuple[int, int]] = []
        max_prob: float = 0.0

        for m in alice_unused_messages:
            mt: tuple[int, int] = (0, 0)
            prob: float = 0.0

            (mt, prob) = self.guess_tag_for_given_message(m)

            if prob > max_prob:
                max_prob = prob
                possible_pairs = [mt]
            elif prob == max_prob:
                possible_pairs.append(mt)

        return (choice(possible_pairs), max_prob)
