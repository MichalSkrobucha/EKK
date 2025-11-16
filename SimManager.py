import pandas as pd
from Alice import Alice
from Bob import Bob
from Eve import Eve
from Channel import Channel
from Logger import SimLogger

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

            self.bob.receive()

        logger.msg(f"=====================")
        # Basis exchange
        basesA: list[int] = self.alice.sendBases()
        basesB: list[int] = self.bob.sendBases()

        self.bob.receiveBases(basesA)
        self.alice.receiveBases(basesB)

        if self.ifEve:
            self.eve.eavesdrop_bases(basesA, basesB)

        # Sieving
        self.bob.sieveBits()
        self.alice.sieveBits()

        if self.ifEve:
            self.eve.print_sieved_bits()

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
        pass

    def printTable(self, fname: str = "data/bb84_data.csv"):
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
