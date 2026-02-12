from MAC.HashMAC import HashMAC as Hash
from MAC.EveMAC import EveMAC as eve

from random import choice, sample, shuffle

import statistics
from itertools import count
import pandas as pd


class AnalysisMAC:

    def __init__(self):
        pass

    # ... (reszta importów bez zmian)

    def run_analysis(self, start_m=2, save_threshold=4):
        general_data = []
        detailed_data = []

        num_range = 7

        print(f"Rozpoczynam analizę ciągłą od m_exp={start_m}. Zapis plików od m_exp={save_threshold}.")

        # count(start_m) tworzy nieskończony iterator: start_m, start_m+1, start_m+2...
        for m_exp in count(start_m):

            for t_exp in range(2, m_exp + 1):
                print(f'\n[Ongoing] Analysis for m_exp = {m_exp}, t_exp = {t_exp}')

                possible_hashes = Hash.find_eq_prob_hashes(2 ** m_exp, 2 * t_exp)
                possible_hashes_count = len(possible_hashes)
                avg_hashes_remaining = {
                    num: self.getNarrowDegree(m_exp, t_exp, num, possible_hashes=set(possible_hashes)) for num in
                    range(1, num_range)}
                guess_probs = {
                    num: self.getGuessProbabilities(m_exp, t_exp, num, 3 * num, possible_hashes=set(possible_hashes))
                    for num in
                    range(1, num_range)}
                iters_to_sure = self.getItersNeededToNarrowTo1(m_exp, t_exp, possible_hashes=set(possible_hashes))

                print(f'\tPossible hashes: {possible_hashes_count}')
                print(f'\tEve needs {iters_to_sure} iterations to break')
                print(f'\tEve has _ hashes remaining based on how pairs she was given: {avg_hashes_remaining}')
                print(f'\tEve has (best, total) guess rate for how many pairs she was given: {guess_probs}')

                general_data.append({
                    "M_exp": m_exp,
                    "T_exp": t_exp,
                    "Possible Hashes": possible_hashes_count,
                    "Avg Msgs to Break": iters_to_sure
                })

                for num in range(1, num_range):
                    detailed_data.append({
                        "M_exp": m_exp,
                        "T_exp": t_exp,
                        "Given MTs": num,
                        "MTs to fake": 3 * num,
                        "Hashes reaming": avg_hashes_remaining[num],
                        "Guess rate": guess_probs[num][0],
                        "Best guess": guess_probs[num][1],
                    })

            if m_exp >= save_threshold:
                current_file_name = f'QKD_Algorithms\\MAC\\AuthAnalysisMAC_{m_exp}.xlsx'
                print(f'--> Saving snapshot to: {current_file_name}...')

                try:
                    with pd.ExcelWriter(current_file_name, engine='openpyxl') as writer:
                        pd.DataFrame(general_data).to_excel(writer, sheet_name="General", index=False)
                        pd.DataFrame(detailed_data).to_excel(writer, sheet_name="Detailed", index=False)
                    print(f'--> Save complete.')
                except Exception as e:
                    print(f"!!! Error saving file {current_file_name}: {e}")

    # (M, T) -> (count_of_eq_prob_hashes)
    def getPossibleHashesCount(self, m_exp: int, t_exp: int):
        return len(Hash.find_eq_prob_hashes(2 ** m_exp, 2 ** t_exp))

    # (M, T, given_mts) / (M, T, iters) -> (how_many_possible_hashes_left)
    def getNarrowDegree(self, m_exp: int, t_exp: int, given_mts: int, how_many_unique_hashes_tested: int = -1,
                        possible_hashes=None):
        M = 2 ** m_exp
        T = 2 ** t_exp
        p = Hash.next_prime(M)

        if how_many_unique_hashes_tested < 0:
            how_many_unique_hashes_tested = 2 * m_exp

        if possible_hashes is None:
            possible_hashes: list[tuple[int, int]] = list(Hash.find_eq_prob_hashes(M, T, p=p))

        message_space = list(range(M))

        outer_averages = []

        shuffle(possible_hashes)
        true_hashes_to_test = possible_hashes[:how_many_unique_hashes_tested]

        trial_results = []

        for (q, r) in true_hashes_to_test:
            h_true = Hash(M, T, q, r, p)

            e = eve(M, T, p, possible_hashes)

            if given_mts > len(message_space):
                given_mts = len(message_space)

            sampled_messages = sample(message_space, given_mts)

            for m in sampled_messages:
                t = h_true(m)
                e.eavesdrop((m, t))

            e.narrow_possible_hashes()
            trial_results.append(len(e.possible_hashes))

        mean = statistics.mean(trial_results)
        return mean

    # (M, T, given_mts, mts_to_forge) -> (guess_probability, best_guess_probability)
    def getGuessProbabilities(self, m_exp: int, t_exp: int, given_mts: int, mts_to_forge: int,
                              how_many_unique_hashes_tested: int = -1, possible_hashes=None):
        if how_many_unique_hashes_tested < 0:
            how_many_unique_hashes_tested = 2 * m_exp

        M = 2 ** m_exp
        T = 2 ** t_exp

        p = Hash.next_prime(M)
        if possible_hashes is None:
            possible_hashes: list[tuple[int, int]] = list(Hash.find_eq_prob_hashes(M, T, p=p))
        message_space = list(range(M))

        total_success_rate = []
        best_guess_success = []

        for _ in range(how_many_unique_hashes_tested):
            (q_true, r_true) = choice(possible_hashes)
            h_true = Hash(M, T, q_true, r_true, p)

            e = eve(M, T, p, possible_hashes)

            if given_mts > len(message_space):
                given_mts = len(message_space)

            eavesdropped_msgs = sample(message_space, given_mts)
            for m in eavesdropped_msgs:
                e.eavesdrop((m, h_true(m)))

            e.narrow_possible_hashes()

            remaining_msgs = [m for m in message_space if m not in eavesdropped_msgs]
            if not remaining_msgs:
                continue

            to_forge = sample(remaining_msgs, min(mts_to_forge, len(remaining_msgs)))
            fakes = e.forge_mtags(to_forge)

            results = []

            for i, (m_fake, t_fake) in enumerate(fakes):
                is_correct = (t_fake == h_true(m_fake))
                results.append(is_correct)

                if i == 0:
                    best_guess_success.append(1 if is_correct else 0)

            total_success_rate.append(sum(results) / len(results) if results else 0)

        avg_total_prob = statistics.mean(total_success_rate) if total_success_rate else 0
        avg_best_prob = statistics.mean(best_guess_success) if best_guess_success else 0

        return avg_total_prob, avg_best_prob

    # (M, T) -> (iters_needed_to_narrow_to_1) -> (number_of_eavesdropped_mts)
    def getItersNeededToNarrowTo1(self, m_exp: int, t_exp: int, how_many_unique_hashes_tested: int = -1,
                                  possible_hashes=None):
        if how_many_unique_hashes_tested < 0:
            how_many_unique_hashes_tested = 2 * m_exp

        M = 2 ** m_exp
        T = 2 ** t_exp

        p = Hash.next_prime(M)
        if possible_hashes is None:
            possible_hashes: list[tuple[int, int]] = list(Hash.find_eq_prob_hashes(M, T, p=p))
        message_space = list(range(M))

        messages_needed_results = []

        for _ in range(how_many_unique_hashes_tested):
            q_true, r_true = choice(possible_hashes)
            h_true = Hash(M, T, q_true, r_true, p)

            e = eve(M, T, p, possible_hashes)

            shuffled_msgs = sample(message_space, len(message_space))

            for count, m in enumerate(shuffled_msgs, 1):
                e.eavesdrop((m, h_true(m)))

                if count >= 2:
                    m_needed = e.narrow_possible_hashes()

                    if len(e.possible_hashes) <= 1:
                        messages_needed_results.append(m_needed)
                        break
            else:
                messages_needed_results.append(len(message_space))

        avg_mts = statistics.mean(messages_needed_results) if len(messages_needed_results) else 0

        return avg_mts


if __name__ == '__main__':
    a = AnalysisMAC()
    a.run_analysis()
