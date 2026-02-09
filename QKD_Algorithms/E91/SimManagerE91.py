import math
from typing import override
from itertools import combinations
from DIContainers import E91Container
from Common.SimManager import SimManager
from Common.config import cfg

from .Source import Source


class SimManagerE91(SimManager):
    protocol: int = 91
    S: float = 2.0

    S_Threshhold: float = 2.0

    BASES_ALICE = list(cfg.e91.alice_bases.keys())
    BASES_BOB = list(cfg.e91.bob_bases.keys())
    BASES_EVE = list(cfg.e91.eve_bases.keys())
    BASES_DICT = cfg.e91.bases_dict

    p: float = 1.0

    eveMode: int = -1

    # -1 - noEve,
    # 0 - eve measures after eavsdropping bases,
    # 1 - eve measures before AB,
    # 2 - eve measures between A&B,
    # 3 - eve measures after AB

    def __init__(self):
        self._recalculate_channel_params()
        self.channel_alice = E91Container.channel_A()
        self.channel_bob = E91Container.channel_B()
        self.channel_eve = E91Container.channel_E()
        alice = E91Container.alice(self.BASES_ALICE, self.BASES_DICT)
        bob = E91Container.bob(self.BASES_BOB, self.BASES_DICT)
        eve = E91Container.eve(self.BASES_EVE, self.BASES_DICT)
        self.source = E91Container.source()
        logger = E91Container.logger()

        self.ifEve = self.eveMode >= 0

        self.source.n = 2 if self.eveMode < 0 else 3
        self.source.p = self.p

        super().__init__(None, alice, bob, eve, logger, "E91")

    @override
    def clear_simManager(self) -> None:
        """
        Empties all lists
        """
        self.alice.clearLists()
        self.bob.clearLists()
        self.eve.clearLists()
        self.channel_alice.clearLists()
        self.channel_bob.clearLists()
        self.channel_eve.clearLists()
        self.source.clearLists()

        self.sim_step = 0
        self.logger.reset_logger()

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
                        f'> Alice bases: {cfg.e91.alice_bases.values()}\n'
                        f'> Bob bases: {cfg.e91.bob_bases.values()}\n')

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
        elif self.sim_step == self.sim_end + 1:
            self.alice.prepareForErrorCorrection()
            self.bob.prepareForErrorCorrection()
        elif self.sim_step == self.sim_end + 2:
            if self.S >= self.S_Threshhold:
                self._run_error_correction()
                self._run_privacy_amplification()
            else:
                self.logger.log('Transmission won\'t be continued')
        else:
            self.is_running = False
            return
        self.sim_step += 1

    @override
    def _sim_transmition_step(self):
        # Generating pair
        if self.eveMode < 0:
            self.source.n = 2
            photon_A, photon_B = self.source.generate()
            self.channel_alice.send([photon_A])
            self.channel_bob.send([photon_B])

            self.alice.receive()
            self.bob.receive()
        else:
            self.source.n = 3
            photon_A, photon_B, photon_E = self.source.generate()
            self.channel_alice.send([photon_A])
            self.channel_bob.send([photon_B])
            self.channel_eve.send([photon_E])

            match self.eveMode:
                case 0:
                    self.alice.receive()
                    self.bob.receive()

                    self.eve.receive()
                case 1:
                    self.eve.receive_and_measure()

                    self.alice.receive()
                    self.bob.receive()
                case 2:
                    self.alice.receive()

                    self.eve.receive_and_measure()

                    self.bob.receive()
                case 3:
                    self.alice.receive()
                    self.bob.receive()

                    self.eve.receive_and_measure()
                case _:
                    pass

    def _sim_analysis_step(self):
        self.logger.log("\n________________________")
        self.logger.log("--- EKSPERYMENTALNIE ---")
        self.logger.log("________________________")
        self._analyze_results()
        self.logger.log("\n____________________")
        self.logger.log("--- TEORETYCZNIE ---")
        self.logger.log("____________________\n")
        self._theoretical_result()

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

            if self.eveMode >= 0:
                self.eve.eavsdrop_bases(pair_key[0], pair_key[1])

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

        match self.eveMode:
            case 0:
                self.eve.sieve_and_measure()
            case -1:
                pass  # no Eve
            case _:
                self.eve.sieve()

        self.logger.log(f"\nWygenerowano surowy klucz o długości: {len(raw_key_alice)} bitów")
        self.logger.log(f"Klucz Alicji: {raw_key_alice}")
        self.logger.log(f"Klucz Boba:   {raw_key_bob}")

        self.alice.keyBits = raw_key_alice
        self.bob.keyBits = raw_key_bob

        err: int = 0

        for (a, b) in zip(raw_key_alice, raw_key_bob):
            if a != b:
                err += 1

        if len(raw_key_alice) != 0:
            self.qber = err / len(raw_key_alice)
        else:
            self.qber = 0
        self.logger.log(f'QBER: {self.qber:.4f}')

        # Wzór na E: E = (N_same - N_diff) / (N_same + N_diff)
        def get_E(idx_a, idx_b):
            key = (idx_a, idx_b)
            if key not in stats: return 0
            s = stats[key]['same']
            d = stats[key]['diff']
            if s + d == 0: return 0
            return (s - d) / (s + d)

        E_A0_B1 = float(get_E(0, 1))
        E_A0_B3 = float(get_E(0, 3))
        E_A2_B1 = float(get_E(2, 1))
        E_A2_B3 = float(get_E(2, 3))

        # Wzór na S dla zestawu kątów A1, A3, B1, B3:
        # S = |E(A1, B1) - E(A1, B3) + E(A3, B1) + E(A3, B3)|
        S = abs(E_A0_B1 - E_A0_B3 + E_A2_B1 + E_A2_B3)

        self.logger.log("\n--- Test Nierówności Bella (CHSH) ---")
        self.logger.log(f"E(A0, B1) = {E_A0_B1:.4f}    Bases: {self.BASES_DICT[0]}, {self.BASES_DICT[1]}")
        self.logger.log(f"E(A0, B3) = {E_A0_B3:.4f}    Bases: {self.BASES_DICT[0]}, {self.BASES_DICT[3]}")
        self.logger.log(f"E(A2, B1) = {E_A2_B1:.4f}    Bases: {self.BASES_DICT[2]}, {self.BASES_DICT[1]}")
        self.logger.log(f"E(A2, B3) = {E_A2_B3:.4f}    Bases: {self.BASES_DICT[2]}, {self.BASES_DICT[3]}")
        self.logger.log(f"Wartość parametru S = {S:.4f}")

        if S > self.S_Threshhold:
            self.logger.log(">> SUKCES: Nierówność Bella złamana! (Bezpieczeństwo potwierdzone)")
        else:
            self.logger.log(">> OSTRZEŻENIE: Brak kwantowych korelacji lub zbyt duży szum.")

        self.S = S

    def _theoretical_result(self):
        def get_theoretical_E(angle_a_deg, angle_b_deg):
            theta_A = math.radians(angle_a_deg)
            theta_B = math.radians(angle_b_deg)

            delta = theta_A - theta_B
            return math.cos(2 * delta)

        E_A0_B1 = float(get_theoretical_E(self.BASES_DICT[0], self.BASES_DICT[1]))
        E_A0_B3 = float(get_theoretical_E(self.BASES_DICT[0], self.BASES_DICT[3]))
        E_A2_B1 = float(get_theoretical_E(self.BASES_DICT[2], self.BASES_DICT[1]))
        E_A2_B3 = float(get_theoretical_E(self.BASES_DICT[2], self.BASES_DICT[3]))

        S_theoretical = abs(E_A0_B1 - E_A0_B3 + E_A2_B1 + E_A2_B3)

        self.logger.log(f"E(A0, B1)  = {E_A0_B1:.4f}")
        self.logger.log(f"E(A0, B3) = {E_A0_B3:.4f}")
        self.logger.log(f"E(A2, B1) = {E_A2_B1:.4f}")
        self.logger.log(f"E(A2, B3) = {E_A2_B3:.4f}")

        self.logger.log(f"Teoretyczne S = {S_theoretical:.4f}\n")

        # def get_S_for_pair(base_idx_1, base_idx_2):
        #     val_A1_B1 = get_theoretical_E(self.alice.bases[base_idx_1], self.bob.bases[base_idx_1])
        #     val_A1_B2 = get_theoretical_E(self.alice.bases[base_idx_1], self.bob.bases[base_idx_2])
        #     val_A2_B1 = get_theoretical_E(self.alice.bases[base_idx_2], self.bob.bases[base_idx_1])
        #     val_A2_B2 = get_theoretical_E(self.alice.bases[base_idx_2], self.bob.bases[base_idx_2])
        #
        #     print(
        #         f"E(A{base_idx_1}, B{base_idx_1}) [{self.alice.bases[base_idx_1]} vs {self.bob.bases[base_idx_1]}]  = {val_A1_B1:.4f}")
        #     print(
        #         f"E(A{base_idx_1}, B{base_idx_2}) [{self.alice.bases[base_idx_1]} vs {self.bob.bases[base_idx_2]}]  = {val_A1_B2:.4f}")
        #     print(
        #         f"E(A{base_idx_2}, B{base_idx_1}) [{self.alice.bases[base_idx_2]} vs {self.bob.bases[base_idx_1]}] = {val_A2_B1:.4f}")
        #     print(
        #         f"E(A{base_idx_2}, B{base_idx_2}) [{self.alice.bases[base_idx_2]} vs {self.bob.bases[base_idx_2]}] = {val_A2_B2:.4f}")
        #
        #     # S = |E(A1, B1) - E(A1, B3) + E(A3, B1) + E(A3, B3)|
        #     S_theoretical = abs(val_A1_B1 - val_A1_B2 + val_A2_B1 + val_A2_B2)
        #     print(
        #         f"Teoretyczne S ({self.alice.bases[base_idx_1]},{self.alice.bases[base_idx_2]}) = {S_theoretical:.5f}\n")
        #     return S_theoretical

        # def find_max_S():
        #     indices = [1, 2, 3]
        #     results = {}
        #     for idx1, idx2 in combinations(indices, 2):
        #         s_val = get_S_for_pair(idx1, idx2)
        #         results[(idx1, idx2)] = s_val
        #
        #     best_pair = max(results, key=results.get)
        #     max_S = results[best_pair]
        #     print(f"\n>>> ZWYCIĘZCA: Para indeksów {best_pair}")
        #     print(f">>> Maksymalne S = {max_S:.5f}")
        #     return max_S

        # if find_max_S() > 2:
        #     print("\n>> SUKCES: Wynik łamie nierówność Bella.")
        # else:
        #     print("\n>> UWAGA: Coś nie tak z kątami.")

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

        elif key == "bob_bases":
            if hasattr(self.alice, 'bases'):
                self.bob.bases = value

        elif key == "eve_mode":
            id = ["No Eve", "Eve measures after base exchange", "Eve measures before Alice",
                  "Eve measures between Alice & Bob", "Eve measures after Bob"].index(value)

            self.eveMode = id - 1

        elif key == "s_thresh":
            self.S_Threshhold = float(value)

        elif key == "p":
            self.p = float(value)
