from hashlib import sha256


class bob:
    def __init__(self, bits: list[int]):
        self.bits = bits
        self.i = 0

        self.blocks: list[list[int]] = []
        self.bob_parities: list[int] = []

    def get_alice_permutation(self, permutation: list[int]):
        """Bob odbiera permutację Alicji i dzieli permutuje swój klucz"""
        self.bits = [self.bits[i] for i in permutation]

    def split_into_blocks(self) -> None:
        """Bob dzieli bity na bloki"""
        n: int = min(len(self.bits) // 4, 2 * 2 ** (self.i + 1))
        self.i += 1

        self.blocks = [self.bits[i: min(i + n, len(self.bits))] for i in range(0, len(self.bits), n)]

    def compute_parity_bits(self) -> list[int]:
        """Bob oblicza parzystosci bloków"""
        self.bob_parities = [sum(block) % 2 for block in self.blocks]
        return self.bob_parities

    def get_alice_parity(self, alice_parities: list[int]) -> None:
        """Bob odbiera parzystosci blokó Alicji i dzieli swoje gdy parzystości się nie zgadzają (gdy blok jest jednobitowy - zmienia bit)"""
        blocks: list[list[int]] = []
        bob_parities: list[int] = self.bob_parities

        for (i, (a, b)) in enumerate(zip(alice_parities, bob_parities)):
            if a == b:
                blocks.append(self.blocks[i])
            else:
                block_len: int = len(self.blocks[i])

                if block_len > 1:
                    blocks.append(self.blocks[i][:block_len // 2])
                    blocks.append(self.blocks[i][block_len // 2:])
                else:
                    self.blocks[i][0] = 1 - self.blocks[i][0]
                    blocks.append(self.blocks[i])

        self.blocks = blocks

    def flatten_blocks(self) -> None:
        """Bob zamienia swoje bloki na bity"""
        self.bits = [bit for block in self.blocks for bit in block]

    def get_key_hash(self, alice_hash: bytes) -> bool:
        """Bob odbiera hash klucza Alicji i wysyła czy zgadza się z jego kluczem"""
        return alice_hash == sha256(bytes.fromhex(
            ''.join([hex(num)[2:] for num in
                     [sum([x * 2 ** i for (i, x) in enumerate(halfbyte)]) for halfbyte in
                      [self.bits[i: min(len(self.bits), i + 4)] for i in
                       range(0, len(self.bits), 4)]]]))).digest()

    def privacy_amplification(self) -> None:
        """Wzmocnienie prywatności"""
        pass
