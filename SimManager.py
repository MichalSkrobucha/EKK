from Alice import Alice
from Bob import Bob
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

    channel: Channel
    alice: Alice
    bob: Bob

    def __init__(self):
        self.channel = Channel(0.1)
        self.alice = Alice(self.channel, 0.5)
        self.bob = Bob(self.channel, 0.99, 0.01)
        logger.set_time(self.sim_start)

    def simLoop(self):
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
