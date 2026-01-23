from auth_hash import hash

class alice:
    def __init__(self, qr :tuple[int, int], M : int, T : int):
        self.h : hash = hash(M, T, qr[0], qr[1])