import pandas as pd


class TableManager:
    def __init__(self):
        # Inicjalizacja pustych list
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
        for key in self.data:
            self.data[key] = []

    def update_from_simulation(self, sim_manager, protocol_name):
        """
        Pobiera PEŁNE listy z SimManagera.
        ProtocolPage decyduje ile z tego wyświetlić.
        """
        self.clear()

        alice = sim_manager.alice
        bob = sim_manager.bob
        eve = getattr(sim_manager, 'eve', None)

        a_bits = getattr(alice, 'bits', [])
        a_bases = getattr(alice, 'bases', [])
        b_bits = getattr(bob, 'bits', [])
        b_bases = getattr(bob, 'bases', [])

        e_bits = getattr(eve, 'bits', []) if eve else []
        e_bases = getattr(eve, 'bases', []) if eve else []

        max_len = max(len(a_bits), len(b_bits))

        for i in range(max_len):
            # --- ALICE ---
            if i < len(a_bits):
                self.data["Alice bits"].append(a_bits[i])
            else:
                self.data["Alice bits"].append("")

            if i < len(a_bases):
                base_val = a_bases[i]
                if isinstance(base_val, int) and base_val in [0, 1]:
                    base_symbol = "+" if base_val == 0 else "x"
                else:
                    base_symbol = base_val
                self.data["Alice bases"].append(base_symbol)
            else:
                self.data["Alice bases"].append("")

            # --- BOB ---
            if i < len(b_bits):
                self.data["Bob bits"].append(b_bits[i])
            else:
                self.data["Bob bits"].append("")

            if i < len(b_bases):
                base_val = b_bases[i]
                if isinstance(base_val, int) and base_val in [0, 1]:
                    base_symbol = "+" if base_val == 0 else "x"
                else:
                    base_symbol = base_val
                self.data["Bob bases"].append(base_symbol)
            else:
                self.data["Bob bases"].append("")

            # --- EVE ---
            if i < len(e_bits):
                self.data["Eve bits"].append(e_bits[i])
            else:
                self.data["Eve bits"].append("")

            if i < len(e_bases):
                base_val = e_bases[i]
                if isinstance(base_val, int) and base_val in [0, 1]:
                    base_symbol = "+" if base_val == 0 else "x"
                else:
                    base_symbol = base_val
                self.data["Eve bases"].append(base_symbol)
            else:
                self.data["Eve bases"].append("")

            # --- MATCH ---
            curr_a_base = self.data["Alice bases"][-1]
            curr_b_base = self.data["Bob bases"][-1]
            curr_b_bit = self.data["Bob bits"][-1]

            match_symbol = ""
            key_bit = "-"

            if str(curr_a_base) != "" and str(curr_b_base) != "" and str(curr_b_bit) != "":
                if str(curr_a_base) == str(curr_b_base):
                    match_symbol = "✔️"
                    key_bit = str(curr_b_bit)
                else:
                    match_symbol = "❌"

            self.data["Bob hits"].append(match_symbol)
            self.data["Key bits"].append(key_bit)

    def get_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)