from auth_hash import hash
from random import randint


class alice:
    def __init__(self, h: hash, possible_messages: list[int]):
        self.h: hash = h
        self.possible_messages: list[int] = possible_messages

    def send_message(self) -> tuple[int, int]:
        i: int = randint(0, len(self.possible_messages) - 1)
        m: int = self.possible_messages.pop(i)

        return (m, self.h(m))
