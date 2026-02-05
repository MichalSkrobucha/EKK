import pandas as pd
from Common.SimManager import SimManager
from DIContainers import SARGContainer
from Common.config import cfg


class SimManagerSARG(SimManager):
    protocol: int = 4
    qber : float = 0.0
    def __init__(self):
        self._recalculate_channel_params()
        channel = self.channel = SARGContainer.channel(self.dumpening, self.base_transform)
        alice = SARGContainer.alice(mi=cfg.bb84.alice_mi)
        bob = SARGContainer.bob(efficiency=cfg.bb84.bob_efficiency/100,
                                error=cfg.bb84.bob_error/100)
        eve = SARGContainer.eve()
        logger = SARGContainer.logger()

        super().__init__(channel, alice, bob, eve, logger, "SARG04")

    def simLoop(self):
        """
        Simulates QKD (du-uh)
        """
        self._initial_print()
        self.is_running = True
        while self.is_running:
            self.sim_next_step()

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

    def sim_next_step(self):
        self.logger.set_time(self.sim_step)
        if self.sim_step == 0:
            self._initial_print()

        if self.sim_step < self.sim_end:
            self._sim_transmition_step()
        elif self.sim_step == self.sim_end:
            self.logger.msg(f"=====================")
            self._anounce_states_step()
        elif self.sim_step == self.sim_end + 1:
            self._sieve_used_states()
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

    def _anounce_states_step(self):
        statesAnnounced: list[tuple[int, int]] = self.alice.announceStates()
        self.bob.recieveStates(statesAnnounced)

        if self.ifEve:
            self.eve.eavesdropStates(statesAnnounced)

    def _sieve_used_states(self):
        self.bob.sieveStates()
        usedStates: list[int] = self.bob.announceUsedStates()

        if self.ifEve:
            self.eve.eavsdropUsedStates(usedStates)

        self.alice.getUsedStates(usedStates)

