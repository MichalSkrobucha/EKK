import sys

from Channel import Channel
from Logger import SimLogger
from Photon import Photon
from random import randint, binomialvariate, shuffle
import Logger

logger = SimLogger()


class Bob:
    channel: Channel

    def __init__(self, channel: Channel, efficiency: float, error: float) -> None:
        """
        efficinecy - kilka jak przyjdzie
        error - klika jak nie przyjdzie
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

    def receive(self):
        impulse: list[Photon] = self.channel.read()
        logger.log(f"Bob read {len(impulse)} photons from channel")

        # pomiary
        measurments: list[list[int]] = [[0, 0], [0,0]] # [base][bit], wartosć = liczba kliknięć detektora

        for p in impulse:
            base: int = randint(0, 1)
            bit: int = p.measure(base)

            # czy dobry detektor kliknie
            measurments[base][bit] += binomialvariate(p=self.efficiency)

        # error (fałszywe kliknięcia) - może kliknąć tylko jak nie kliknęło poprawnie na dobry foton
        # może się zdarzyć, że na detektor przyszedł foton, nie kliknęło (pech na efficinecy), ale klikęło na error
        for (base, bit) in [(0,0), (0,1), (1,0), (1,1)]:
            if measurments[base][bit] == 0:
                measurments[base][bit] += binomialvariate(p=self.error)

        logger.log(f"Bob measured: \n"
                   f"\t\t\t{measurments[0][0]} clicks in base 0 (computational) of value 0 (horizontal)\n"
                   f"\t\t\t{measurments[0][1]} clicks in base 0 (computational) of value 1 (vertical)\n"
                   f"\t\t\t{measurments[1][0]} clicks in base 1 (Hadamard) of value 0 (diagonal 45)\n"
                   f"\t\t\t{measurments[1][1]} clicks in base 1 (Hadamard) of value 1 (diagonal -45)")
        # Bob czyta wyniki (liczbę kliknięć) detektorów i je interpretuje

        clickCount: int = measurments[0][0] + measurments[0][1] + measurments[1][0] + measurments[1][1]
        logger.log(f"Bob measured {clickCount} clicks")

        if clickCount == 0:
            self.bases.append(-1) # BASE = -1 - niejasny odczyt (nie można jednoznacznie(z dostatecznie dużą pewnością?) określić wyniku pomiaru)
            self.bits.append(-1) # żeby nie zepsuć indeksów
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
            # kilka kliknięć w tej samej bazie
            clicksInBase0: int = measurments[0][0] + measurments[0][1]
            clicksInBase1: int = measurments[1][0] + measurments[1][1]

            base: int = -1

            # kilka kliknięć w jednej z baz (druga 0)
            if clicksInBase1 == 0:
                base = 0
            elif clicksInBase0 == 0:
                base = 1

            # powyższy warunek spełniony (klikało tylko w jednej z baz)
            if base >= 0:
                # na tym samym bicie
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

                # na różnych bitach
                self.bases.append(-1)
                self.bits.append(-1)
                logger.log(f"Bob's measure is unclear")
                return

            # kliknięcia na obu bazach
            # w których bazach są kliknięcia tylko na jednym detektorze (na drugim clickCount to 0) (bazy czyste)
            is0Clean: bool = (measurments[0][0] * measurments[0][1] == 0)
            is1Clean: bool = (measurments[1][0] * measurments[1][1] == 0)

            bit: int

            if is0Clean and is1Clean:
                # obie bazy są czyste

                # która ma więcej kliknięć (jest bardziej wiarygodna)
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
                # tylko 0 jest czysta
                base = 0
                if measurments[0][0] > 0:
                    bit = 0
                else:
                    bit = 1
                self.bases.append(base)
                self.bits.append(bit)
                logger.log(f"Bob's base is {base} and bit is {bit}")
            elif is1Clean:
                # tylko 1 jest czysta
                base = 1
                if measurments[1][0] > 0:
                    bit = 0
                else:
                    bit = 1
                self.bases.append(base)
                self.bits.append(bit)
                logger.log(f"Bob's base is {base} and bit is {bit}")
            else:
                # żadna nie jest czysta (każdy z 4 detektorów kliknął)
                self.bases.append(-1)
                self.bits.append(-1)
                logger.log(f"Bob's measure is unclear")
                return

    def sendBases(self) -> list[int]:
        logger.log("Bob sent his bases to Alice")
        return self.bases

    def receiveBases(self, bases: list[int]) -> None:
        self.aliceBases = bases
        logger.log(f"Bob is recieving bases from Alice {bases}")

    def sieveBits(self) -> None:
        i: int = 0

        for (a, b, bit) in zip(self.aliceBases, self.bases, self.bits):
            if a == b:
                self.sievedBits.append(bit)

        logger.log(f"Bob sieved his measurments (based on his and Alice's bases) and got {len(self.sievedBits)} bits: {self.sievedBits}")

    def sendSampleIds(self) -> list[int]:
        l: int = len(self.sievedBits)
        ids: list[int] = list(range(l))
        shuffle(ids)

        self.sampleIds = ids[:int(self.sample_bits * l)]

        logger.log("Bob is sending to Alice indexes of sample bits")

        return self.sampleIds

    def sendSample(self) -> list[int]:
        for i in self.sampleIds:
            self.bobSample.append(self.sievedBits[i])

        logger.log("Bob is sending his samples to Alice")

        return self.bobSample

    def receiveSamples(self, sample: list[int]) -> None:
        self.aliceSample = sample
        logger.log(f"Bob is recieving samples from Alice {sample}")

    def calculateQBER(self) -> None:
        difference: int = 0

        for (a, b) in zip(self.aliceSample, self.bobSample):
            difference += a^b

        self.qber: float = difference / len(self.aliceSample)

        logger.log(f"Bob is calculating QBER: {self.qber}")

