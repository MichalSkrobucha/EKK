from auth_channel import channel
from auth_hash import hash


class analysis:
    def __init__(self):
        pass

    # (M, T) -> (count_of_eq_prob_hashes) // close_to_eq
    def getPossibleHashesCount(self, m_exp: int, t_exp: int):
        for i in range(1, m_exp + 1):
            for j in range(1, t_exp + 1):
                try:
                    c: channel = channel()
                    c.setupValues_andClear(i, j, 0, 0, 0)

                    print(i, j, len(c.find_possible_hashes()))
                except Exception as e:
                    pass

    # (M, T, given_mts) / (M, T, iters) -> (how_many_possible_hashes_left)
    def getNarrowDistr(self, M: int, T: int, given_mts: int, mts: bool, n: int):
        pass

    # (M, T, given_mts, mts_to_forge) -> (guess_probability, best_guess_probability)
    def getGuessProbabilities(self, M: int, T: int, given_mts: int, mts_to_forge: int, n: int):
        pass

    # (M, T) -> (iters_needed_to_narrow_to_1) -> (number_of_eavesdropped_mts)
    def getItersNeededToNarrowTo1(self, M: int, T: int, n: int):
        pass
