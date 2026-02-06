# Common/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    qber_threshold: float = 25  # %
    key_length: int = 1024


@dataclass(frozen=True)
class ChannelConfig:
    length_km: float = 20.0
    dumpening_per_km: float = 0.2
    base_transform_per_km: float = 0.2


@dataclass(frozen=True)
class BB84Config:
    alice_mi: float = 0.1
    bob_efficiency: float = 90.0
    bob_error: float = 10.0
    eve_present: bool = False


@dataclass(frozen=True)
class E91Config:
    n_photons: int = 1000
    bases_dict = {0: 0.0, 1: 22.5, 2: 45.0, 3: 67.5}
    alice_bases = {0: 0.0, 1: 22.5, 2: 45.0}
    bob_bases = {1: 22.5, 2: 45.0, 3: 67.5}
    eve_bases = {1: 22.5, 2: 45.0}


@dataclass(frozen=True)
class AppConfig:
    sim: SimulationConfig = SimulationConfig()
    channel: ChannelConfig = ChannelConfig()
    bb84: BB84Config = BB84Config()
    e91: E91Config = E91Config()


cfg = AppConfig()
