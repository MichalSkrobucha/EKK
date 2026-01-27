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
        for key in self.data:
            self.data[key].clear()

    def add_step(self,
                 alice_bit: int, alice_base: int,
                 bob_bit: int, bob_base: int,
                 eve_present: bool = False, eve_base: int = None, eve_bit: int = None):
        """
        Dodaje jeden kompletny wiersz do tabeli.
        Zapewnia spójność danych (brak dziur).
        """

        # --- 1. ALICE ---
        self.data["Alice bits"].append(alice_bit)
        # Zamiana: 0 -> +, 1 -> x
        self.data["Alice bases"].append('+' if alice_base == 0 else 'x')

        # --- 2. BOB ---
        # Czy Bob odebrał foton (czy nie jest to -1)
        if bob_base == -1 or bob_bit == -1:
            self.data["Bob bases"].append("-")
            self.data["Bob bits"].append("-")
            self.data["Bob hits"].append("-")
            self.data["Key bits"].append("-")
        else:
            # Foton odebrany
            self.data["Bob bases"].append('+' if bob_base == 0 else 'x')
            self.data["Bob bits"].append(bob_bit)

            # Logika "Hits" (Sifting): Czy bazy są identyczne?
            bases_match = (alice_base == bob_base)
            self.data["Bob hits"].append('✔' if bases_match else 'X')

            # Logika "Key bits": Jeśli bazy zgodne -> bit, jeśli nie -> kreska
            if bases_match:
                self.data["Key bits"].append(bob_bit)
            else:
                self.data["Key bits"].append("-")

        # --- 3. EVE ---
        # Dane Ewy tylko jeśli podsłuch jest włączony i Ewa dokonała pomiaru
        if eve_present and eve_base is not None and eve_base != -1:
            self.data["Eve result"].append('+' if eve_base == 0 else 'x')
            self.data["Eve bits"].append(eve_bit)
        else:
            # Jeśli Ewy nie ma lub nie zmierzyła - kreska (żeby tabela się nie rozjechała)
            self.data["Eve result"].append("-")
            self.data["Eve bits"].append("-")

    def get_dataframe(self) -> pd.DataFrame:
        """Zwraca gotową tabelę"""
        return pd.DataFrame(self.data)
