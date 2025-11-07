from numpy.random import poisson
import numpy as np
from random import randint
from Channel import Channel
from Logger import SimLogger
from Photon import Photon
from random import shuffle

logger = SimLogger()


class Alice:
    """
    :param:rozkład wysyałania
    """
    mi: float
    channel: Channel
    message: list[Photon]

    def __init__(self, channel: Channel, mi: float):
        self.channel = channel
        self.mi = mi

        self.message: list[Photon] = []

        self.bases: list[int] = []
        self.bobBases: list[int] = []
        self.bits: list[int] = []
        self.sievedBits: list[int] = []
        self.aliceSample: list[int] = []
        self.bobSample: list[int] = []
        self.sampleIds: list[int] = []
        self.qber: float = 0.0

    def _generate_key(self) -> list[Photon]:
        n_photons: int = poisson(self.mi)
        photons_list = []

        base: int = randint(0, 1)
        bit: int = randint(0, 1)
        self.bits.append(bit)
        self.bases.append(base)

        for _ in range(n_photons):
            photons_list.append(Photon(base, bit))
            logger.log(f">>> Photon: {base}, {bit}")

        self.message.extend(photons_list)
        logger.log(f"Alice generated {n_photons} photons")
        return photons_list

    def send_key(self) -> None:
        logger.log("Alice sent key to the channel")
        self.channel.send(self._generate_key())

    def sendBases(self) -> list[int]:
        logger.log("Alice sent bases")
        return self.bases

    def receiveBases(self, bases: list[int]) -> None:
        self.bobBases = bases
        logger.log(f"Alice received bases from Bob: {bases}")

    def sieveBits(self) -> None:
        for (a, b, bit) in zip(self.bases, self.bobBases, self.bits):
            if a == b:
                self.sievedBits.append(bit)

        logger.log(f"Alice sieved her measurments (based on her and Bob's bases) and got {len(self.sievedBits)} bits: {self.sievedBits}")

    def getSampleIds(self, sampleIds: list[int]) -> None:
        self.sampleIds = sampleIds
        logger.log(f"Alice recieved Bob's indexes of sample bits: {sampleIds}")

    def sendSample(self) -> list[int]:
        for i in self.sampleIds:
            self.aliceSample.append(self.sievedBits[i])
        logger.log(f"Alice sent sample")
        return self.aliceSample

    def recieveSamples(self, sample: list[int]) -> None:
        self.bobSample = sample
        logger.log(f"Alice is recieving samples from Bob: {sample}")

    def calculateQBER(self) -> None:
        difference: int = 0

        for (a, b) in zip(self.aliceSample, self.bobSample):
            difference += a^b

        self.qber: float = difference / len(self.aliceSample)

        logger.log(f"Alice is calculating QBER: {self.qber}")
