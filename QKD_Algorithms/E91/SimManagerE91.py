import math
from typing import override
from itertools import combinations
from DIContainers import E91Container
from Common.SimManager import SimManager
from Common.config import cfg


class SimManagerE91(SimManager):
    protocol: int = 91
    S: float = 2.0

    BASES_ALICE = cfg.e91.alice_bases
    BASES_BOB = cfg.e91.bob_bases

    def __init__(self):
        self._recalculate_channel_params()
        self.channel_alice = E91Container.channel_A()
        self.channel_bob = E91Container.channel_B()
        alice = E91Container.alice(self.BASES_ALICE)
        bob = E91Container.bob(self.BASES_BOB)
        self.source = E91Container.source()
        logger = E91Container.logger()

        super().__init__(None, alice, bob, None, logger, "E91")

    def simLoop(self):
        """
        Simulates QKD (du-uh)
        """
        self._initial_print()
        self.is_running = True
        while self.is_running:
            self.sim_next_step()
        self.is_running = False

    @override
    def _initial_print(self):
        self.logger.log(f'\n --- {self.protocol_name} Simulation ---'
                        f'> Channel Length: {self.channel_length} km\n'
                        f'> Dumpening per km: {self.dumpening_per_km} dB/km\n'
                        f'> Base transform rate: {self.base_transform_per_km} dB/km\n'
                        f'> Dumpening rate: {self.dumpening_dB} dB\n'
                        f'> Total base transform: {self.base_transform_per_km} dB\n'
                        f'> Total dumpening rate: {self.dumpening}\n'
                        f'> Base transform per km {self.base_transform_per_km}\n'
                        f'> QBER treshhold: {self.qberThreshhold}\n'
                        f'> If Eve is present: {self.ifEve}\n'
                        f'> Alice bases: {self.BASES_ALICE}\n'
                        f'> Bob bases: {self.BASES_BOB}\n')

    def sim_next_step(self):
        self.logger.set_time(self.sim_step)
        if self.sim_step == 0:
            self._initial_print()

        if self.sim_step < self.sim_end:
            self._sim_transmition_step()
            self.logger.msg(f"---")
        elif self.sim_step == self.sim_end:
            self.logger.msg(f"=====================")
            self._sim_analysis_step()
        else:
            self.is_running = False
            return
        self.sim_step += 1

    @override
    def _sim_transmition_step(self):
        # Generating pair
        photon_A, photon_B = self.source.generate()
        self.channel_alice.send([photon_A])
        self.channel_bob.send([photon_B])

        self.alice.receive()
        self.bob.receive()

    def _sim_analysis_step(self):
        print("\n________________________")
        print("--- EKSPERYMENTALNIE ---")
        print("________________________")
        self._analyze_results()
        print("\n____________________")
        print("--- TEORETYCZNIE ---")
        print("____________________\n")
        self._theoretical_result()

        self._run_error_correction()
        self._run_privacy_amplification()

    def _analyze_results(self):  # Eksperymentalnie liczona nierówność Bella
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

        for a, b in zip(alice_results, bob_results):
            # Para baz użyta w tej rundzie
            pair_key = (a['base_idx'], b['base_idx'])

            # KEY GENERATION

            # Alice and Bob used same bases
            if a['base'] == b['base']:
                raw_key_alice.append(a['bit'])
                raw_key_bob.append(b['bit'])

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

        self.alice.keyBits = raw_key_alice
        self.bob.keyBits = raw_key_bob

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

        self.S = S

    def _theoretical_result(self):
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

            print(
                f"E(A{base_idx_1}, B{base_idx_1}) [{self.alice.bases[base_idx_1]} vs {self.bob.bases[base_idx_1]}]  = {val_A1_B1:.4f}")
            print(
                f"E(A{base_idx_1}, B{base_idx_2}) [{self.alice.bases[base_idx_1]} vs {self.bob.bases[base_idx_2]}]  = {val_A1_B2:.4f}")
            print(
                f"E(A{base_idx_2}, B{base_idx_1}) [{self.alice.bases[base_idx_2]} vs {self.bob.bases[base_idx_1]}] = {val_A2_B1:.4f}")
            print(
                f"E(A{base_idx_2}, B{base_idx_2}) [{self.alice.bases[base_idx_2]} vs {self.bob.bases[base_idx_2]}] = {val_A2_B2:.4f}")

            # S = |E(A1, B1) - E(A1, B3) + E(A3, B1) + E(A3, B3)|
            S_theoretical = abs(val_A1_B1 - val_A1_B2 + val_A2_B1 + val_A2_B2)
            print(
                f"Teoretyczne S ({self.alice.bases[base_idx_1]},{self.alice.bases[base_idx_2]}) = {S_theoretical:.5f}\n")
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

    @override
    def update_setting(self, key: str, value):
        """Dynamiczna aktualizacja parametrów symulacji"""
        print(f"Updating setting: {key} -> {value}")

        if key == "qber_threshold":
            self.qberThreshhold = float(value) / 100.0

        elif key == "key_length":
            self.sim_end = int(value)

        elif key == "channel_length":
            self.channel_length = float(value)
            self._recalculate_channel_params()

        elif key == "dumpening":
            self.dumpening_per_km = float(value)
            self._recalculate_channel_params()

        elif key == "base_transform":  # Polaryzacja
            self.base_transform_per_km = float(value)
            self._recalculate_channel_params()

        elif key == "n_photons":
            if hasattr(self.source, 'n'):
                self.source.n = int(value)

        elif key == "distribution":
            if hasattr(self.source, 'distribution'):
                self.source.distribution = float(value)

        elif key == "alice_bases":
            if hasattr(self.alice, 'bases'):
                parts = value.replace(';', ',').split(',')
                bases_dict = {i: float(val) for i, val in enumerate(parts, start=1)}
                self.alice.bases = bases_dict

        elif key == "bob_bases":  # TODO
            if hasattr(self.alice, 'bases'):
                self.bob.bases = value
