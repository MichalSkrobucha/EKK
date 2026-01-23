import pandas as pd
from abc import abstractmethod
from math import ceil
from Logger import SimLogger
from .Channel import Channel
from .Alice import Alice
from .Bob import Bob
from .Eve import Eve


class SimManager:
    sim_start: int = 0
    sim_end: int = 1000
    sim_step: int
    qberThreshhold: float = 0.2
    ifEve: bool = True
    is_running: bool = False
    logs: bool = True

    channel_length: float = 1.0  # km
    dumpening_per_km: float = 0.2  # dB/ km
    base_transform_per_km: float = 0.2  # db / km

    dumpening_dB: float = dumpening_per_km * channel_length
    base_transform_dB: float = base_transform_per_km * channel_length

    dumpening: float = 1 - 10 ** (-dumpening_dB / 10.0)
    base_transform: float = 1 - 10 ** (-base_transform_dB / 10.0)

    def __init__(self, channel: Channel|None, alice: Alice, bob: Bob, eve: Eve|None, logger: SimLogger):
        # self.reloadBaseValues()
        self.channel = channel
        self.alice = alice
        self.bob = bob
        self.eve = eve
        self.sim_step = self.sim_start

        self.logger = logger
        self.logger.set_time(self.sim_start)

    def reloadBaseValues(self):
        self.channel_length: float = 1.0  # km
        self.dumpening_per_km: float = 0.2  # dB/ km
        self.base_transform_per_km: float = 0.2  # db / km

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.alice.clearLists()
        self.bob.clearLists()
        self.eve.clearLists()

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
