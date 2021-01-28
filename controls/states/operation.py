"""
Main operation modes.
"""

import logging
import time
from typing import Dict

import zmq
from controls.context import Context

from .events import Event, StartOperationAssisted, StartOperationControlled
from .state import State

GAUGE_PRESSION_DIFF = 0.01  # s
OXYGEN_PRESSION_DIFF = 1  # s
DHT_DIFF = 10  # s


class OperationControlled(State):
    """
    Controlled ventilation.
    """

    def __init__(self, ctx: Context, payload: Dict):
        super().__init__(ctx)

        self.ipap = payload["ipap"]
        self.epap = payload["epap"]
        self.freq = payload["freq"]
        self.inhale = payload["inhale"]
        self.exhale = payload["exhale"]
        self.trigger = payload["trigger"]
        self.from_standby = payload["from_standby"]

        self.time_old = time.time()
        self.oxygen_time_saved = 0
        self.dht_time_saved = 0

        self.volume = 0.0
        self.gauge_pressure = None
        self.airflow_pressure = 0
        self.airflow_pressure_old = 0
        self.oxygen_percentage = None
        self.atm_pressure = None
        self.temperature_box = None
        self.humidity_box = None
        self.temperature_air = None

    def transitions(self) -> Dict[Event, State]:
        return {StartOperationAssisted: OperationAssisted}

    def read_and_send_sensors(self, time_now):
        # Read Sensors
        if time_now >= (self.time_old + GAUGE_PRESSION_DIFF):
            self.gauge_pressure = self.ctx.gauge_ps.read()
            self.airflow_pressure_old = self.airflow_pressure
            self.airflow_pressure = self.ctx.airflow_ps.read()
            self.volume += (
                (time_now - self.time_old)
                * (self.airflow_pressure + self.airflow_pressure_old)
                / 2
            )
            self.time_old = time_now

        if time_now >= self.oxygen_time_saved + OXYGEN_PRESSION_DIFF:
            self.oxygen_percentage = self.ctx.oxygen_sensor.read()
            self.oxygen_time_saved = time_now

        if time_now >= self.dht_time_saved + DHT_DIFF:
            self.atm_pressure = self.ctx.atm_ps.read()
            self.temperature_box = self.ctx.dht_box.temperature()
            self.humidity_box = self.ctx.dht_box.humidity()
            self.temperature_air = self.ctx.dht_air.temperature()
            self.dht_time_saved = time_now

    def run(self):
        # Boolean, if insp_exp False: inspiration, if insp_exp True: espiration
        insp_exp = False
        time_saved = time.time()

        if self.from_standby:
            self.ctx.servo.set_angle(0)
            time.sleep(0.5)

        while True:
            # GUI control actions
            try:
                [topic, msg] = self.ctx.messenger.recv(block=False)
                if topic == "request-reading":
                    self.ctx.messenger.send(
                        "reading",
                        {
                            "pressure": self.gauge_pressure,
                            "airflow": self.airflow_pressure,
                            "volume": self.volume,
                        },
                    )
                if topic == "operation":
                    logging.info("Received new operation parameters")

                    self.ipap = msg["ipap"]
                    self.epap = msg["epap"]
                    self.freq = msg["freq"]
                    self.inhale = msg["inhale"]
                    self.exhale = msg["exhale"]
                if topic == "change-alarms":
                    logging.info("Received new alarm ranges")
                    # TODO: Change alarm ranges
                    pass
            except zmq.Again:
                # No message available at the moment of checking
                pass

            cycle_duration = 60 / self.freq  # ms
            insp_duration = cycle_duration / (self.inhale + self.exhale) * self.inhale
            exp_duration = cycle_duration / (self.exhale + self.inhale) * self.exhale

            if (not insp_exp and time.time() >= time_saved + insp_duration) or (
                insp_exp and time.time() >= time_saved + exp_duration
            ):
                insp_exp = not insp_exp
                time_saved = time.time()

            if insp_exp:  # Exhaling
                self.ctx.servo.set_angle(0)
            else:  # Inhaling
                self.ctx.servo.set_angle(180)

            self.read_and_send_sensors(time.time())

            time.sleep(0.0001)


class OperationAssisted(State):
    """
    Assisted ventilation.
    """

    def __init__(self, ctx: Context, payload: Dict):
        super().__init__(ctx)

        self.ipap = payload["ipap"]
        self.epap = payload["epap"]
        self.freq = payload["freq"]

    def transitions(self) -> Dict[Event, State]:
        return {StartOperationControlled: OperationControlled}

    def run(self) -> Event:
        # TODO: Implement assisted mode

        pass
