# from QKD_Algorithms_OLD.E91.SimManager import SimManager
# from QKD_Algorithms_OLD.Logger import SimLogger

from QKD_Algorithms_OLD.E91.Photon import Photon
from QKD_Algorithms_OLD.E91.Source import Source

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

    measuresA = []
    measuresB = []

    N: int = 1_000

    s: Source = Source()

    basesA: list[int] = [0, 1, 2]
    basesB: list[int] = [1, 2, 3]

    for _ in range(N):
        (phA, phB, phE) = s.generate()

        baseA = random.choice(basesA)
        baseB = random.choice(basesB)

        mA = (phA.measure(bases[baseA]), baseA)
        mB = (phB.measure(bases[baseB]), baseB)

        measuresA.append(mA)
        measuresB.append(mB)

        print(f'A measured {mA[0]} in base {mA[1]} ({bases[mA[1]]})',
              f'B measured {mB[0]} in base {mB[1]} ({bases[mB[1]]})',
              sep='\n', end='\n\n')

    stats: dict[tuple[int, int], dict[str, int]] = {}

    for a, b in zip(measuresA, measuresB):
        # Para baz użyta w tej rundzie
        pair_key = (a[1], b[1])

        # # Alice and Bob used same bases, used to create key
        # if a[1] == b[1]:
        #     pass

        # BELL TEST - CHSH inequality
        # Zliczanie korelacji dla wszystkich kombinacji
        if pair_key not in stats:
            stats[pair_key] = {'same': 0, 'diff': 0}

        if a[0] == b[0]:
            stats[pair_key]['same'] += 1
        else:
            stats[pair_key]['diff'] += 1

    # Wzór na E: E = (N_same - N_diff) / (N_same + N_diff)
    def get_E(idx_a, idx_b):
        key = (idx_a, idx_b)
        if key not in stats: return 0
        s = stats[key]['same']
        d = stats[key]['diff']
        if s + d == 0: return 0
        return (s - d) / (s + d)

    print(f'(Alice base, Bob base): measured |  theroetica)')

    for a in basesA:
        for b in basesB:
            print(f'{a, b}: {get_E(a, b)} | {get_theoretical_E(bases[a], bases[b])}')

    # CHSH : 01, 03, 21, 23

    chsh: float = get_E(0, 1) - get_E(0, 3) + get_E(2, 1) + get_E(2, 3)

    print(f'CHSH: {chsh:.2f}')


if __name__ == '__main__':
    main()
