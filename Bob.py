from Channel import Channel
from Logger import SimLogger
from Photon import Photon
from random import randint, binomialvariate, shuffle

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
        self.bases: list[int] = []
        self.bits: list[int] = []
        self.aliceBases: list[int] = []
        self.sievedBits: list[int] = []
        self.sampleIds: list[int] = []
        self.aliceSample: list[int] = []
        self.bobSample: list[int] = []
        self.qber: float = 0.0
        self.sample_bits = 0.25

    def clearLists(self) -> None:
        """
        Empties all lists
        """
        self.bases.clear()
        self.bits.clear()
        self.aliceBases.clear()
        self.sievedBits.clear()
        self.sampleIds.clear()
        self.aliceSample.clear()
        self.bobSample.clear()

    def receive(self):
        """
        Gets impulse of photons from channel and measures it
        """
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
                return

    def sendBases(self) -> list[int]:
        """
        Returns bases in which he measured bits of key
        :return: List of bases (in chronological order)
        """
        logger.log("Bob sent his bases to Alice")
        return self.bases

    def receiveBases(self, bases: list[int]) -> None:
        """
        Get's Alice's bases in which she send bits of key
        :param bases: Alice's bases (in chronological order)
        """
        self.aliceBases = bases
        logger.log(f"Bob is recieving bases from Alice {bases}")

    def sieveBits(self) -> None:
        """
        Sieves key bits based on his and Alice's bases
        """
        i: int = 0

        for (a, b, bit) in zip(self.aliceBases, self.bases, self.bits):
            if a == b:
                self.sievedBits.append(bit)

        logger.log(
            f"Bob sieved his measurments (based on his and Alice's bases) and got {len(self.sievedBits)} bits: {self.sievedBits}")

    def sendSampleIds(self) -> list[int]:
        """
        Sends IDs of bits which are to used as samples (for QBER)
        :return sampleIds: IDs of bits (no need for order)
        """
        l: int = len(self.sievedBits)
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
            self.bobSample.append(self.sievedBits[i])

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

        self.qber: float = difference / len(self.aliceSample)

        logger.log(f"Bob is calculating QBER: {self.qber}")
