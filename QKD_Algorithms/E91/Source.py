from Photon import Photon
from QKD_Algorithms.Logger import SimLogger

logger = SimLogger()


class Source:
    def generate_pair(self):
        photon_1 = Photon()
        photon_2 = Photon()
        photon_1.set_entangled_pair(photon_2)
        logger.log("Source generated pair of entangled photons")
        return photon_1, photon_2
