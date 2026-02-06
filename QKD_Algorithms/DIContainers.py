from dependency_injector import containers, providers

import E91.PhotonE91
from Logger import SimLogger
# --- Common Dependencies ---
from Common.Photon import Photon
from Common.Channel import Channel

# --- BB84 Dependencies ---
from BB84.AliceBB84 import AliceBB84
from BB84.BobBB84 import BobBB84
from BB84.EveBB84 import EveBB84

# --- SARG04 Dependencies ---
from SARG04.AliceSARG import AliceSARG
from SARG04.BobSARG import BobSARG
from SARG04.EveSARG import EveSARG

# --- Ekert91 Dependencies ---
from E91.PhotonE91 import PhotonE91
from E91.ChannelE91 import ChannelE91
from E91.AliceE91 import AliceE91
from E91.BobE91 import BobE91
from E91.EveE91 import EveE91
from E91.Source import Source


class BB84Container(containers.DeclarativeContainer):
    logger = providers.Singleton(SimLogger)
    photon_factory = providers.Object(Photon)
    channel = providers.Singleton(Channel, logger=logger)

    alice = providers.Singleton(
        AliceBB84,
        channel=channel,
        photon_factory=photon_factory,
        logger=logger
    )
    bob = providers.Singleton(
        BobBB84,
        channel=channel,
        logger=logger
    )
    eve = providers.Singleton(
        EveBB84,
        channel=channel,
        logger=logger
    )


class SARGContainer(containers.DeclarativeContainer):
    logger = providers.Singleton(SimLogger)
    photon_factory = providers.Object(Photon)
    channel = providers.Singleton(Channel, logger=logger)

    alice = providers.Singleton(
        AliceSARG,
        channel=channel,
        photon_factory=photon_factory,
        logger=logger
    )
    bob = providers.Singleton(
        BobSARG,
        channel=channel,
        logger=logger
    )
    eve = providers.Singleton(
        EveSARG,
        channel=channel,
        logger=logger
    )


class E91Container(containers.DeclarativeContainer):
    logger = providers.Singleton(SimLogger)
    photon_factory = providers.Object(PhotonE91)
    channel_A = providers.Singleton(ChannelE91, logger=logger)
    channel_B = providers.Singleton(ChannelE91, logger=logger)
    channel_E = providers.Singleton(ChannelE91, logger=logger)
    alice = providers.Singleton(
        AliceE91,
        channel=channel_A,
        logger=logger
    )
    bob = providers.Singleton(
        BobE91,
        channel=channel_B,
        logger=logger
    )
    eve = providers.Singleton(
        EveE91,
        channel=channel_E,
        logger=logger
    )
    source = providers.Singleton(
        Source
        # ,photon_factory=photon_factory
    )
