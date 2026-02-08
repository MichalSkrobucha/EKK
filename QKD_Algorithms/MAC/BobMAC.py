from MAC.HashMAC import HashMAC as Hash

class BobMAC():
    def __init__(self, h: hash):
        self.h: hash = h

    def recieve_message(self, mt: tuple[int, int]) -> bool:
        return self.h(mt[0]) == mt[1]
