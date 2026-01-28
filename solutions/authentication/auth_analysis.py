from auth_channel import channel
from auth_hash import hash
from auth_eve import eve
from random import choice, sample
import statistics

import pandas as pd


class analysis:
    def __init__(self):
        pass

    def run_analysis(self):
        f_name = 'mac_comprehensive_analysis.xlsx'

        print(f"Rozpoczynam kompleksową analizę. Wyniki trafią do: {f_name}")

        with pd.ExcelWriter(f_name, engine='openpyxl') as writer:
            print("\n[1/2] Generowanie ogólnego podsumowania (stałe given_mts=2)...")
            summary_data = []

            fixed_given_mts = 2
            fixed_mts_to_forge = 1

            for m_exp in range(2, 7):
                M = 2 ** m_exp
                print(f"  -> Przetwarzanie M_exp={m_exp}...")

                for t_exp in range(2, m_exp + 1):
                    try:
                        hashes_count = self.getPossibleHashesCount(m_exp, t_exp)
                        if hashes_count == 0:
                            continue

                        avg_left = self.getNarrowDistr(m_exp, t_exp, fixed_given_mts, n1=5, n2=5)
                        total_p, best_p = self.getGuessProbabilities(m_exp, t_exp, fixed_given_mts, fixed_mts_to_forge,
                                                                     n=15)
                        avg_iters = self.getItersNeededToNarrowTo1(m_exp, t_exp, n=10)

                        summary_data.append({
                            "M_exp": m_exp,
                            "M (Size)": M,
                            "T_exp": t_exp,
                            "T (Tags)": 2 ** t_exp,
                            "Possible Hashes": hashes_count,
                            "Avg Hashes Left (mts=2)": avg_left,
                            "Crack Success (Best Guess)": best_p,
                            "Avg Msgs to Break": avg_iters
                        })
                    except Exception as e:
                        print(f"    [!] Error M={M}, T=2^{t_exp}: {e}")

            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name="General_Summary", index=False)
                print("  -> Arkusz 'General_Summary' zapisany.")

            print("\n[2/2] Generowanie szczegółowych rozbić (zmienne parametry ataku)...")
            detailed_data = []

            for m_exp in range(2, 7):
                M = 2 ** m_exp
                print(f"  -> Analiza szczegółowa dla M_exp={m_exp}...")

                for t_exp in range(2, m_exp + 1):
                    if self.getPossibleHashesCount(m_exp, t_exp) == 0:
                        continue

                    mts_checkpoints = sorted(list(set([
                        2,
                        int(M ** 0.5),
                        int(M / 2)
                    ])))
                    mts_checkpoints = [x for x in mts_checkpoints if 2 <= x < M]

                    for given_mts in mts_checkpoints:
                        for mts_to_forge in [1, 3]:
                            try:

                                avg_left = self.getNarrowDistr(m_exp, t_exp, given_mts, n1=5, n2=5)
                                total_p, best_p = self.getGuessProbabilities(m_exp, t_exp, given_mts, mts_to_forge,
                                                                             n=15)

                                detailed_data.append({
                                    "M_exp": m_exp,
                                    "M (Size)": M,
                                    "T_exp": t_exp,
                                    "T (Tags)": 2 ** t_exp,
                                    "Eavesdropped Msgs": given_mts,
                                    "Forgeries Attempted": mts_to_forge,
                                    "Avg Hashes Left": avg_left,
                                    "Success Rate (Total)": total_p,
                                    "Success Rate (Best Guess)": best_p
                                })
                            except Exception as e:
                                pass

            if detailed_data:
                df_detailed = pd.DataFrame(detailed_data)
                df_detailed.to_excel(writer, sheet_name="Detailed_Breakdown", index=False)
                print("  -> Arkusz 'Detailed_Breakdown' zapisany.")

        print(f"\n[!] Proces zakończony pomyślnie. Plik: {f_name}")

    # (M, T) -> (count_of_eq_prob_hashes) // close_to_eq
    def getPossibleHashesCount(self, m_exp: int, t_exp: int):
        c = channel()
        return len(c.possible_hashes)

    # (M, T, given_mts) / (M, T, iters) -> (how_many_possible_hashes_left)
    def getNarrowDistr(self, m_exp: int, t_exp: int, given_mts: int, n1=10, n2=10):
        c = channel()
        c.setupValues_andClear(m_exp, t_exp, 0, 0, 0)

        M = 2 ** m_exp
        T = 2 ** t_exp

        possible_hashes: list[tuple[int, int]] = list(c.find_possible_hashes())
        p = c.p
        message_space = list(range(M))

        outer_averages = []

        true_hashes_to_test = [choice(possible_hashes) for _ in range(n1)]

        for (q, r) in true_hashes_to_test:
            trial_results = []
            h_true = hash(M, T, q, r, p)  #

            for _ in range(n2):
                e = eve(M, T, p, possible_hashes)

                sampled_messages = sample(message_space, given_mts)

                for m in sampled_messages:
                    t = h_true(m)
                    e.eavesdrop((m, t))

                e.narrow_possible_hashes()
                trial_results.append(len(e.possible_hashes))

            outer_averages.append(statistics.mean(trial_results))

        final_avg = statistics.mean(outer_averages)
        print(f"Average hashes remaining for M={M}, T={T}, mts={given_mts}: {final_avg}")
        return final_avg

    # (M, T, given_mts, mts_to_forge) -> (guess_probability, best_guess_probability)
    def getGuessProbabilities(self, m_exp: int, t_exp: int, given_mts: int, mts_to_forge: int, n: int = 100):
        c = channel()
        M = 2 ** m_exp
        T = 2 ** t_exp
        c.setupValues_andClear(m_exp, t_exp, 0, 0, 0)

        p = c.p
        all_valid_hashes = c.find_possible_hashes()
        message_space = list(range(M))

        total_success_rate = []
        best_guess_success = []

        for _ in range(n):
            q_true, r_true = choice(all_valid_hashes)
            h_true = hash(M, T, q_true, r_true, p)

            e = eve(M, T, p, all_valid_hashes)

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
    def getItersNeededToNarrowTo1(self, m_exp: int, t_exp: int, n: int = 30):
        import statistics
        from random import choice, sample
        from auth_channel import channel
        from auth_eve import eve
        from auth_hash import hash

        # Inicjalizacja kanału w celu wyznaczenia parametrów p oraz zbioru poprawnych haszy
        c = channel()
        M = 2 ** m_exp
        T = 2 ** t_exp
        # setupValues_andClear automatycznie oblicza p i generuje initial possible_hashes
        c.setupValues_andClear(m_exp, t_exp, 0, 0, 0)

        p = c.p
        all_valid_hashes = c.find_possible_hashes()
        message_space = list(range(M))

        messages_needed_results = []

        for _ in range(n):
            q_true, r_true = choice(all_valid_hashes)
            h_true = hash(M, T, q_true, r_true, p)

            e = eve(M, T, p, all_valid_hashes)

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

        avg_mts = statistics.mean(messages_needed_results) if messages_needed_results else 0

        return avg_mts
