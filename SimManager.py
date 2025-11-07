from Alice import Alice
from Bob import Bob
from Eve import Eve
from Channel import Channel
from Logger import SimLogger

logger = SimLogger()


class SimManager:
    """
    """
    sim_start: int = 0
    sim_step: int = 1
    sim_end: int = 1000
    qberThreshhold: float = 0.2
    ifEve: bool = True

    channel_length : float = 1.0 #km
    dumpening_per_km : float = 0.2 # dB/ km
    base_transform_per_km : float = 0.2 # db / km

    dumpening_dB : float = dumpening_per_km * channel_length
    base_transform_dB : float = base_transform_per_km * channel_length

    dumpening: float = 1 - 10 ** (-dumpening_dB / 10.0)
    base_transform : float = 1 - 10 ** (-base_transform_dB / 10.0)

    channel: Channel
    alice: Alice
    bob: Bob
    eve: Eve

    def __init__(self):
        self.channel = Channel(self.dumpening, self.base_transform)
        self.alice = Alice(self.channel, 0.5)
        self.bob = Bob(self.channel, 0.99, 0.01)
        logger.set_time(self.sim_start)

    def simLoop(self):
        logger.log(f'\nSimulating channel of length {self.channel_length} km\n'
                   f'with dumpening rate {self.dumpening_per_km} dB/km and base_transform rate {self.base_transform_per_km} dB/km\n'
                   f'Total rates are {self.dumpening_dB} dB of dumpening and {self.base_transform_per_km} dB of base_transform\n'
                   f'Probability of events (per photon) are {self.dumpening} for dumpening and {self.base_transform_per_km} for base_transform')



        for step in range(self.sim_start, self.sim_end, self.sim_step):
            # alicja wysła do boba impulsy fotonów (bity)
            print(f"=====================")
            logger.set_time(step)

            self.alice.send_key()
            self.bob.receive()

        # wymiana baz
        self.bob.receiveBases(self.alice.sendBases())
        self.alice.receiveBases((self.bob.sendBases()))

        # przesiewanie
        self.bob.sieveBits()
        self.alice.sieveBits()

        # bob ustala któe bity są próbkowane
        self.alice.getSampleIds(self.bob.sendSampleIds())
        # wymiana próbki
        self.alice.recieveSamples(self.bob.sendSample())
        self.bob.receiveSamples(self.alice.sendSample())
        # obliczanie błędu
        self.alice.calculateQBER()
        self.bob.calculateQBER()

        if self.bob.qber > self.qberThreshhold:
            logger.log("QBER exceeded threshhold. Ending transmission")
            return

        # błąd w akceptowalnych granicach
        # tu dodamy korektę błędów

    def printTable(self):
        bitsA = [p.bit for p in self.alice.message]
        print(f"Alice | {bitsA}")
        