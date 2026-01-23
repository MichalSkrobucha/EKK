from dependency_injector import containers, providers
from Logger import SimLogger




class BB84Container(containers.DeclarativeContainer):
    photon_factory = providers.Object(PhotonSARG)
    alice = providers.Singleton(

    )
    bob = providers.Singleton()
    channel = providers.Singleton()
    photon = providers.Singleton()
    eve = providers.Singleton()
    logger = providers.Singleton(SimLogger)
