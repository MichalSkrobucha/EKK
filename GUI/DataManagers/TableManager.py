import pandas as pd


class TableManager:
    def __init__(self):
        self.data = {
            "Alice bits": [],
            "Alice bases": [],
            "Bob bases": [],
            "Bob bits": [],
            "Bob hits": [],
            "Key bits": [],
            "Eve bases": [],
            "Eve bits": []
        }

    def clear(self):
        for key in self.data.keys():
            self.data[key].clear()

    # _fix_length i get_data_len nie są już krytyczne przy bezpiecznym podejściu,
    # ale get_data_len używasz w argumentach, więc zostawiamy.
    def get_data_len(self, key):
        return len(self.data[key])

    def append_data(self, key, value):
        self.data[key].append(value)

    # --- LOGERY (Bez zmian, tylko wywołują bezpieczną logikę) ---
    def log_alice_base(self, base, if_e91=False):
        base_symbol = base if if_e91 else (base if base == -1 else "+x"[base])
        self.append_data("Alice bases", base_symbol)
        # Próbujemy przeliczyć dla AKTUALNEGO kroku tej listy
        self._try_calculate_logic(len(self.data["Alice bases"]) - 1)

    def log_alice_bit(self, bit):
        self.append_data("Alice bits", bit)
        self._try_calculate_logic(len(self.data["Alice bits"]) - 1)

    def log_bob_base(self, base, if_e91=False):
        base_symbol = base if if_e91 else (base if base == -1 else "+x"[base])
        self.append_data("Bob bases", base_symbol)
        self._try_calculate_logic(len(self.data["Bob bases"]) - 1)

    def log_bob_bit(self, bit):
        self.append_data("Bob bits", bit)
        self._try_calculate_logic(len(self.data["Bob bits"]) - 1)

    def _try_calculate_logic(self, step: int):
        """
        Sprawdza czy dane istnieją. Jeśli nie - wychodzi bez błędu.
        """
        if step < 0:
            return

        if step >= len(self.data["Alice bases"]): return
        if step >= len(self.data["Bob bases"]): return
        if step >= len(self.data["Bob bits"]): return

        alice_base = self.data["Alice bases"][step]
        bob_base = self.data["Bob bases"][step]
        bob_bit = self.data["Bob bits"][step]

        if alice_base == "" or bob_base == "" or bob_bit == "":
            return

        match = (alice_base == bob_base)
        hit_val = '✔️' if match else '❌'
        key_val = str(bob_bit) if match else "-"

        self._safe_set_result("Bob hits", step, hit_val)
        self._safe_set_result("Key bits", step, key_val)

    def _safe_set_result(self, key, index, value):
        """
        Pozwala zapisać wynik w dowolnym miejscu listy,
        nawet jeśli lista jest za krótka (dopełnia ją).
        """
        target_list = self.data[key]
        current_len = len(target_list)

        if index == current_len:
            target_list.append(value)
        elif index < current_len:
            target_list[index] = value
        else:
            missing = index - current_len
            target_list.extend([""] * missing)
            target_list.append(value)

    def get_dataframe(self) -> pd.DataFrame:
        if not self.data:
            return pd.DataFrame()

        lengths = [len(lst) for lst in self.data.values()]
        if not lengths:
            return pd.DataFrame()

        max_len = max(lengths)
        if max_len == 0:
            return pd.DataFrame()

        display_data = {}
        for key, original_list in self.data.items():
            # Kopia listy
            col = list(original_list)
            # Wyrównanie do wyświetlania
            missing = max_len - len(col)
            if missing > 0:
                col.extend([""] * missing)
            display_data[key] = col

        return pd.DataFrame(display_data)