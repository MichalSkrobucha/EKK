from E91.Alice import Alice
from E91.Bob import Bob
from E91.Channel import Channel
from E91.Source import Source
from Logger import SimLogger
import math
from itertools import combinations
import numpy as np

logger = SimLogger()


class SimManager:
    sim_start: int = 0
    sim_step: int = 1
    sim_end: int = 100
    qberThreshhold: float = 0.2
    ifEve: bool = True
    logs: bool = True

    BASES_ALICE = {1: 0, 2: 22.5, 3: 45}
    BASES_BOB = {1: 22.5, 2: 45, 3: 67.5}

    def __init__(self):
        self.channel_alice = Channel()
        self.channel_bob = Channel()

        self.alice = Alice(self.channel_alice, self.BASES_ALICE)
        self.bob = Bob(self.channel_bob, self.BASES_BOB)
        logger.set_time(self.sim_start)

    def simLoop(self):
        """
        Simulates QKD (du-uh)
        """
        source = Source()

        for step in range(self.sim_start, self.sim_end, self.sim_step):
            # Alice sends bits (impulses of photons) to Bob
            logger.msg(f"=====================")
            logger.set_time(step)
            # Generating pair
            photon_A, photon_B = source.generate_pair()
            self.channel_alice.send([photon_A])
            self.channel_bob.send([photon_B])

            self.alice.receive()
            self.bob.receive()

        print("\n________________________")
        print("--- EKSPERYMENTALNIE ---")
        print("________________________")
        self.analyze_results()
        print("\n____________________")
        print("--- TEORETYCZNIE ---")
        print("____________________\n")
        self.theoretical_result()

    def analyze_results(self):  # Eksperymentalnie liczona nierówność Bella
        """
        Faza Sifting i Testu Bella.
        Alicja i Bob ujawniają bazy i sortują wyniki.
        """
        raw_key_alice = []
        raw_key_bob = []

        # Do obliczenia statystyk CHSH (liczba zgodnych i niezgodnych wyników dla danych par baz)
        # Klucz słownika: (AliceBase, BobBase), Wartość: [zgodne, niezgodne]
        stats = {}
        alice_results = self.alice.results
        bob_results = self.bob.results

        for a,b in zip(alice_results, bob_results):
            # Para baz użyta w tej rundzie
            pair_key = (a['base_idx'], b['base_idx'])

            # KEY GENERATION

            # Alice and Bob used same bases
            if a['base'] == b['base']:
                raw_key_alice.append(a['bit'])
                # W stanie splątanym wyniki są przeciwne. Bob musi odwrócić swój bit, by mieć to samo co Alicja.
                raw_key_bob.append(1 - b['bit'])

            # BELL TEST - CHSH inequality
            # Zliczanie korelacji dla wszystkich kombinacji
            if pair_key not in stats:
                stats[pair_key] = {'same': 0, 'diff': 0}

            if a['bit'] == b['bit']:
                stats[pair_key]['same'] += 1
            else:
                stats[pair_key]['diff'] += 1

        print(f"\nWygenerowano surowy klucz o długości: {len(raw_key_alice)} bitów")
        print(f"Klucz Alicji: {raw_key_alice}")
        print(f"Klucz Boba:   {raw_key_bob}")

        # Wzór na E: E = (N_same - N_diff) / (N_same + N_diff)
        def get_E(idx_a, idx_b):
            key = (idx_a, idx_b)
            if key not in stats: return 0
            s = stats[key]['same']
            d = stats[key]['diff']
            if s + d == 0: return 0
            return (s - d) / (s + d)

        E_A1_B1 = get_E(1, 1)
        E_A1_B3 = get_E(1, 3)
        E_A3_B1 = get_E(3, 1)
        E_A3_B3 = get_E(3, 3)

        # Wzór na S dla zestawu kątów A1, A3, B1, B3:
        # S = |E(A1, B1) - E(A1, B3) + E(A3, B1) + E(A3, B3)|
        S = abs(E_A1_B1 - E_A1_B3 + E_A3_B1 + E_A3_B3)

        print("\n--- Test Nierówności Bella (CHSH) ---")
        print(f"E(A1, B1) = {E_A1_B1:.4f}    Bases: {self.alice.bases[1]}, {self.bob.bases[1]}")
        print(f"E(A1, B3) = {E_A1_B3:.4f}    Bases: {self.alice.bases[1]}, {self.bob.bases[3]}")
        print(f"E(A3, B1) = {E_A3_B1:.4f}    Bases: {self.alice.bases[3]}, {self.bob.bases[1]}")
        print(f"E(A3, B3) = {E_A3_B3:.4f}    Bases: {self.alice.bases[3]}, {self.bob.bases[3]}")
        print(f"Wartość parametru S = {S:.4f}")

        if S > 2.0:
            print(">> SUKCES: Nierówność Bella złamana! (Bezpieczeństwo potwierdzone)")
        else:
            print(">> OSTRZEŻENIE: Brak kwantowych korelacji lub zbyt duży szum.")

    def theoretical_result(self):
        def get_theoretical_E(angle_a_deg, angle_b_deg):
            theta_A = math.radians(angle_a_deg)
            theta_B = math.radians(angle_b_deg)

            delta = theta_A - theta_B
            return -math.cos(2 * delta)

        def get_S_for_pair(base_idx_1, base_idx_2):
            val_A1_B1 = get_theoretical_E(self.alice.bases[base_idx_1], self.bob.bases[base_idx_1])
            val_A1_B2 = get_theoretical_E(self.alice.bases[base_idx_1], self.bob.bases[base_idx_2])
            val_A2_B1 = get_theoretical_E(self.alice.bases[base_idx_2], self.bob.bases[base_idx_1])
            val_A2_B2 = get_theoretical_E(self.alice.bases[base_idx_2], self.bob.bases[base_idx_2])

            print(f"E(A{base_idx_1}, B{base_idx_1}) [{self.alice.bases[base_idx_1]} vs {self.bob.bases[base_idx_1]}]  = {val_A1_B1:.4f}")
            print(f"E(A{base_idx_1}, B{base_idx_2}) [{self.alice.bases[base_idx_1]} vs {self.bob.bases[base_idx_2]}]  = {val_A1_B2:.4f}")
            print(f"E(A{base_idx_2}, B{base_idx_1}) [{self.alice.bases[base_idx_2]} vs {self.bob.bases[base_idx_1]}] = {val_A2_B1:.4f}")
            print(f"E(A{base_idx_2}, B{base_idx_2}) [{self.alice.bases[base_idx_2]} vs {self.bob.bases[base_idx_2]}] = {val_A2_B2:.4f}")

            # S = |E(A1, B1) - E(A1, B3) + E(A3, B1) + E(A3, B3)|
            S_theoretical = abs(val_A1_B1 - val_A1_B2 + val_A2_B1 + val_A2_B2)
            print(f"Teoretyczne S ({self.alice.bases[base_idx_1]},{self.alice.bases[base_idx_2]}) = {S_theoretical:.5f}\n")
            return S_theoretical

        def find_max_S():
            indices = [1, 2, 3]
            results = {}
            for idx1, idx2 in combinations(indices, 2):
                s_val = get_S_for_pair(idx1, idx2)
                results[(idx1, idx2)] = s_val

            best_pair = max(results, key=results.get)
            max_S = results[best_pair]
            print(f"\n>>> ZWYCIĘZCA: Para indeksów {best_pair}")
            print(f">>> Maksymalne S = {max_S:.5f}")
            return max_S

        if find_max_S() > 2:
            print("\n>> SUKCES: Wynik łamie nierówność Bella.")
        else:
            print("\n>> UWAGA: Coś nie tak z kątami.")