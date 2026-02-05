from auth_alice import alice
from auth_bob import bob
from auth_eve import eve
from auth_hash import hash
from random import choice, shuffle


class channel:
    m_exp: int = 4
    t_exp: int = 2
    M: int = 2 ** m_exp
    T: int = 2 ** t_exp

    eq_prob_tolerance: int = 0

    given_mts: int = 2
    eve_forgeries: int = 2

    def __init__(self, m_exp: int = 4, t_exp: int = 2, eq_prob_tolerance: int = 0, given_mts: int = 2,
                 eve_forgeries: int = 2):
        self.M = 2 ** m_exp
        self.T = 2 ** t_exp

        self.eq_prob_tolerance = eq_prob_tolerance
        self.given_mts = given_mts
        self.eve_forgeries = eve_forgeries

        self.p: int = hash.next_prime(self.M)
        self.possible_messages: list[int] = [m for m in range(self.M)]

        possible_hashes: list[tuple[int, int]] = self.find_possible_hashes()
        self.possible_hashes = possible_hashes
        qr: tuple[int, int] = choice(possible_hashes)

        h: hash = hash(self.M, self.T, qr[0], qr[1], self.p)

        self.alice: alice = alice(h, list(self.possible_messages))
        self.bob: bob = bob(h)
        # print(f'Alice and Bob have secret hash of (q,r): {qr[0], qr[1]}')
        # print(f'In total there are {len(possible_hashes)} possible hashes\n')

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
        for _ in range(self.given_mts):
            mt: tuple[int, int] = self.alice.send_message()
            self.eve.eavesdrop(mt)

            # print(f'Alice sends message to Bob: {mt[0]} with tag {mt[1]}')
            # if self.bob.recieve_message(mt):
            #     print(f'Bob positively verifies message')
            # else:
            #     print(f'Bob negatively verifies message - End of transmission')
            #     return
            # print(f'Eve eavesdropps on (message, tag) pair\n')

        alice_unused_messages: list[int] = self.alice.possible_messages
        shuffle(alice_unused_messages)
        messages_to_forge: list[int] = alice_unused_messages[:min(self.eve_forgeries, len(alice_unused_messages))]

        self.eve.narrow_possible_hashes()
        print(len(self.eve.possible_hashes), self.eve.possible_hashes)

        # co gdy len == 1 (Ewa złamała hash) - nie trzeba dalszej analizy

        fakes: list[tuple[int, int]] = self.eve.forge_mtags(messages_to_forge)

        for (m, t) in fakes:
            print(m, t, self.alice.h(m), t == self.alice.h(m))
