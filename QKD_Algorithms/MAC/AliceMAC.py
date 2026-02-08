from .HashMAC import HashMAC as Hash
from random import randint


class AliceMAC:
    def __init__(self, h: Hash, possible_messages: list[int]):
        self.h: Hash = h
        self.possible_messages: list[int] = possible_messages

    def send_message(self) -> tuple[int, int]:
        i: int = randint(0, len(self.possible_messages) - 1)
        m: int = self.possible_messages.pop(i)

        return (m, self.h(m))
