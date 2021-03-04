from datetime import datetime
from enum import Enum, auto

PRESSURE_MIN = "pressure-min"
PRESSURE_MAX = "pressure-max"
VOLUME_MIN = "volume-min"
VOLUME_MAX = "volume-max"
OXYGEN_MIN = "oxygen-min"
OXYGEN_MAX = "oxygen-max"
FREQ_MAX = "freq-max"
APNEA = "apnea"
DISCONNECTION = "disconnection"


class Type(Enum):
    PRESSURE_MIN = auto()
    PRESSURE_MAX = auto()
    VOLUME_MIN = auto()
    VOLUME_MAX = auto()
    OXYGEN_MIN = auto()
    OXYGEN_MAX = auto()
    FREQ_MAX = auto()
    APNEA = auto()
    DISCONNECTION = auto()


class Criticality(Enum):
    NONE = auto()
    MEDIUM = auto()
    HIGH = auto()


class Alarm:
    def __init__(
        self,
        type: Type,
        criticality: Criticality,
        timestamp: datetime = datetime.now(),
    ):
        self.type = type
        self.criticality = criticality
        self.timestamp = timestamp
