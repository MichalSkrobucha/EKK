from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon
from random import randint, binomialvariate, shuffle

from math import ceil
from hashlib import sha256

logger = SimLogger()


class Bob:
    channel: Channel

    def __init__(self, channel: Channel, efficiency: float, error: float) -> None:
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param efficiency: How often detectors react to photons (properly)
        :param error: How often detectors click without photon
        """
        self.channel = channel
        self.efficiency = efficiency
        self.error = error
        self.sample_bits = 0.25
        self.qber: float = 0.0

        self.bases: list[int] = []
        self.bits: list[int] = []
        self.aliceStates: list[tuple[int, int]] = []  # 1st - computational basis, 2nd - Hadamard basis
        self.keyIDs: list[int] = []
        self.keyBits: list[int] = []

        self.sampleIds: list[int] = []
        self.aliceSample: list[int] = []
        self.bobSample: list[int] = []

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

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.bases.clear()
        self.bits.clear()
        self.aliceStates.clear()
        self.keyIDs.clear()
        self.keyBits.clear()

        self.sampleIds.clear()
        self.aliceSample.clear()
        self.bobSample.clear()

    def recieve(self):
        impulse: list[Photon] = self.channel.read()
        logger.log(f"Bob read {len(impulse)} photons from channel")

        # measurments
        measurments: list[list[int]] = [[0, 0], [0, 0]]  # [base][bit], wartosć = liczba kliknięć detektora

        for p in impulse:
            base: int = randint(0, 1)
            bit: int = p.measure(base)

            # does detector click (properly)
            measurments[base][bit] += binomialvariate(p=self.efficiency)

        # error (false clicks)
        for (base, bit) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            if measurments[base][bit] == 0:
                measurments[base][bit] += binomialvariate(p=self.error)

        logger.log(f"Bob measured: \n"
                   f"\t\t\t{measurments[0][0]} clicks in base 0 (computational) of value 0 (horizontal)\n"
                   f"\t\t\t{measurments[0][1]} clicks in base 0 (computational) of value 1 (vertical)\n"
                   f"\t\t\t{measurments[1][0]} clicks in base 1 (Hadamard) of value 0 (diagonal 45)\n"
                   f"\t\t\t{measurments[1][1]} clicks in base 1 (Hadamard) of value 1 (diagonal -45)")
        # Bob reades detectors output and interprets it

        clickCount: int = measurments[0][0] + measurments[0][1] + measurments[1][0] + measurments[1][1]
        logger.log(f"Bob measured {clickCount} clicks")

        if clickCount == 0:
            self.bases.append(-1)  # BASE = -1 -unclear measurment (unable to clearly decide what was the outcome)
            self.bits.append(-1)  # so indexes are in right place
            logger.log(f"Bob's measure is unclear")
            return
        elif clickCount == 1:
            for (base, bit) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                if measurments[base][bit] == 1:
                    self.bases.append(base)
                    self.bits.append(bit)
                    logger.log(f"Bob's base is {base} and bit is {bit}")
                    return
        else:
            # how many clicks in basis
            clicksInBase0: int = measurments[0][0] + measurments[0][1]
            clicksInBase1: int = measurments[1][0] + measurments[1][1]

            base: int = -1

            # many clicks in one base (second one has 0)
            if clicksInBase1 == 0:
                base = 0
            elif clicksInBase0 == 0:
                base = 1

            # as below (clicks only in one base)
            if base >= 0:
                # same bit
                if measurments[base][0] == 0:
                    self.bases.append(base)
                    self.bits.append(1)
                    logger.log(f"Bob's base is {base} and bit is {1}")
                    return
                elif measurments[base][1] == 0:
                    self.bases.append(base)
                    self.bits.append(0)
                    logger.log(f"Bob's base is {base} and bit is {0}")
                    return

                # different bits
                self.bases.append(-1)
                self.bits.append(-1)
                logger.log(f"Bob's measure is unclear")
                return

            # clicks in both bases
            # clicks on only one detector in given base (second detecxtor has 0 clicks) (clear base)
            is0Clean: bool = (measurments[0][0] * measurments[0][1] == 0)
            is1Clean: bool = (measurments[1][0] * measurments[1][1] == 0)

            bit: int

            if is0Clean and is1Clean:
                # both basis are clear
                # which one has more clicks? (higher trust)
                if clicksInBase0 > clicksInBase1:
                    base = 0
                elif clicksInBase0 < clicksInBase1:
                    base = 1
                else:
                    # ==
                    self.bases.append(-1)
                    self.bits.append(-1)
                    logger.log(f"Bob's measure is unclear")
                    return

                if base >= 0:
                    if measurments[base][0] > 0:
                        bit = 0
                    else:
                        bit = 1
                self.bases.append(base)
                self.bits.append(bit)
                logger.log(f"Bob's base is {base} and bit is {bit}")
            elif is0Clean:
                # tonly base 0(+) is clear
                base = 0
                if measurments[0][0] > 0:
                    bit = 0
                else:
                    bit = 1
                self.bases.append(base)
                self.bits.append(bit)
                logger.log(f"Bob's base is {base} and bit is {bit}")
            elif is1Clean:
                # only base 1(x) is clear
                base = 1
                if measurments[1][0] > 0:
                    bit = 0
                else:
                    bit = 1
                self.bases.append(base)
                self.bits.append(bit)
                logger.log(f"Bob's base is {base} and bit is {bit}")
            else:
                # neither base is clear (all 4 detectos clicked)
                self.bases.append(-1)
                self.bits.append(-1)
                logger.log(f"Bob's measure is unclear")

    def recieveStates(self, states: list[tuple[int, int]]) -> None:
        self.aliceStates = states

    def sieveStates(self) -> None:
        for (i, (bit, base, alice)) in enumerate(zip(self.bits, self.bases, self.aliceStates)):
            if base != -1:
                # Bob's measured base has different bit than Alice -> it was the other bit
                if alice[base] != bit:
                    self.keyIDs.append(i)
                    self.keyBits.append(alice[1 - base])

        logger.log(f'Bob got {len(self.keyBits)} bits of key')

    def announceUsedStates(self) -> list[int]:
        return self.keyIDs

    def sendSampleIds(self) -> list[int]:
        """
        Sends IDs of bits which are to used as samples (for QBER)
        :return sampleIds: IDs of bits (no need for order)
        """
        l: int = len(self.keyBits)
        ids: list[int] = list(range(l))
        shuffle(ids)

        self.sampleIds = ids[:int(self.sample_bits * l)]

        logger.log("Bob is sending to Alice indexes of sample bits")

        return self.sampleIds

    def sendSample(self) -> list[int]:
        """
        Sends sample to Alice (based on send IDs)
        :return: List of Bobs's sample bits (in order of IDs in its respective list)
        """
        for i in self.sampleIds:
            self.bobSample.append(self.keyBits[i])

        logger.log("Bob is sending his samples to Alice")

        return self.bobSample

    def receiveSamples(self, sample: list[int]) -> None:
        """
        Gets sample bits from Alice
        :param sample: List of Alice's sample bits (in order of IDs in its respective list)
        """
        self.aliceSample = sample
        logger.log(f"Bob is recieving samples from Alice {sample}")

    def calculateQBER(self) -> None:
        """
        Calculates QBER based on his and Alice's sample
        """
        difference: int = 0

        for (a, b) in zip(self.aliceSample, self.bobSample):
            difference += a ^ b

        try:
            self.qber: float = difference / len(self.aliceSample)
        except ZeroDivisionError:
            logger.error(f"ZeroDivisionError")

        logger.log(f"Bob is calculating QBER: {self.qber}")


    def prepareForErrorCorrection(self):
        sievedBits = list(self.keyBits)

        for i in range(len(sievedBits)):
            if i not in self.sampleIds:
                self.keyBits.append(sievedBits[i])

        kb_pad: int = 0 if len(self.keyBits) % 8 == 0 else 8 - len(self.keyBits) % 8
        self.keyBits += [0] * kb_pad

        self.max_length = len(self.keyBits) // 2
        self.start_length = ceil (1 / (self.qber + 1 / len(self.keyBits)))

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
        quads : list[list[int]] = [self.keyBits[i : i + 4] for i in range(0, len(self.keyBits), 4)]
        quad_vals : list[int] = [sum([2**(3 - i) * b for (i, b) in enumerate(q)]) for q in quads]
        quad_hex : list[str] = [hex(q)[2:] for q in quad_vals]
        hex_bytes : str = ''.join(quad_hex)
        b : bytes = bytes.fromhex(hex_bytes) + self.random_bytes
        self.key = sha256(b).digest()
