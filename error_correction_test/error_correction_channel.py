from error_correction_alice import alice
from error_correction_bob import bob
from error_correction_eve import eve
from random import randint, random

class channel:
    def __init__(self, n=256, pb=0.75, pe=0.6):
        bits = [randint(0, 1) for _ in range(n)]

        self.alice = alice(bits[:])
        self.bob = bob([bit if random() < pb else (1 - bit) for bit in bits])
        self.eve = eve([bit if random() < pe else (-1) for bit in bits])

    def peek_keys(self):
        n = len(self.alice.bits)
        bob_correct : int = sum([1 for (a, b) in zip(self.alice.bits, self.bob.bits) if a == b])
        eve_has : int = sum([1 for e in self.eve.bits if e != -1])

        print(f'A: {self.alice.bits}')
        print(f'B: {self.bob.bits}')
        print(f'E: {self.eve.bits}')
        print(f'Bob has {bob_correct} bits ({bob_correct / n :.4f})\n'
              f'Eve knows {eve_has} bits ({eve_has / n :.4f})')

    def run(self):
        # korekcja błędów
        # Alicja i Bob wymieniają się informacjami, ewa słucha
        # (spróbuje złamać dopiero na koniec - łatwiej w(y)łączyć w symulacji)
        while True:
            break
            pass
            # permutacja

            # podział na bloki

            # obliczenia parzystości
            #   rekurencyjnie

            # sprawdzenie poprawności (może być po przelecienie odpowiedniej liczby rund)


        # eve.attack()

        # sprawdzenie poprawności
        # all[a == b for (a, b) in zip(alice.key_bits, bob.key_bits)]