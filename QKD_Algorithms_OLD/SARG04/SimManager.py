import pandas as pd
from .Alice import Alice
from .Bob import Bob
from .Eve import Eve
from .Channel import Channel
from QKD_Algorithms_OLD.Logger import SimLogger

from math import ceil

logger = SimLogger()


class SimManager:
    sim_start: int = 0
    sim_step: int = 1
    sim_end: int = 1000
    qberThreshhold: float = 0.2
    ifEve: bool = True
    logs: bool = True

    channel_length: float = 1.0  # km
    dumpening_per_km: float = 0.2  # dB/ km
    base_transform_per_km: float = 0.2  # db / km

    dumpening_dB: float = dumpening_per_km * channel_length
    base_transform_dB: float = base_transform_per_km * channel_length

    dumpening: float = 1 - 10 ** (-dumpening_dB / 10.0)
    base_transform: float = 1 - 10 ** (-base_transform_dB / 10.0)

    channel: Channel
    alice: Alice
    bob: Bob
    eve: Eve

    def __init__(self):
        self.reloadBaseValues()
        self.channel = Channel(self.dumpening, self.base_transform)
        self.alice = Alice(self.channel, 0.5)
        self.bob = Bob(self.channel, 0.99, 0.01)
        self.eve = Eve(self.channel)
        logger.set_time(self.sim_start)

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

    def simLoop(self):
        """
        Simulates QKD (du-uh)
        """
        logger.log(f'\nSimulating channel of length {self.channel_length} km\n'
                   f'with dumpening rate {self.dumpening_per_km} dB/km and base_transform rate {self.base_transform_per_km} dB/km\n'
                   f'Total rates are {self.dumpening_dB} dB of dumpening and {self.base_transform_per_km} dB of base_transform\n'
                   f'Probability of events (per photon) are {self.dumpening} for dumpening and {self.base_transform_per_km} for base_transform')

        for step in range(self.sim_start, self.sim_end, self.sim_step):
            # Alice sends bits (impulses of photons) to Bob
            logger.msg(f"=====================")
            logger.set_time(step)

            self.alice.send_key()

            if self.ifEve:
                self.eve.eavesdrop()

            self.bob.recieve()

        logger.msg(f"=====================")
        # BStates Announce
        statesAnnounced: list[tuple[int, int]] = self.alice.announceStates()

        self.bob.recieveStates(statesAnnounced)

        if self.ifEve:
            self.eve.eavesdropStates(statesAnnounced)

        # Sieving
        self.bob.sieveStates()

        usedStates: list[int] = self.bob.announceUsedStates()

        if self.ifEve:
            self.eve.eavsdropUsedStates(usedStates)

        self.alice.getUsedStates(usedStates)

        # Bob decides sampleIDs
        self.alice.getSampleIds(self.bob.sendSampleIds())
        # Sample exchange
        self.alice.recieveSamples(self.bob.sendSample())
        self.bob.receiveSamples(self.alice.sendSample())
        # QBER calculation
        self.alice.calculateQBER()
        self.bob.calculateQBER()

        if self.bob.qber > self.qberThreshhold:
            # QBER is NOT accepatable
            logger.log("QBER exceeded threshhold. Ending transmission")
            return

        # QBER is accepatable

        # Here will be error correction
        self.alice.prepareForErrorCorrection()
        self.bob.prepareForErrorCorrection()

        self.run_error_correction()
        self.run_privacy_amplification()


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

        if bob.check_hash():
            print('Key hashes match - end of error correction\n'
                  f'Bob has {sum([1 for (a, b) in zip(alice.keyBits, bob.keyBits) if a == b])} correct bits (~SimMaster)\n'
                  f'{'Both keys are the same' if all([a == b for (a, b) in zip(alice.keyBits, bob.keyBits)]) else 'Keys are not the same'}')
            return

        while True:
            # permutacja
            permutation: list[int] = alice.permute()
            bob.get_alice_permutation(permutation)

            print(f'Alice permutes her bits using permutation {permutation}\n'
                  f'And gets bits {''.join([str(bit) for bit in self.alice.keyBits])}\n'
                  f'Bob has bits {''.join([str(bit) for bit in self.bob.keyBits])}\n'
                  f'Bob has {sum([1 for (a, b) in zip(alice.keyBits, bob.keyBits) if a == b])} correct bits (~SimMaster)\n')

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
                      f'Bob has {sum([1 for (a, b) in zip(alice.keyBits, bob.keyBits) if a == b])} correct bits (~SimMaster)\n'
                      f'{'Both keys are the same' if all([a == b for (a, b) in zip(alice.keyBits, bob.keyBits)]) else 'Keys are not the same'}')
                break

            print('Key hashes don\'t match - next iteration of error correction\n\n')

    def run_privacy_amplification(self):

        print('\n--- PRIVACY AMPLIFICATION ---\n')

        alice = self.alice
        bob = self.bob

        print(f'Alice and Bob have {len(self.alice.keyBits)} bits\n')

        # estywamcja bezpieczeńśtwa klucza
        n: int = len(self.alice.keyBits)

        ###
        eves_known_bits: int = ceil(alice.qber * n)
        security_bits: int = n - eves_known_bits

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

    def printTable(self, fname: str = "QKD_Algorithms_OLD/SARG04/data/bb84_data.csv"):
        """
        Saves table of data (Alice's, Bob's and Eve's basis and bits) to file and prints it to console
        :param fname: name of save file
        """

        alice_bases = ['+' if b == 0 else 'x' for b in self.alice.sendBases]
        bob_bases = ['+' if b == 0 else 'x' for b in self.bob.bases]
        eve_bases = ['+' if b == 0 else 'x' for b in self.eve.bases]
        bobs_hits_bin = [x ^ y for x, y in zip(self.alice.sendBases, self.bob.bases)]
        bobs_hits = ['✔' if x == 0 else 'X' for x in bobs_hits_bin]
        key_bits = [x if y == 0 else '-' for x, y in zip(self.bob.bits, bobs_hits_bin)]

        # bits - what alice thinks she sent / what Bob (Eve) 'measured)
        # keyBits - what they actually got

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
