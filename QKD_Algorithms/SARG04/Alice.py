from numpy.random import poisson
from random import randint, shuffle, randbytes
from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon

from math import ceil
from hashlib import sha256

logger = SimLogger()


class Alice:
    """

    """
    mi: float
    channel: Channel
    message: list[Photon]

    def __init__(self, channel: Channel, mi: float):
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param mi: Average amount of photons in impulse
        """
        self.channel: Channel = channel
        self.mi: float = mi

        self.message: list[Photon] = []
        self.possibleStates: list[tuple[int, int]] = []
        self.bits: list[int] = []
        self.sendBases: list[int] = []
        self.keyBits: list[int] = []

        self.aliceSample: list[int] = []
        self.bobSample: list[int] = []
        self.sampleIds: list[int] = []

        self.qber: float = 0.0

        self.i: int = 0
        self.n: int = 0

        self.keyBits: list[int] = []

        self.permutation: list[int] = []

        self.blocks: list[list[int]] = []
        self.alice_parities: list[int] = []
        self.max_length: int = 0
        self.start_length: int = 0

        self.bytes_count: int = 16
        self.random_bytes: bytes = b''
        self.key: bytes = b''

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.message.clear()
        self.possibleStates.clear()
        self.bits.clear()
        self.sendBases.clear()
        self.keyBits.clear()

        self.aliceSample.clear()
        self.bobSample.clear()
        self.sampleIds.clear()

    def _generate_key(self) -> list[Photon]:
        """
        Generates next bit of key, and returns impulse of photons
        :return: impulse of photons
        """
        n_photons: int = poisson(self.mi)
        photons_list = []

        bitComputational: int = randint(0, 1)
        bitHadamard: int = 1 - bitComputational
        self.possibleStates.append((bitComputational, bitHadamard))
        sendBase: int = randint(0, 1)
        self.sendBases.append(sendBase)
        sendBit: int = bitHadamard if sendBase else bitComputational
        self.bits.append(sendBit)

        for _ in range(n_photons):
            photons_list.append(Photon(sendBase, sendBit))
            logger.log(f">>> Photon: [{sendBase}, {sendBit}]")

        self.message.extend(photons_list)
        logger.log(f"Alice generated {n_photons} photons")
        return photons_list

    def send_key(self) -> None:
        """
            Sends impulse of photons (carrying bit of a key) to the channel
        """
        logger.log("Alice sent key to the channel")
        self.channel.send(self._generate_key())

    def announceStates(self) -> list[
        tuple[int, int]]:  # list[tuple[int,int]] - 1 baza prostokatna )bit, 2 - bit z Hadamarda
        """
        Anounces pair of possible states of the Photon
        :return:
        """
        return self.possibleStates

    def getUsedStates(self, states: list[int]) -> None:
        for i in states:
            self.keyBits.append(self.possibleStates[i][self.sendBases[i]])

        logger.log(f'Alice got {len(self.keyBits)} bits of key')

    def getSampleIds(self, sampleIds: list[int]) -> None:
        """
        Gets IDs of bits which are to used as samples (for QBER)
        :param sampleIds: IDs of bits (no need for order)
        """
        self.sampleIds = sampleIds
        logger.log(f"Alice recieved Bob's indexes of sample bits: {sampleIds}")

    def sendSample(self) -> list[int]:
        """
        Sends sample to Bob (based on recieved IDs)
        :return: List of Alice's sample bits (in order of IDs in its respective list)
        """
        for i in self.sampleIds:
            self.aliceSample.append(self.keyBits[i])
        logger.log(f"Alice sent sample")
        return self.aliceSample

    def recieveSamples(self, sample: list[int]) -> None:
        """
        Gets sample bits from Bob
        :param sample: List of Bob's sample bits (in order of IDs in its respective list)
        """
        self.bobSample = sample
        logger.log(f"Alice is recieving samples from Bob: {sample}")

    def calculateQBER(self) -> None:
        """
        Calculates QBER based on her and Bob's sample
        """
        difference: int = 0

        for (a, b) in zip(self.aliceSample, self.bobSample):
            difference += a ^ b

        try:
            self.qber: float = difference / len(self.aliceSample)
        except ZeroDivisionError:
            logger.error(f"ZeroDivisionError")

        logger.log(f"Alice is calculating QBER: {self.qber}")


    def prepareForErrorCorrection(self):
        sievedBits = list(self.keyBits)

        for i in range(len(sievedBits)):
            if i not in self.sampleIds:
                self.keyBits.append(sievedBits[i])

        kb_pad: int = 0 if len(self.keyBits) % 8 == 0 else 8 - len(self.keyBits) % 8
        self.keyBits += [0] * kb_pad

        self.max_length = len(self.keyBits) // 2
        self.start_length = ceil (1 / (self.qber + 1 / len(self.keyBits)))

    def permute(self) -> list[int]:
        """Alicja generuje permutacje"""
        self.permutation: list[int] = list(range(len(self.keyBits)))
        shuffle(self.permutation)

        self.keyBits = [self.keyBits[i] for i in self.permutation]

        return self.permutation

    def split_into_blocks(self) -> None:
        """Alicja dzieli bity na bloki"""
        n: int = min(self.max_length, self.start_length * 2 ** self.i)
        self.n = n
        self.i += 1

        self.blocks = [self.keyBits[i: min(i + n, len(self.keyBits))] for i in range(0, len(self.keyBits), n)]

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
                      [self.keyBits[i: min(len(self.keyBits), i + 4)] for i in
                       range(0, len(self.keyBits), 4)]]]))).digest()

    def unpermute(self):
        bits: list[int] = [0 for _ in self.keyBits]

        for (new, old) in enumerate(self.permutation):
            bits[old] = self.keyBits[new]

        self.keyBits = bits

    def send_random_bytes(self) -> bytes:
        self.random_bytes = randbytes(self.bytes_count)

        return self.random_bytes

    def get_final_key(self) -> None:
        self.keyBits += [0] * (8 - len(self.keyBits) % 8)
        quads : list[list[int]] = [self.keyBits[i : i + 4] for i in range(0, len(self.keyBits), 4)]
        quad_vals : list[int] = [sum([2**(3 - i) * b for (i, b) in enumerate(q)]) for q in quads]
        quad_hex : list[str] = [hex(q)[2:] for q in quad_vals]
        hex_bytes : str = ''.join(quad_hex)
        b : bytes = bytes.fromhex(hex_bytes) + self.random_bytes
        self.key = sha256(b).digest()
