from numpy.random import poisson
from random import randint
from QKD_Algorithms.Logger import SimLogger


class Alice:
    """

    """
    mi: float
    message: list

    def __init__(self, mi: float, channel, photon_factory, logger):
        """
        :param channel: Channel on which Alice and Bob are communicating
        :param mi: Average amount of photons in impulse
        """
        self.mi: float = mi
        self.channel = channel
        self.photon_factory = photon_factory
        self.logger = logger

        self.message: list = []
        self.bases: list[int] = []
        self.bobBases: list[int] = []
        self.bits: list[int] = []
        self.sievedBits: list[int] = []

        self.aliceSample: list[int] = []
        self.bobSample: list[int] = []
        self.sampleIds: list[int] = []

        self.qber: float = 0.0

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.message.clear()
        self.bases.clear()
        self.bobBases.clear()
        self.bits.clear()
        self.sievedBits.clear()
        self.aliceSample.clear()
        self.bobSample.clear()
        self.sampleIds.clear()

    def _generate_key(self) -> list:
        """
        Generates next bit of key, and returns impulse of photons
        :return: impulse of photons
        """
        n_photons: int = poisson(self.mi)
        photons_list = []

        base: int = randint(0, 1)
        bit: int = randint(0, 1)
        self.bits.append(bit)
        self.bases.append(base)

        for _ in range(n_photons):
            photons_list.append(self.photon_factory(base, bit))
            self.logger.log(f">>> Photon: {base}, {bit}")

        self.message.extend(photons_list)
        self.logger.log(f"Alice generated {n_photons} photons")
        return photons_list

    def send_key(self) -> None:
        """
        Sends impulse of photons (carrying bit of a key) to the channel
        """
        self.logger.log("Alice sent key to the channel")
        self.channel.send(self._generate_key())

    def getSampleIds(self, sampleIds: list[int]) -> None:
        """
        Gets IDs of bits which are to used as samples (for QBER)
        :param sampleIds: IDs of bits (no need for order)
        """
        self.sampleIds = sampleIds
        self.logger.log(f"Alice recieved Bob's indexes of sample bits: {sampleIds}")

    def sendSample(self) -> list[int]:
        """
        Sends sample to Bob (based on recieved IDs)
        :return: List of Alice's sample bits (in order of IDs in its respective list)
        """
        for i in self.sampleIds:
            self.aliceSample.append(self.sievedBits[i])
        self.logger.log(f"Alice sent sample")
        return self.aliceSample

    def recieveSamples(self, sample: list[int]) -> None:
        """
        Gets sample bits from Bob
        :param sample: List of Bob's sample bits (in order of IDs in its respective list)
        """
        self.bobSample = sample
        self.logger.log(f"Alice is recieving samples from Bob: {sample}")

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
            self.logger.error(f"ZeroDivisionError")

        self.logger.log(f"Alice is calculating QBER: {self.qber}")
