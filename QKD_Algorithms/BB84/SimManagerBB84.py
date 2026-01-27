import pandas as pd
from DIContainers import BB84Container
from Common.SimManager import SimManager
from Common.config import cfg


class SimManagerBB84(SimManager):
    def __init__(self):
        # self.reloadBaseValues()
        self._recalculate_channel_params()
        channel = BB84Container.channel(self.dumpening, self.base_transform)
        alice = BB84Container.alice(mi=cfg.bb84.alice_mi)
        bob = BB84Container.bob(efficiency=cfg.bb84.bob_efficiency/100,
                                error=cfg.bb84.bob_error/100)
        eve = BB84Container.eve()
        logger = BB84Container.logger()

        super().__init__(channel, alice, bob, eve, logger, "BB84")

    def simLoop(self):
        """
        Simulates QKD (du-uh)
        """
        self._initial_print()
        self.is_running = True
        while self.is_running:
            self.sim_next_step()

    def checkCorrectness(self):
        alice_bits = self.alice.sievedBits
        bob_bits = self.bob.sievedBits
        eve_bits = self.eve.sieved_bits

        bob_correct_bits = len([1 for (a, b) in zip(alice_bits, bob_bits) if a == b])
        eve_has_bits = len([1 for e in eve_bits if e != -1])
        eve_correct_bits = len([1 for (a, e) in zip(alice_bits, eve_bits) if a == e])

        print(
            f'Alice and Bob have {len(alice_bits)} each and Bob has {bob_correct_bits} correct ({bob_correct_bits / len(alice_bits):.4f})\n'
            f'Eve has {eve_has_bits} bits ({eve_has_bits / len(alice_bits):.4f}), and in (total) has correct {eve_correct_bits} ({eve_correct_bits / len(alice_bits):.4f})')

    def sim_next_step(self):
        self.logger.set_time(self.sim_step)
        if self.sim_step == 0:
            self._initial_print()

        if self.sim_step < self.sim_end:
            self._sim_transmition_step()
        elif self.sim_step == self.sim_end:
            self.logger.msg(f"=====================")
            self._sim_bases_exchange_step()
        elif self.sim_step == self.sim_end + 1:
            self._sim_sieve_step()
        elif self.sim_step == self.sim_end + 2:
            self._sim_sampling_step()
            self._sim_calculate_qber()
        elif self.sim_step == self.sim_end + 3:
            self.alice.prepareForErrorCorrection()
            self.bob.prepareForErrorCorrection()
        elif self.sim_step == self.sim_end + 4:
            self._run_error_correction()
        elif self.sim_step == self.sim_end + 5:
            self._run_privacy_amplification()
        else:
            self.is_running = False
            return
        self.sim_step += 1

    def _sim_bases_exchange_step(self):
        # Basis exchange
        basesA: list[int] = self.alice.sendBases()
        basesB: list[int] = self.bob.sendBases()

        self.bob.receiveBases(basesA)
        self.alice.receiveBases(basesB)

        if self.ifEve:
            self.eve.eavesdrop_bases(basesA, basesB)

    def _sim_sieve_step(self):
        # Sieving
        self.bob.sieveBits()
        self.alice.sieveBits()

        if self.ifEve:
            self.eve.print_sieved_bits()

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


