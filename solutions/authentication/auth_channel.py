from auth_alice import alice
from auth_bob import bob
from auth_eve import eve

class channel:

    ifEve : bool = False

    def __init__(self, a : alice, b : bob, M : int, T : int):
        self.alice : alice = a
        self.bob : bob = b
        self.M : int = M
        self.T : int = T

        self.eve : eve = eve(M, T)

    def run(self):
        pass

