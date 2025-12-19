from random import shuffle
from hashlib import sha256


class alice:
    def __init__(self, bits: list[int]):
        self.bits: list[int] = bits
        self.i: int = 0
        self.n: int = 0

        self.blocks: list[list[int]] = []
        self.alice_parities: list[int] = []

    def permute(self) -> list[int]:
        """Alicja generuje permutacje"""
        permutation: list[int] = list(range(len(self.bits)))
        shuffle(permutation)

        self.bits = [self.bits[i] for i in permutation]

        return permutation

    def split_into_blocks(self) -> None:
        """Alicja dzieli bity na bloki"""
        n: int = min(len(self.bits) // 4, 2 * 2 ** (self.i + 1))
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

    def privacy_amplification(self) -> None:
        """Wzmocnienie prywatności"""
        pass