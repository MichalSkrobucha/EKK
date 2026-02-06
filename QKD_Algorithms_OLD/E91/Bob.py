from .Channel import Channel
import random

from .Photon import Photon

from math import ceil
from hashlib import sha256


class Bob:
    channel: Channel
    bases: dict = {}
    results: list[dict] = []
    raw_key: list[int]

    def __init__(self, channel: Channel, avaliable_bases: list, bases_dict: dict):
        self.channel = channel
        self.channel.name = "channel_B"
        self.avaliable_bases = avaliable_bases
        self.bases_dict = bases_dict
        self.raw_key: list[int] = []

        self.test_key = []

        self.i: int = 0

        self.keyBits: list[int] = []

        self.permutation: list[int] = []
        self.alice_hash: bytes = bytes()

        self.blocks: list[list[int]] = []
        self.bob_parities: list[int] = []
        self.max_length: int = 0
        self.start_length: int = 0

        self.random_bytes: bytes = b''
        self.key: bytes = b''

    def choose_base(self):
        base_idx = random.choice([1, 2, 3])
        return self.bases[base_idx]

    def receive(self) -> None:
        if len(self.channel.container) > 0:
            photon: Photon = self.channel.read()[0]  # Only 1 photon for now
            base_idx = random.choice(self.avaliable_bases)
            base = self.bases_dict[base_idx]
            bit = photon.measure(base)

            print(f'Bob measured bit {bit} in base {base_idx}')

            self.results.append({'base_idx': base_idx, 'base': base, 'bit': bit})

    def prepareForErrorCorrection(self):
        self.keyBits = [1 - b for b in self.raw_key]

        kb_pad: int = 0 if len(self.keyBits) % 8 == 0 else 8 - len(self.keyBits) % 8
        self.keyBits += [0] * kb_pad

        self.max_length = len(self.keyBits) // 2
        self.start_length = ceil(len(self.keyBits) ** 0.5)

    def get_alice_permutation(self, permutation: list[int]):
        """Bob odbiera permutację Alicji i dzieli permutuje swój klucz"""
        self.permutation = permutation

        self.keyBits = [self.keyBits[i] for i in permutation]

    def split_into_blocks(self) -> None:
        """Bob dzieli bity na bloki"""
        n: int = min(self.max_length, self.start_length * 2 ** self.i)
        self.i += 1

        self.blocks = [self.keyBits[i: min(i + n, len(self.keyBits))] for i in range(0, len(self.keyBits), n)]

    def compute_parity_bits(self) -> list[int]:
        """Bob oblicza parzystosci bloków"""
        self.bob_parities = [sum(block) % 2 for block in self.blocks]
        return self.bob_parities

    def get_alice_parity(self, alice_parities: list[int]) -> None:
        """Bob odbiera parzystosci bloków Alicji i dzieli swoje gdy parzystości się nie zgadzają (gdy blok jest jednobitowy - zmienia bit)"""
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
        self.keyBits = [bit for block in self.blocks for bit in block]

    def get_key_hash(self, alice_hash: bytes) -> None:
        """Bob odbiera hash klucza Alicji i wysyła czy zgadza się z jego kluczem"""
        self.alice_hash = alice_hash

    def check_hash(self) -> bool:
        return self.alice_hash == sha256(bytes.fromhex(
            ''.join([hex(num)[2:] for num in
                     [sum([x * 2 ** i for (i, x) in enumerate(halfbyte)]) for halfbyte in
                      [self.keyBits[i: min(len(self.keyBits), i + 4)] for i in
                       range(0, len(self.keyBits), 4)]]]))).digest()

    def unpermute(self) -> None:
        bits: list[int] = [0 for _ in self.keyBits]

        for (new, old) in enumerate(self.permutation):
            bits[old] = self.keyBits[new]

        self.keyBits = bits

    def get_random_bytes(self, r_bytes: bytes) -> None:
        self.random_bytes = r_bytes

    def get_final_key(self) -> None:
        self.keyBits += [0] * (8 - len(self.keyBits) % 8)
        quads: list[list[int]] = [self.keyBits[i: i + 4] for i in range(0, len(self.keyBits), 4)]
        quad_vals: list[int] = [sum([2 ** (3 - i) * b for (i, b) in enumerate(q)]) for q in quads]
        quad_hex: list[str] = [hex(q)[2:] for q in quad_vals]
        hex_bytes: str = ''.join(quad_hex)
        b: bytes = bytes.fromhex(hex_bytes) + self.random_bytes
        self.key = sha256(b).digest()
