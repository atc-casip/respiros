import datetime

from .config import cfg


class Alarm:
    """Model for system alarms."""

    def __init__(self, type: str, criticality: str, timestamp: float):
        self.type = type
        self.criticality = criticality
        self.timestamp = datetime.datetime.fromtimestamp(timestamp)


class Context:
    """System data shown in the GUI.

    Most of the initial values are taken from a config file.
    """

    def __init__(self):
        # Operational parameters
        self.ipap = cfg["params"]["ipap"]["default"]
        self.epap = cfg["params"]["epap"]["default"]
        self.freq = cfg["params"]["freq"]["default"]
        self.trigger = cfg["params"]["trigger"]["default"]
        self.inhale = cfg["params"]["inhale"]["default"]
        self.exhale = cfg["params"]["exhale"]["default"]

        # Plotting data
        self.pressure_data = []
        self.airflow_data = []
        self.volume_data = []

        # Alarm limits
        self.pressure_min = cfg["alarms"]["pressure"]["min"]
        self.pressure_max = cfg["alarms"]["pressure"]["max"]
        self.volume_min = cfg["alarms"]["volume"]["min"]
        self.volume_max = cfg["alarms"]["volume"]["max"]
        self.oxygen_min = cfg["alarms"]["oxygen"]["min"]
        self.oxygen_max = cfg["alarms"]["oxygen"]["max"]
        self.freq_max = cfg["alarms"]["freq"]["max"]

        # Alarms
        self.alarms = []


ctx = Context()
