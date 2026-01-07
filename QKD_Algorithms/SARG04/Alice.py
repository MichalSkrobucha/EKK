from numpy.random import poisson
from random import randint
from .Channel import Channel
from QKD_Algorithms.Logger import SimLogger
from .Photon import Photon

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
