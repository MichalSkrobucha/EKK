from _alice import _alice
from _bob import _bob
from _eve import _eve
from _channel import _channel

from Logger import SimLogger

import pandas as pd
from math import sqrt

logger = SimLogger()


class _simManager:
    sim_start: int = 0
    sim_step: int = 1
    sim_end: int = 1000
    qberThreshhold: float = 0.2
    ifEve: bool = True
    logs: bool = True

    channel_length: float = 1.0  # km
    distance_alice_to_eve: float = 0.5  # km
    distance_eve_to_bob: float = channel_length - distance_alice_to_eve

    dumpening_per_km: float = 0.2  # dB/ km
    base_transform_per_km: float = 0.2  # dB / km

    dumpening_dB_alice_eve: float = dumpening_per_km * distance_alice_to_eve
    dumpening_dB_eve_bob: float = dumpening_per_km * distance_eve_to_bob
    dumpening_alice_eve: float = 10 ** (-dumpening_dB_alice_eve / 10.0)
    dumpening_eve_bob: float = 10 ** (-dumpening_dB_eve_bob / 10.0)

    base_transform_alice_eve: float = base_transform_per_km * distance_alice_to_eve
    base_transform_dB_eve_bob: float = base_transform_per_km * distance_eve_to_bob
    base_transform_alice_eve: float = 10 ** (-base_transform_alice_eve / 10.0)
    base_transform_eve_bob: float = 10 ** (-base_transform_dB_eve_bob / 10.0)

    channel: _channel
    alice: _alice
    bob: _bob
    eve: _eve

    def __init__(self) -> None:
        # self.reloadBaseValues()
        self.channel = _channel(self.dumpening_alice_eve, self.dumpening_eve_bob, self.base_transform_alice_eve,
                                self.base_transform_eve_bob)
        self.alice = _alice(self.channel, 0.5)
        self.bob = _bob(self.channel, 0.99, 0.01)
        self.eve = _eve(self.channel)
        logger.set_time(self.sim_start)

    # def reloadBaseValues(self):
    #     pass

    def clearLists(self) -> None:
        self.alice.clearLists()
        self.bob.clearLists()
        self.eve.clearLists()

    def simLoop(self) -> None:
        for i in range(self.sim_start, self.sim_step, self.sim_end):
            self.impulse_transmission()

        self.info_exchange()

        if not self.calculate_qber():
            return

        self.errorCorrection()
        self.privacyAmplification()

    def impulse_transmission(self) -> None:
        raise NotImplemented

    def info_exchange(self) -> None:
        raise NotImplemented

    def calculate_qber(self) -> bool:
        raise NotImplemented

    def dynamic_qber_threshold(self, n: int, p: float = 0.25, k: int = 3) -> float:
        return p - k * sqrt(p * (1 - p) / n)

    def errorCorrection(self) -> None:
        # z solutions
        pass

    def privacyAmplification(self) -> None:
        # dodać
        pass

    def printTable(self, fname: str = "QKD_Algorithms/data/bb84_data.csv") -> None:
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

    def checkCorrectness(self) -> None:
        alice_bits = self.alice.sievedBits
        bob_bits = self.bob.sievedBits
        eve_bits = self.eve.sievedBits

        bob_correct_bits = len([1 for (a, b) in zip(alice_bits, bob_bits) if a == b])
        eve_has_bits = len([1 for e in eve_bits if e != -1])
        eve_correct_bits = len([1 for (a, e) in zip(alice_bits, eve_bits) if a == e])

        print(
            f'Alice and Bob have {len(alice_bits)} each and Bob has {bob_correct_bits} correct ({bob_correct_bits / len(alice_bits):.4f})\n'
            f'Eve has {eve_has_bits} bits ({eve_has_bits / len(alice_bits):.4f}), and in (total) has correct {eve_correct_bits} ({eve_correct_bits / len(alice_bits):.4f})')

    def analyzeResults(self):
        pass

    def theoriticalResults(self):
        pass
