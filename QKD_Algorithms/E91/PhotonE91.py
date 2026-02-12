from math import cos, sin, radians, sqrt
from random import random


class SharedState:
    def __init__(self, n: int, amp0: float, amp1: float):
        self.n_remaining = n
        self.amp0 = amp0
        self.amp1 = amp1


class PhotonE91:
    def __init__(self, shared_state: SharedState) -> None:
        self.shared_state = shared_state

    def measure(self, base_degree: float) -> int:
        theta = radians(base_degree)
        c = cos(theta)
        s = sin(theta)

        a0 = self.shared_state.amp0
        a1 = self.shared_state.amp1

        is_last = (self.shared_state.n_remaining == 1)

        if is_last:
            # last photon
            amp_0_final = a0 * c + a1 * s

            prob_0 = amp_0_final ** 2

            r = random()
            if r <= prob_0:
                result = 0
                self.shared_state.amp0 = 0
                self.shared_state.amp1 = 0
            else:
                result = 1
                self.shared_state.amp0 = 0
                self.shared_state.amp1 = 0

        else:
            # probability is sum of squares of projections

            # amplitude of 00...
            next_a0_if_0 = a0 * c
            # 11...
            next_a1_if_0 = a1 * s

            prob_0 = next_a0_if_0 ** 2 + next_a1_if_0 ** 2

            r = random()

            if r <= prob_0:
                result = 0
                norm = sqrt(prob_0)
                if norm > 0:
                    self.shared_state.amp0 = next_a0_if_0 / norm
                    self.shared_state.amp1 = next_a1_if_0 / norm
                else:
                    self.shared_state.amp0 = 0
                    self.shared_state.amp1 = 0
            else:
                result = 1
                # |1> is [-sin, cos]
                next_a0_if_1 = a0 * (-s)
                next_a1_if_1 = a1 * c

                norm = sqrt(next_a0_if_1 ** 2 + next_a1_if_1 ** 2)
                if norm > 0:
                    self.shared_state.amp0 = next_a0_if_1 / norm
                    self.shared_state.amp1 = next_a1_if_1 / norm
                else:
                    self.shared_state.amp0 = 0
                    self.shared_state.amp1 = 0

        # unentagle this photon
        self.shared_state.n_remaining -= 1
        return result
