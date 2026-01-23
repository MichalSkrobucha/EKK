from auth_alice import alice
from auth_bob import bob
from auth_eve import eve

from math import ceil, floor


class channel:
    def __init__(self, M: int, T: int, hashes: list[tuple[int, int]], qr: tuple[int, int], iters):
        self.alice: alice = alice(qr, M, T)
        self.bob: bob = bob(qr, M, T)
        print(f'Alice and Bob have secret hash of (q,r): {qr[0], qr[1]}')
        print(f'In total there are {len(hashes)} possible hashes\n')

        self.eve: eve = eve(M, T, hashes)

        self.T: int = T
        self.iters = iters

    def run(self):
        for _ in range(self.iters):
            mt: tuple[int, int] = self.alice.send_message()

            print(f'Alice sends message to Bob: {mt[0]} with tag {mt[1]}')

            if self.bob.recieve_message(mt):
                print(f'Bob positively verifies message')
            else:
                print(f'Bob negatively verifies message - End of transmission')
                return

            self.eve.eavesdrop(mt)
            print(f'Eve eavesdropps on (message, tag) pair')

            print('\n')

        self.eve.narrow_possible_hashes()

        alice_unused_messages: list[int] = self.alice.possible_messages

        guessed_mt: tuple[int, int] = (0, 0)
        prob: float = 0.0

        (guessed_mt, prob) = self.eve.guess_tag_for_message_of_your_choice(alice_unused_messages)

        print(f'Eve tries to fake message-tag : {guessed_mt[0], guessed_mt[1]}')
        print(f'She estimates that probability of success is {prob}')
        print(f'Probability if she guessed randomly: {1 / self.T}')

        correct_tag: int = self.bob.h(guessed_mt[0])

        print(f'Correct tag is {correct_tag}')

        if correct_tag == guessed_mt[1]:
            print(f'Eve guessed correctly - she suceeds')
        else:
            print(f'Bob guessed wrong - she loses')
