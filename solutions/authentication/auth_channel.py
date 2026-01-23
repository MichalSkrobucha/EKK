from auth_alice import alice
from auth_bob import bob
from auth_eve import eve
from auth_hash import hash

from random import choice


class channel:
    M: int = 2 ** 4
    T: int = 2 ** 2

    eq_prob_tolerance: int = 0

    iters: int = 0

    def __init__(self):
        self.p: int = hash.next_prime(self.M)
        self.possible_messages: list[int] = [m for m in range(self.M)]

        possible_hashes: list[tuple[int, int]] = self.find_possible_hashes()
        qr: tuple[int, int] = choice(possible_hashes)
        h: hash = hash(self.M, self.T, qr[0], qr[1], self.p)

        self.alice: alice = alice(h, self.possible_messages)
        self.bob: bob = bob(h)
        print(f'Alice and Bob have secret hash of (q,r): ({qr[0], qr[1]})')
        print(f'In total there are {len(possible_hashes)} possible hashes\n')

        self.eve: eve = eve(self.M, self.T, self.p, possible_hashes)

    def find_possible_hashes(self) -> list[tuple[int, int]]:
        eq_prob: int = self.M // self.T

        possible_hashes: list[tuple[int, int]] = []

        h: hash = hash(self.M, self.T, 0, 0, self.p)

        for q in range(1, self.p):
            for r in range(self.p):
                h.q = q
                h.r = r

                t_ctr: dict[int, int] = {i: 0 for i in range(self.T)}
                diff: int = 0

                for m in self.possible_messages:
                    t_ctr[h(m)] += 1

                for v in t_ctr.values():
                    diff += abs(v - eq_prob)

                if diff <= self.eq_prob_tolerance:
                    possible_hashes.append((q, r))

        return possible_hashes

    def run(self):
        for _ in range(self.iters):
            mt: tuple[int, int] = self.alice.send_message()

            # print(f'Alice sends message to Bob: {mt[0]} with tag {mt[1]}')
            # if self.bob.recieve_message(mt):
            #     print(f'Bob positively verifies message')
            # else:
            #     print(f'Bob negatively verifies message - End of transmission')
            #     return
            # print(f'Eve eavesdropps on (message, tag) pair\n')

            self.eve.eavesdrop(mt)

        self.eve.narrow_possible_hashes()

        guessed_mt: tuple[int, int]
        prob: float
        (guessed_mt, prob) = self.eve.guess_tag_for_message_of_your_choice(self.possible_messages)

        print(f'Eve tries to fake message-tag : {guessed_mt[0], guessed_mt[1]}')
        print(f'She estimates that probability of success is {prob}')
        print(f'Probability if she guessed randomly: {1 / self.T}')

        correct_tag: int = self.alice.h(guessed_mt[0])

        print(f'Correct tag is {correct_tag}')

        if correct_tag == guessed_mt[1]:
            print(f'Eve guessed correctly - she suceeds')
        else:
            print(f'Eve guessed wrong - she loses')
