import pandas as pd
from abc import abstractmethod, ABC
from math import ceil
from Logger import SimLogger
from .Channel import Channel
from .Alice import Alice
from .Bob import Bob
from .Eve import Eve
from Common.config import cfg


class SimManager(ABC):
    sim_start: int = 0
    sim_end: int = cfg.sim.key_length
    sim_step: int
    qberThreshhold: float = cfg.sim.qber_threshold/100
    ifEve: bool = cfg.bb84.eve_present
    is_running: bool = False

    channel_length: float = cfg.channel.length_km  # km
    dumpening_per_km: float = cfg.channel.dumpening_per_km  # dB/ km
    base_transform_per_km: float = cfg.channel.base_transform_per_km  # db / km

    dumpening_dB: float
    base_transform_dB: float

    dumpening: float
    base_transform: float

    def __init__(self, channel: Channel|None, alice: Alice, bob: Bob, eve: Eve|None, logger: SimLogger, protocol_name: str=""):
        self.protocol_name = protocol_name
        self.channel = channel
        self.alice = alice
        self.bob = bob
        self.eve = eve
        self.sim_step = self.sim_start

        self.logger = logger
        self.logger.set_time(self.sim_start)
        self._recalculate_channel_params()

    def reloadBaseValues(self):
        self.channel_length: float = cfg.channel.length_km  # km
        self.dumpening_per_km: float = cfg.channel.dumpening_per_km  # dB/ km
        self.base_transform_per_km: float = cfg.channel.base_transform_per_km  # db / km

    def clear_simManager(self) -> None:
        """
        Empties all lists
        """
        self.alice.clearLists()
        self.bob.clearLists()
        self.eve.clearLists()
        self.channel.clearLists()

        self.sim_step = 0
        self.logger.reset_logger()

    @abstractmethod
    def simLoop(self):
        """
        Simulates QKD (du-uh)
        """
        pass

    def printTable(self, fname: str = "QKD_Algorithms_OLD/BB84/data/bb84_data.csv"):
        """
        Saves table of data (Alice's, Bob's and Eve's basis and bits) to file and prints it to console
        :param fname: name of save file
        """

        alice_bases = ['+' if b == 0 else 'x' for b in self.alice.bases]
        bob_bases = ['+' if b == 0 else 'x' for b in self.bob.bases]
        eve_bases = ['+' if b == 0 else 'x' for b in self.eve.bases]
        bobs_hits_bin = [x ^ y for x, y in zip(self.alice.bases, self.bob.bases)]
        bobs_hits = ['✔' if x == 0 else 'X' for x in bobs_hits_bin]
        key_bits = [x if y == 0 else '-' for x, y in zip(self.bob.bits, bobs_hits_bin)]

        df = pd.DataFrame({
            "Alice bits": self.alice.bits,
            "Alice bases": alice_bases,
            "Bob bases": bob_bases,
            "Bob results": self.bob.bits,
            "Bob hits": bobs_hits,
            "Key bits": key_bits,
            "Eve result": eve_bases,
            "Eve bits": self.eve.bits
        })
        df = df.transpose()
        df.to_csv(fname, index=False)
        print("\n", df)

    def checkCorrectness(self):
        alice_bits = self.alice.sievedBits
        bob_bits = self.bob.sievedBits
        eve_bits = self.eve.sieved_bits

        bob_correct_bits = len([1 for (a, b) in zip(alice_bits, bob_bits) if a == b])
        eve_has_bits = len([1 for e in eve_bits if e != -1])
        eve_correct_bits = len([1 for (a, e) in zip(alice_bits, eve_bits) if a == e])

        self.logger.log(
            f'Alice and Bob have {len(alice_bits)} each and Bob has {bob_correct_bits} correct ({bob_correct_bits / len(alice_bits):.4f})\n'
            f'Eve has {eve_has_bits} bits ({eve_has_bits / len(alice_bits):.4f}), and in (total) has correct {eve_correct_bits} ({eve_correct_bits / len(alice_bits):.4f})')

    def _initial_print(self):
        self.logger.log(f'\n --- {self.protocol_name} Simulation ---\n'
                        f'> Channel Length: {self.channel_length} km\n'
                        f'> Dumpening per km: {self.dumpening_per_km} dB/km\n'
                        f'> Base transform rate: {self.base_transform_per_km} dB/km\n'
                        f'> Dumpening rate: {self.dumpening_dB} dB\n'
                        f'> Total base transform: {self.base_transform_per_km} dB\n'
                        f'> Total dumpening rate: {self.dumpening}\n'
                        f'> Base transform per km {self.base_transform_per_km}\n'
                        f'> QBER treshhold: {self.qberThreshhold}\n'
                        f'> If Eve is present: {self.ifEve}\n')

    @abstractmethod
    def sim_next_step(self):
        pass

    def _sim_transmition_step(self):
        self.alice.send_key()

        if self.ifEve:
            self.eve.eavesdrop()

        self.bob.receive()

    def _sim_sampling_step(self):
        # Bob decides sampleIDs
        self.alice.getSampleIds(self.bob.sendSampleIds())
        # Sample exchange
        self.alice.recieveSamples(self.bob.sendSample())
        self.alice.sendSample()
        self.bob.receiveSamples(self.alice.sendSample())

    def _sim_calculate_qber(self):
        # QBER calculation
        self.alice.calculateQBER()
        self.bob.calculateQBER()

        if self.bob.qber > self.qberThreshhold:
            # QBER is NOT accepatable
            self.logger.log("QBER exceeded threshhold. Ending transmission")
            self.is_running = False
            return

    def _run_error_correction(self):

        self.logger.log('\n--- ERROR CORRECTION ---\n')

        alice = self.alice
        bob = self.bob

        # korekcja błędów
        # Alicja i Bob wymieniają się informacjami, ewa słucha (w teorii - brak wywołań funkcji)

        # Alicja wysyła klucz
        alice_key_hash = alice.send_key_hash()
        bob.get_key_hash(alice_key_hash)
        self.logger.log(f'Alice\'s key hash: {alice_key_hash.hex()}\n')

        if bob.check_hash():
            self.logger.log('Key hashes match - end of error correction\n'
                  f'Bob has {sum([1 for (a, b) in zip(alice.keyBits, bob.keyBits) if a == b])} correct bits (~SimMaster)\n'
                  f'{'Both keys are the same' if all([a == b for (a, b) in zip(alice.keyBits, bob.keyBits)]) else 'Keys are not the same'}')
            return

        while True:
            # permutacja
            permutation: list[int] = alice.permute()
            bob.get_alice_permutation(permutation)

            self.logger.log(f'Alice permutes her bits using permutation {permutation}\n'
                  f'And gets bits {''.join([str(bit) for bit in self.alice.keyBits])}\n'
                  f'Bob has bits {''.join([str(bit) for bit in self.bob.keyBits])}\n'
                  f'Bob has {sum([1 for (a, b) in zip(alice.keyBits, bob.keyBits) if a == b])} correct bits (~SimMaster)\n')

            # podział na bloki
            alice.split_into_blocks()
            bob.split_into_blocks()

            self.logger.log(f'Alice and Bob split their bits into blocks of length {alice.n}\n')

            # obliczenia parzystości
            alice_parities = alice.compute_parity_bits()
            bob_parities = bob.compute_parity_bits()
            matching_parities: bool = all([a == b for (a, b) in zip(alice_parities, bob_parities)])

            self.logger.log(f'Alice and Bob exchange blocks parities\n'
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

                self.logger.log(f'Alice and Bob exchange blocks parities\n'
                      f'Alice\'s parities: {''.join([str(bit) for bit in alice_parities])}\n'
                      f'Bob\'s parities: {''.join([str(bit) for bit in bob_parities])}\n'
                      f'{'All parities match' if matching_parities else 'There are parities that do not match - next round of recursive correction'}\n')

            bob.flatten_blocks()

            # permutacja odwrotna
            alice.unpermute()
            bob.unpermute()

            # sprawdzenie poprawności
            if bob.check_hash():
                self.logger.log('Key hashes match - end of error correction\n'
                      f'Bob has {sum([1 for (a, b) in zip(alice.keyBits, bob.keyBits) if a == b])} correct bits (~SimMaster)\n'
                      f'{'Both keys are the same' if all([a == b for (a, b) in zip(alice.keyBits, bob.keyBits)]) else 'Keys are not the same'}')
                break

            self.logger.log('Key hashes don\'t match - next iteration of error correction\n\n')

    def _run_privacy_amplification(self):

        self.logger.log('\n--- PRIVACY AMPLIFICATION ---\n')

        alice = self.alice
        bob = self.bob

        self.logger.log(f'Alice and Bob have {len(self.alice.keyBits)} bits\n')

        # estywamcja bezpieczeńśtwa klucza
        n: int = len(self.alice.keyBits)

        ###
        eves_known_bits: int = ceil(alice.qber * n)
        security_bits : int = n - eves_known_bits

        self.logger.log(f'Estimated bits known by Eve: {eves_known_bits}\n'
              f'Esitmated secuirty provided by key: {security_bits} bits\n')

        # wzmocnienie prywatności
        r_bytes: bytes = alice.send_random_bytes()
        bob.get_random_bytes(r_bytes)

        self.logger.log(f'Alice send random bytes ({alice.bytes_count}): {alice.random_bytes.hex()}\n')

        alice.get_final_key()
        bob.get_final_key()

        self.logger.log('Alice and Bob calculate final key')

        self.logger.log(f'A: {alice.key.hex()}\n'
              f'B: {bob.key.hex()}\n'
              f'Keys match: {alice.key == bob.key}')

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

        elif key == "alice_mi":
            if hasattr(self.alice, 'mi'):
                self.alice.mi = float(value)

        elif key == "bob_eff":
            if hasattr(self.bob, 'efficiency'):
                self.bob.efficiency = float(value) / 100.0

        elif key == "bob_error":
            if hasattr(self.bob, 'error'):
                self.bob.error = float(value) / 100.0

        elif key == "if_eve":
            self.ifEve = bool(value)

    def _recalculate_channel_params(self):
        """Przelicza parametry zależne od długości kanału"""
        self.dumpening_dB: float = self.dumpening_per_km * self.channel_length
        self.base_transform_dB: float = self.base_transform_per_km * self.channel_length

        self.dumpening: float = round(1 - 10 ** (-self.dumpening_dB / 10.0),1)
        self.base_transform: float = round(1 - 10 ** (-self.base_transform_dB / 10.0),1)

        # Aktualizacja obiektu Channel
        if hasattr(self, 'channel') and self.channel is not None:
            if hasattr(self.channel, 'dumpening'):
                self.channel.dumpening = self.dumpening
            if hasattr(self.channel, 'base_transform'):
                self.channel.base_transform = self.base_transform
