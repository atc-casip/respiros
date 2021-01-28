"""
System context.
"""

from typing import List

from .config import cfg


class Context:
    """Necessary context for system operation."""

    # Operational parameters
    ipap: int
    epap: int
    freq: int
    trigger: int
    inhale: int
    exhale: int

    # Plotting data
    pressure_data: List[float]
    airflow_data: List[float]
    volume_data: List[float]

    # Alarm limits
    pressure_min: int
    pressure_max: int
    volume_min: int
    volume_max: int
    oxygen_min: int
    oxygen_max: int
    freq_max: int

    def __init__(self):
        self.ipap = cfg["params"]["ipap"]["default"]
        self.epap = cfg["params"]["epap"]["default"]
        self.freq = cfg["params"]["freq"]["default"]
        self.trigger = cfg["params"]["trigger"]["default"]
        self.inhale = cfg["params"]["inhale"]["default"]
        self.exhale = cfg["params"]["exhale"]["default"]

        self.pressure_data = []
        self.airflow_data = []
        self.volume_data = []

        self.pressure_min = cfg["alarms"]["pressure"]["min"]
        self.pressure_max = cfg["alarms"]["pressure"]["max"]
        self.volume_min = cfg["alarms"]["volume"]["min"]
        self.volume_max = cfg["alarms"]["volume"]["max"]
        self.oxygen_min = cfg["alarms"]["oxygen"]["min"]
        self.oxygen_max = cfg["alarms"]["oxygen"]["max"]
        self.freq_max = cfg["alarms"]["freq"]["max"]
