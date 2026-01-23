from QKD_Algorithms.Logger import SimLogger
import PhotonE91 as Photon


class ChannelE91:
    container: list[Photon]
    name: str = ""

    def __init__(self, logger: SimLogger, name: str = "channel"):
        self.logger = logger
        self.name = name
        self.container = []

    def send(self, photons: list[Photon]) -> None:
        """
        Adds list of photons (impulse) to channel (where they are (optionally) dumpened and their basis are transformed)
        :param photons: Alice's photon impulse
        """
        self.container.extend(photons)
        self.logger.log(f"Channel {self.name} received {len(self.container)} photons")

    def read(self) -> list[Photon]:
        """
        Return list of photons
        """
        # Płytka kopia listy (list slicing) - przekazuje te same obiekty fotonów
        read_container = self.container[:]
        self.container.clear()
        self.logger.log(f"Channel {self.name} output: {len(read_container)} photons have been read")
        return read_container
