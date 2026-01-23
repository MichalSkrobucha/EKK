from auth_hash import hash
from random import randint


class alice:
    def __init__(self, qr: tuple[int, int], M: int, T: int):
        self.h: hash = hash(M, T, qr[0], qr[1])

        self.possible_messages: list[int] = [m for m in range(M)]

    def send_message(self) -> tuple[int, int]:
        i: int = randint(0, len(self.possible_messages) - 1)
        m: int = self.possible_messages.pop(i)

        return (m, self.h(m))
