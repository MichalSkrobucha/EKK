from random import shuffle, randbytes
from hashlib import sha256
from math import ceil


class alice:
    def __init__(self, bits: list[int], q: float = 0.25):
        self.bits: list[int] = bits
        self.i: int = 0
        self.n: int = 0

        self.permutation: list[int] = []

        self.blocks: list[list[int]] = []
        self.alice_parities: list[int] = []
        self.max_length: int = len(self.bits) // 2
        self.start_length: int = ceil(1 / q)

        self.bytes_count : int = 16
        self.random_bytes: bytes = b''
        self.key: bytes = b''

    def permute(self) -> list[int]:
        """Alicja generuje permutacje"""
        self.permutation: list[int] = list(range(len(self.bits)))
        shuffle(self.permutation)

        self.bits = [self.bits[i] for i in self.permutation]

        return self.permutation

    def split_into_blocks(self) -> None:
        """Alicja dzieli bity na bloki"""
        n: int = min(self.max_length, self.start_length * 2 ** self.i)
        self.n = n
        self.i += 1

        self.blocks = [self.bits[i: min(i + n, len(self.bits))] for i in range(0, len(self.bits), n)]

    def compute_parity_bits(self) -> list[int]:
        """Alicja oblicza parzystosci bloków"""
        self.alice_parities = [sum(block) % 2 for block in self.blocks]
        return self.alice_parities

    def get_bobs_parity(self, bob_parities: list[int]) -> None:
        """Alicja odbiera parzystosci blokó Boba i dzieli swoje gdy parzystości się nie zgadzają"""
        blocks: list[list[int]] = []
        alice_parities: list[int] = self.alice_parities

        for (i, (a, b)) in enumerate(zip(alice_parities, bob_parities)):
            if a == b:
                blocks.append(self.blocks[i])
            else:
                block_len: int = len(self.blocks[i])

                if block_len > 1:
                    blocks.append(self.blocks[i][:block_len // 2])
                    blocks.append(self.blocks[i][block_len // 2:])
                else:
                    blocks.append(self.blocks[i])

        self.blocks = blocks

    def send_key_hash(self) -> bytes:
        """Alicja wysyła hash swojego klucza"""
        return sha256(bytes.fromhex(
            ''.join([hex(num)[2:] for num in
                     [sum([x * 2 ** i for (i, x) in enumerate(halfbyte)]) for halfbyte in
                      [self.bits[i: min(len(self.bits), i + 4)] for i in
                       range(0, len(self.bits), 4)]]]))).digest()

    def unpermute(self):
        bits: list[int] = [0 for _ in self.bits]

        for (new, old) in enumerate(self.permutation):
            bits[old] = self.bits[new]

        self.bits = bits

    def send_random_bytes(self) -> bytes:
        self.random_bytes = randbytes(self.bytes_count)

        return self.random_bytes

    def get_final_key(self) -> None:
        self.bits += [0] * (8 - len(self.bits) % 8)
        quads : list[list[int]] = [self.bits[i : i + 4] for i in range(0, len(self.bits), 4)]
        quad_vals : list[int] = [sum([2**(3 - i) * b for (i, b) in enumerate(q)]) for q in quads]
        quad_hex : list[str] = [hex(q)[2:] for q in quad_vals]
        hex_bytes : str = ''.join(quad_hex)
        b : bytes = bytes.fromhex(hex_bytes) + self.random_bytes
        self.key = sha256(b).digest()