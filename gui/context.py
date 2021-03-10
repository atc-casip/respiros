from dataclasses import dataclass
from typing import List

from common.alarms import Alarm


@dataclass
class Context:
    """System data shown in the GUI.

    Most of the initial values are taken from a config file.
    """

    locked: bool

    ipap: int
    epap: int
    freq: int
    trigger: int
    inhale: int
    exhale: int

    mode: str

    pressure_min: int
    pressure_max: int
    volume_min: int
    volume_max: int
    oxygen_min: int
    oxygen_max: int
    freq_max: int

    alarms: List[Alarm]

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.locked = False

        self.ipap = app.config["IPAP_DEFAULT"]
        self.epap = app.config["EPAP_DEFAULT"]
        self.freq = app.config["FREQ_DEFAULT"]
        self.trigger = app.config["TRIGGER_DEFAULT"]
        self.inhale = app.config["INHALE_DEFAULT"]
        self.exhale = app.config["EXHALE_DEFAULT"]

        self.mode = "vcp"

        self.pressure_min = app.config["ALARM_PRESSURE_MIN"]
        self.pressure_max = app.config["ALARM_PRESSURE_MAX"]
        self.volume_min = app.config["ALARM_VOLUME_MIN"]
        self.volume_max = app.config["ALARM_VOLUME_MAX"]
        self.oxygen_min = app.config["ALARM_OXYGEN_MIN"]
        self.oxygen_max = app.config["ALARM_OXYGEN_MAX"]
        self.freq_max = app.config["ALARM_FREQ_MAX"]

        self.alarms = []

        app.ctx = self


ctx = Context()
