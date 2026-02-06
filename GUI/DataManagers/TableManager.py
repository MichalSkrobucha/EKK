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

    def _fix_length(self):
        """
        Sprawdza, czy tabela jest wystarczająco długa dla podanego kroku.
        """
        max_len = max(map(len, self.data.values()), default=0)

        for key in self.data:
            missing_rows = max_len - len(self.data[key])
            self.data[key].extend([None] * missing_rows)

    def get_data_len(self, key):
        length = len([x for x in self.data[key] if x is not None])
        return length

    def append_data(self, key, value):
        idx = next((i for i, x in enumerate(self.data[key]) if x is None), -1)
        if idx != -1:
            self.data[key][idx] = value
        else:
            self.data[key].append(value)

    def log_alice(self, bit, base):
        base_symbol = "+x"[base]
        self.append_data("Alice bits", bit)
        self.append_data("Alice bases", base_symbol)
        self._fix_length()

    def log_bob(self, bit, base):
        base_symbol = "+x"[base]
        self.append_data("Bob bits", bit)
        self.append_data("Bob bases", base_symbol)
        self._try_calculate_logic(self.get_data_len("Bob bases")-1)
        self._fix_length()

    def _try_calculate_logic(self, step: int):
        """
        Sprawdza, czy w danym wierszu są już dane Alice i Boba.
        Jeśli tak -> oblicza Bob hits i Key bits.
        """
        alice_base = self.data["Alice bases"][step]
        bob_base = self.data["Bob bases"][step]
        bob_bit = self.data["Bob bits"][step]

        if alice_base is not None and bob_base is not None:
            match = (alice_base == bob_base)
            self.data["Bob hits"][step] = '✔️' if match else '❌'
            if match:
                self.data["Key bits"][step] = bob_bit
            else:
                self.data["Key bits"][step] = "-"

    def get_dataframe(self) -> pd.DataFrame:
        """Zwraca gotową tabelę"""
        return pd.DataFrame(self.data)
