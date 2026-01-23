from error_correction_alice import alice
from error_correction_bob import bob
from random import randint, random
from math import ceil

class channel:
    def __init__(self, n=512, pb=0.95, pe=0.6):
        bits = [randint(0, 1) for _ in range(n)]

        self.pb: float = pb

        self.alice = alice(bits[:], 1 - pb)
        self.bob = bob([bit if random() < pb else (1 - bit) for bit in bits], 1 - pb)

    def peek_keys(self):
        n = len(self.alice.bits)
        bob_correct: int = sum([1 for (a, b) in zip(self.alice.bits, self.bob.bits) if a == b])

        print(f'A: {''.join([str(bit) for bit in self.alice.bits])}')
        print(f'B: {''.join([str(bit) for bit in self.bob.bits])}')
        print(f'Bob has {bob_correct} correct bits (out of {len(self.bob.bits)}) ({bob_correct / n :.4f})\n'
              f'~SimMaster\n')

    def run_error_correction(self):

        print('\n--- ERROR CORRECTION ---\n')

        alice = self.alice
        bob = self.bob

        # korekcja błędów
        # Alicja i Bob wymieniają się informacjami, ewa słucha (w teorii - brak wywołań funkcji)

        # Alicja wysyła klucz
        alice_key_hash = alice.send_key_hash()
        bob.get_key_hash(alice_key_hash)
        print(f'Alice\'s key hash: {alice_key_hash.hex()}\n')

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
            if bob.check_hash():
                print('Key hashes match - end of error correction\n'
                      f'Bob has {sum([1 for (a, b) in zip(alice.bits, bob.bits) if a == b])} correct bits (~SimMaster)\n'
                      f'{'Both keys are the same' if all([a == b for (a, b) in zip(alice.bits, bob.bits)]) else 'Keys are not the same'}')
                break

            print('Key hashes don\'t match - next iteration of error correction\n\n')

    def run_privacy_amplification(self):

        print('\n--- PRIVACY AMPLIFICATION ---\n')

        alice = self.alice
        bob = self.bob

        print(f'Alice and Bob have {len(self.alice.bits)} bits\n')

        # estywamcja bezpieczeńśtwa klucza
        qber: float = 1 - self.pb
        n: int = len(self.alice.bits)

        ###
        eves_known_bits: int = ceil(qber * n)
        security_bits : int = n - eves_known_bits

        print(f'Estimated bits known by Eve: {eves_known_bits}\n'
              f'Esitmated secuirty provided by key: {security_bits} bits\n')

        # wzmocnienie prywatności
        r_bytes: bytes = alice.send_random_bytes()
        bob.get_random_bytes(r_bytes)

        print(f'Alice send random bytes ({alice.bytes_count}): {alice.random_bytes.hex()}\n')

        alice.get_final_key()
        bob.get_final_key()

        print('Alice and Bob calculate final key')

        print(f'A: {alice.key.hex()}\n'
              f'B: {bob.key.hex()}\n'
              f'Keys match: {alice.key == bob.key}')
