from error_correction_alice import alice
from error_correction_bob import bob
from error_correction_eve import eve
from random import randint, random


class channel:
    def __init__(self, n=512, pb=0.95, pe=0.6):
        bits = [randint(0, 1) for _ in range(n)]

        self.alice = alice(bits[:], 1 - pb)
        self.bob = bob([bit if random() < pb else (1 - bit) for bit in bits], 1 - pb)
        self.eve = eve([bit if random() < pe else (-1) for bit in bits])

    def peek_keys(self):
        n = len(self.alice.bits)
        bob_correct: int = sum([1 for (a, b) in zip(self.alice.bits, self.bob.bits) if a == b])
        eve_known: int = sum([1 for e in self.eve.bits if e != -1])

        print(f'A: {''.join([str(bit) for bit in self.alice.bits])}')
        print(f'B: {''.join([str(bit) for bit in self.bob.bits])}')
        print(f'E: {''.join([str(bit) if bit >= 0 else 'x' for bit in self.eve.bits])}')
        print(f'Bob has {bob_correct} bits ({bob_correct / n :.4f})\n'
              f'Eve knows {eve_known} bits ({eve_known / n :.4f})\n'
              f'~SimMaster\n')

    def run(self):
        alice = self.alice
        bob = self.bob
        # eve = self.eve

        # korekcja błędów
        # Alicja i Bob wymieniają się informacjami, ewa słucha (w teorii - brak wywołań funkcji)

        # Alicja wysyła klucz
        alice_key_hash = alice.send_key_hash()
        bob.get_key_hash(alice_key_hash)
        print(f'Alice\'s key hash: {alice_key_hash.hex()}')

        while True:
            # permutacja
            permutation: list[int] = alice.permute()
            bob.get_alice_permutation(permutation)

            print(f'Alice permutes her bits using permutation {permutation}\n'
                  f'And gets bits {''.join([str(bit) for bit in self.alice.bits])}\n'
                  f'Bob has bits {''.join([str(bit) for bit in self.bob.bits])}\n'
                  f'Bob has {sum([1 for (a, b) in zip(alice.bits, bob.bits) if a == b])} correct bits (~SimMaster)\n')

            # podział na bloki
            alice.split_into_blocks()
            bob.split_into_blocks()

            print(f'Alice and Bob split their bits into blocks of length {alice.n}\n')

            # obliczenia parzystości
            alice_parities = alice.compute_parity_bits()
            bob_parities = bob.compute_parity_bits()
            matching_parities: bool = all([a == b for (a, b) in zip(alice_parities, bob_parities)])

            print(f'Alice and Bob exchange blocks parities\n'
                  f'Alice\'s parities: {''.join([str(bit) for bit in alice_parities])}\n'
                  f'Bob\'s parities: {''.join([str(bit) for bit in bob_parities])}\n'
                  f'{'All parities match' if matching_parities else 'There are parities that do not match - need of recursive correction'}\n')

            #   rekurencyjnie
            while not matching_parities:
                alice.get_bobs_parity(bob_parities)
                bob.get_alice_parity(alice_parities)

                alice_parities = alice.compute_parity_bits()
                bob_parities = bob.compute_parity_bits()
                matching_parities: bool = all([a == b for (a, b) in zip(alice_parities, bob_parities)])

                print(f'Alice and Bob exchange blocks parities\n'
                      f'Alice\'s parities: {''.join([str(bit) for bit in alice_parities])}\n'
                      f'Bob\'s parities: {''.join([str(bit) for bit in bob_parities])}\n'
                      f'{'All parities match' if matching_parities else 'There are parities that do not match - next round of recursive correction'}\n')

            bob.flatten_blocks()

            # permutacja odwrotna
            alice.unpermute()
            bob.unpermute()

            # sprawdzenie poprawności
            if bob.check_hash(alice_key_hash):
                print('Key hashes match - end of error correction\n'
                      f'Bob has {sum([1 for (a, b) in zip(alice.bits, bob.bits) if a == b])} correct bits (~SimMaster)\n'
                      f'{'Both keys are the same' if all([a == b for (a, b) in zip(alice.bits, bob.bits)]) else 'Keys are not the same'}')
                break

            print('Key hashes don\'t match - next iteration of error correction\n\n')
