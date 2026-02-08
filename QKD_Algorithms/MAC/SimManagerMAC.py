from MAC.ChannelMAC import ChannelMAC as channel
from Common.SimManager import SimManager
from typing import override
from DIContainers import MACContainer

from MAC.AliceMAC import AliceMAC as alice
from MAC.BobMAC import BobMAC as bob
from MAC.EveMAC import EveMAC as eve
from MAC.HashMAC import HashMAC as Hash
from random import choice, shuffle


class SimManagerMAC(SimManager):
    m_exp = 4
    t_exp = 2
    given_mts = 4
    eve_forgeries = 4

    def __init__(self):
        self.logger = MACContainer.logger()
        self.sim_step = 0

    def simLoop(self):
        self.is_running = True
        while self.is_running:
            self.sim_next_step()
        self.is_running = False

    def sim_next_step(self):
        self.logger.set_time(self.sim_step)

        if self.sim_step == 0:
            self._initial_print()
        if self.sim_step < self.given_mts:
            self._sim_transmition_step()
            self.logger.msg(f"---")
        elif self.sim_step == self.given_mts:
            self.logger.msg(f"=====================")
            self._sim_analysis_step()
        else:
            self.is_running = False
            return
        self.sim_step += 1

    def _initial_print(self):
        print('IP')

        self.M = 2 ** self.m_exp
        self.T = 2 ** self.t_exp

        self.p: int = Hash.next_prime(self.M)
        self.possible_messages: list[int] = [m for m in range(self.M)]

        possible_hashes: list[tuple[int, int]] = Hash.find_eq_prob_hashes(self.M, self.T)
        self.possible_hashes = possible_hashes
        qr: tuple[int, int] = choice(possible_hashes)

        h: hash = Hash(self.M, self.T, qr[0], qr[1], self.p)

        self.alice: alice = alice(h, list(self.possible_messages))
        self.bob: bob = bob(h)
        self.logger.log(f'Alice and Bob have secret hash of (q,r): {qr[0], qr[1]}')
        self.logger.log(f'In total there are {len(possible_hashes)} possible hashes\n')

        self.eve: eve = eve(self.M, self.T, self.p, possible_hashes)

    def _sim_transmition_step(self):
        self.logger.set_time(self.sim_step)

        mt: tuple[int, int] = self.alice.send_message()

        self.logger.log(f'Alice sends message to Bob: {mt[0]} with tag {mt[1]}')
        if self.bob.recieve_message(mt):
            self.logger.log(f'Bob positively verifies message')
        else:
            self.logger.log(f'Bob negatively verifies message - End of transmission')
            self.sim_step = self.given_mts + 2

        self.logger.log(f'Eve eavesdropps on (message, tag) pair\n')
        self.eve.eavesdrop(mt)

    def _sim_analysis_step(self):
        self.eve.narrow_possible_hashes()
        self.logger.log(f'Eve\'s possible hashes: {self.eve.possible_hashes}')

        alice_unused_messages: list[int] = self.alice.possible_messages
        shuffle(alice_unused_messages)
        messages_to_forge: list[int] = alice_unused_messages[:min(self.eve_forgeries, len(alice_unused_messages))]

        self.logger.log(f'Eve is given messages to forge tags:\n{messages_to_forge}')

        fakes: list[tuple[int, int]] = self.eve.forge_mtags(messages_to_forge)
        self.logger.log(f'Eve attempted tag forgery')

        self.logger.log('Message | Correct Tag | Eve\'s tag | Comparison')

        succ: int = 0

        for (m, t) in fakes:
            self.logger.log(f'{m, t, self.alice.h(m), t == self.alice.h(m)}')
            if t == self.alice.h(m):
                succ += 1

        self.logger.log(f'\nEve succeded in {100 * succ / len(fakes) :.2f}% of cases')

    @override
    def update_setting(self, key: str, value):
        """Dynamiczna aktualizacja parametrów symulacji"""

        value = int(value)

        print(f"Updating setting: {key} -> {value}")

        if key == "m_exp":
            self.m_exp = value

        elif key == "t_exp":
            self.t_exp = value


        elif key == "mts_given":
            self.given_mts = value

        elif key == "to_forge":
            self.eve_forgeries = value

        elif key == 'START':
            self.simLoop()

# def main():
#     s = SimManagerMAC()
#     s.run_sim()
#
#
# if __name__ == '__main__':
#     main()
