from MAC.AliceMAC import AliceMAC as alice
from MAC.BobMAC import BobMAC as bob
from MAC.EveMAC import EveMAC as eve
from MAC.HashMAC import HashMAC as Hash
from random import choice, shuffle

# ALL LOGIC MOVED TO SIMMANAGER_MAC


class ChannelMAC:
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

        self.p: int = Hash.next_prime(self.M)
        self.possible_messages: list[int] = [m for m in range(self.M)]

        possible_hashes: list[tuple[int, int]] = Hash.find_eq_prob_hashes(self.M, self.T)
        self.possible_hashes = possible_hashes
        qr: tuple[int, int] = choice(possible_hashes)

        h: hash = Hash(self.M, self.T, qr[0], qr[1], self.p)

        self.alice: alice = alice(h, list(self.possible_messages))
        self.bob: bob = bob(h)
        print(f'Alice and Bob have secret hash of (q,r): {qr[0], qr[1]}')
        print(f'In total there are {len(possible_hashes)} possible hashes\n')

        self.eve: eve = eve(self.M, self.T, self.p, possible_hashes)

    def run(self):
        for _ in range(self.given_mts):
            mt: tuple[int, int] = self.alice.send_message()

            print(f'Alice sends message to Bob: {mt[0]} with tag {mt[1]}')
            if self.bob.recieve_message(mt):
                print(f'Bob positively verifies message')
            else:
                print(f'Bob negatively verifies message - End of transmission')
                return

            print(f'Eve eavesdropps on (message, tag) pair\n')
            self.eve.eavesdrop(mt)

        self.eve.narrow_possible_hashes()
        print(len(self.eve.possible_hashes), self.eve.possible_hashes)

        alice_unused_messages: list[int] = self.alice.possible_messages
        shuffle(alice_unused_messages)
        messages_to_forge: list[int] = alice_unused_messages[:min(self.eve_forgeries, len(alice_unused_messages))]

        print(f'Eve is given messages to forge tags:\n{messages_to_forge}')

        fakes: list[tuple[int, int]] = self.eve.forge_mtags(messages_to_forge)
        print(f'Eve attempted tag forgery')

        print('Message | Correct Tag | Eve\'s tag | Comparison')

        succ: int = 0

        for (m, t) in fakes:
            print(m, t, self.alice.h(m), t == self.alice.h(m))
            if t == self.alice.h(m):
                succ += 1

        print(f'\nEve succeded in {100 * succ / len(fakes) :.2f}% of cases')
