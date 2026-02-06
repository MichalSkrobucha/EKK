# from QKD_Algorithms_OLD.E91.SimManager import SimManager
# from QKD_Algorithms_OLD.Logger import SimLogger
from QKD_Algorithms_OLD.E91.Channel import Channel
from QKD_Algorithms_OLD.E91.Source import Source
from QKD_Algorithms_OLD.E91.Photon import Photon
from QKD_Algorithms_OLD.E91.Alice import Alice
from QKD_Algorithms_OLD.E91.Bob import Bob
from QKD_Algorithms_OLD.E91.Eve import Eve

import math
import random

# logger = SimLogger()

bases: dict[int, float] = {0: 0.0, 1: 22.5, 2: 45.0, 3: 67.5}


def get_theoretical_E(angle_a_deg, angle_b_deg):
    return math.cos(2 * (math.radians(angle_a_deg) - math.radians(angle_b_deg)))


def main() -> None:
    """
    Runs the simulation
    """
    # simManager: SimManager = SimManager()
    # logger.enable_logger(True)  # Włączenie logów
    # simManager.ifEve = False
    # # Simulation test
    # simManager.simLoop()

    ifEve: int = -1  # -1 - noEve, 0 - Eve measures after sieving baes, 1 - E before AB, 2 - E between A&B, 3 - E after AB

    p: float = 0.75

    measuresA = []
    measuresB = []

    N: int = 10_000

    source = Source(n=2 if ifEve < 0 else 3, p=p)

    bases: dict[int, float] = {0: 0.0, 1: 22.5, 2: 45.0, 3: 67.5}

    BASES_ALICE = [0, 1, 2]
    BASES_BOB = [1, 2, 3]

    channel_alice = Channel()
    channel_bob = Channel()
    channel_eve = Channel()

    alice = Alice(channel_alice, BASES_ALICE, bases)
    bob = Bob(channel_bob, BASES_BOB, bases)
    eve = Eve(channel_eve, BASES_ALICE, bases)

    for _ in range(N):
        if ifEve < 0:
            photon_A, photon_B = source.generate()
            channel_alice.send([photon_A])
            channel_bob.send([photon_B])

            alice.receive()
            bob.receive()
        else:
            photon_A, photon_B, photon_E = source.generate()
            channel_alice.send([photon_A])
            channel_bob.send([photon_B])
            channel_eve.send([photon_E])

            match ifEve:
                case 0:
                    alice.receive()
                    bob.receive()

                    eve.receive()
                case 1:
                    eve.receive_and_measure()

                    alice.receive()
                    bob.receive()
                case 2:
                    alice.receive()

                    eve.receive_and_measure()

                    bob.receive()
                case 3:
                    alice.receive()
                    bob.receive()

                    eve.receive_and_measure()
                case _:
                    pass

    stats: dict[tuple[int, int], dict[str, int]] = {}

    for a, b in zip(alice.results, bob.results):
        # Para baz użyta w tej rundzie
        pair_key = (a['base_idx'], b['base_idx'])

        # Alice and Bob used same bases, used to create key
        if pair_key[0] == pair_key[1]:
            alice.test_key.append(a['bit'])
            bob.test_key.append(b['bit'])

        eve.eavsdrop_bases(*pair_key)

        # BELL TEST - CHSH inequality
        # Zliczanie korelacji dla wszystkich kombinacji
        if pair_key not in stats:
            stats[pair_key] = {'same': 0, 'diff': 0}

        if a['bit'] == b['bit']:
            stats[pair_key]['same'] += 1
        else:
            stats[pair_key]['diff'] += 1

    match ifEve:
        case 0:
            eve.sieve_and_measure()
        case -1:
            pass  # no Eve

        case _:
            eve.sieve()

    # Wzór na E: E = (N_same - N_diff) / (N_same + N_diff)
    def get_E(idx_a, idx_b):

        key = (idx_a, idx_b)
        if key not in stats: return 0
        s = stats[key]['same']
        d = stats[key]['diff']

        if s + d == 0: return 0
        return float((s - d) / (s + d))

    print(f'(Alice base, Bob base): measured |  theroetical)')

    for a in BASES_ALICE:
        for b in BASES_BOB:
            print(f'{a, b}: {get_E(a, b):.4f} | {get_theoretical_E(bases[a], bases[b]):.4f}')

    # CHSH : 01, 03, 21, 23

    chsh: float = get_E(0, 1) - get_E(0, 3) + get_E(2, 1) + get_E(2, 3)

    print(f'CHSH: {chsh:.4f}')

    print(alice.test_key)
    print(bob.test_key)
    if ifEve >= 0:
        print(eve.key)


if __name__ == '__main__':
    main()
