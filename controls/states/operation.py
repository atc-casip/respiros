"""
Main operation modes.
"""

import logging
import time
from typing import Dict

import numpy as np
import zmq
from controls.context import Context

from .events import Event, StartOperationAssisted, StartOperationControlled
from .state import State

GAUGE_PRESSION_DIFF = 0.01  # s
OXYGEN_PRESSION_DIFF = 1  # s
DHT_DIFF = 10  # s
MEAN_FREQ_LENGTH = 3
MEAN_IEPAP_LENGTH = 1
MEAN_GAUGE_LENGTH = 3
MEAN_AIRFLOW_LENGTH = 6


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

        self.ipap_old = 0.0

        self.ipap_read = 0.0
        self.epap_read = 0.0
        self.insp_duration = 0.0
        self.esp_duration = 0.0
        self.freq_read = 0.0
        self.freq_mean = 0.0
        self.vc_in = 0.0
        self.vc_out = 0.0

        self.time_old = time.time()
        self.oxygen_time_saved = 0
        self.dht_time_saved = 0

        self.volume = 0.0
        self.gauge_pressure = 0.0
        self.airflow_pressure = 0.0
        self.airflow_pressure_old = 0.0
        self.volume_filtered = 0.0
        self.gauge_pressure_filtered = 0.0
        self.airflow_pressure_filtered = 0.0
        self.airflow_pressure_old_filtered = 0.0

        self.oxygen_percentage = None
        self.atm_pressure = None
        self.temperature_box = None
        self.humidity_box = None
        self.temperature_air = None

        self.ipap_angle = 0.0

    def transitions(self) -> Dict[Event, State]:
        return {StartOperationAssisted: OperationAssisted}

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
                            "pressure": self.gauge_pressure_filtered,
                            "airflow": self.airflow_pressure_filtered,
                            "volume": self.volume,
                            "timestamp": self.time_old,
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
            insp_duration = (
                cycle_duration / (self.inhale + self.exhale) * self.inhale
            )
            exp_duration = (
                cycle_duration / (self.exhale + self.inhale) * self.exhale
            )

            if (
                not insp_exp and time.time() >= time_saved + insp_duration
            ) or (insp_exp and time.time() >= time_saved + exp_duration):
                insp_exp = not insp_exp
                if insp_exp:
                    self.insp_duration = time.time() - time_saved
                    self.ipap_read = self.gauge_pressure
                else:
                    self.esp_duration = time.time() - time_saved
                    self.epap_read = self.gauge_pressure
                    self.volume = 0
                    self.__calculate_angle()

                time_saved = time.time()

                self.freq_mean = (
                    (MEAN_FREQ_LENGTH - 1) / MEAN_FREQ_LENGTH
                ) * self.freq_mean + (1 / MEAN_FREQ_LENGTH) * 60 / (
                    self.insp_duration + self.esp_duration
                )
                self.freq_read = 60 / (self.insp_duration + self.esp_duration)

                self.ctx.messenger.send(
                    "cycle",
                    {
                        "ipap": self.ipap_read,
                        "epap": self.epap_read,
                        "freq": self.freq_mean,
                        "vc_in": self.vc_in,
                        "vc_out": self.vc_out,
                        "oxygen": self.oxygen_percentage,
                    },
                )

            if insp_exp:  # Exhaling
                self.epap_read = (
                    (MEAN_IEPAP_LENGTH - 1) / MEAN_IEPAP_LENGTH
                ) * self.epap_read + (
                    1 / MEAN_IEPAP_LENGTH
                ) * self.gauge_pressure
                self.ctx.servo.set_angle(0)
            else:  # Inhaling
                self.ipap_read = (
                    (MEAN_IEPAP_LENGTH - 1) / MEAN_IEPAP_LENGTH
                ) * self.ipap_read + (
                    1 / MEAN_IEPAP_LENGTH
                ) * self.gauge_pressure
                self.ctx.servo.set_angle(self.ipap_angle)

            self.__read_sensors()

            time.sleep(0.0001)

    def __calculate_angle(self):
        """Get servo angle based on IPAP."""

        if self.ipap != self.ipap_old:
            self.ipap_angle = 20.009 * np.log(float(self.ipap)) + 37.997
            self.ipap = self.ipap_old
        else:
            difference = float(self.ipap - self.ipap_read)
            self.ipap_angle = self.ipap_angle + 0.5 * difference

    def __read_sensors(self):
        """Fetch readings from all the sensors."""

        time_now = time.time()

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

            # Filtering
            self.gauge_pressure_filtered = (
                (MEAN_GAUGE_LENGTH - 1) / MEAN_GAUGE_LENGTH
            ) * self.gauge_pressure_filtered + (
                1 / MEAN_GAUGE_LENGTH
            ) * self.gauge_pressure
            self.airflow_pressure_filtered = (
                (MEAN_AIRFLOW_LENGTH - 1) / MEAN_AIRFLOW_LENGTH
            ) * self.airflow_pressure_filtered + (
                1 / MEAN_AIRFLOW_LENGTH
            ) * self.airflow_pressure
            self.volume_filtered = (
                (MEAN_GAUGE_LENGTH - 1) / MEAN_GAUGE_LENGTH
            ) * self.volume_filtered + (1 / MEAN_GAUGE_LENGTH) * self.volume

        if time_now >= self.oxygen_time_saved + OXYGEN_PRESSION_DIFF:
            self.oxygen_percentage = self.ctx.oxygen_sensor.read()

            self.oxygen_time_saved = time_now

        if time_now >= self.dht_time_saved + DHT_DIFF:
            self.atm_pressure = self.ctx.atm_ps.read()
            self.temperature_box = self.ctx.dht_box.temperature()
            self.humidity_box = self.ctx.dht_box.humidity()
            self.temperature_air = self.ctx.dht_air.temperature()

            self.dht_time_saved = time_now


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
