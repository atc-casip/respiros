"""
Main operation modes.
"""

import logging
import time
from typing import Dict

import common.alarms as alarms
import common.ipc.topics as topics
import numpy as np
import zmq
from controls.config import cfg
from controls.context import Context
from controls.messenger import Messenger

from .events import Event, StartOperationAssisted, StartOperationControlled
from .state import State

GAUGE_PRESSION_DIFF = 0.00001  # s
OXYGEN_PRESSION_DIFF = 1  # s
DHT_DIFF = 2  # s
MEAN_FREQ_LENGTH = 6
MEAN_IEPAP_LENGTH = 3
MEAN_GAUGE_LENGTH = 10
MEAN_AIRFLOW_LENGTH = 20
APNEA_TIME = 10
AIRFLOW_PEAK_COEFFICIENT = 0.2
SERVO_MAX_ANGLE = 115
SERVO_MIN_ANGLE = 50


class OperationControlled(State):
    """
    Controlled ventilation.
    """

    def __init__(self, ctx: Context, payload: Dict):
        super().__init__(ctx)

        # Replace and evaluate their value when changed from GUI
        self.ipap = payload["ipap"]
        self.epap = payload["epap"]
        self.freq = payload["freq"]
        self.inhale = payload["inhale"]
        self.exhale = payload["exhale"]
        self.trigger = payload["trigger"]
        self.from_standby = payload["from_standby"]
        self.insp_duration = 0.0
        self.esp_duration = 0.0
        self.cycle_duration = 0.0
        self.time_saved = 0.0

        # Evaluate when changed from GUI
        self.ipap_old = 0.0
        self.epap_old = 0.0

        # Measured parameters
        self.ipap_read = 0.0
        self.epap_read = 0.0
        self.insp_duration_read = 0.0
        self.esp_duration_read = 0.0
        self.freq_read = 0.0
        self.freq_mean = 0.0
        self.vc_in = 0.0
        self.vc_out = 0.0
        self.volume_minute = 0.0

        # Sensor measurements timestamp
        self.sensors_time_saved = time.time()
        self.oxygen_time_saved = 0
        self.dht_time_saved = 0

        # Sensor current measurements
        self.volume = 0.0
        self.gauge_pressure = 0.0
        self.airflow_pressure = 0.0
        self.airflow_pressure_old = 0.0
        self.oxygen_percentage = 0.0
        self.atm_pressure = 0.0
        self.temperature_box = 0.0
        self.humidity_box = 0.0
        self.temperature_air = 0.0
        self.humidity_air = 0.0

        # Sensor current filtered measurements
        self.volume_filtered = 0.0
        self.gauge_pressure_filtered = 0.0
        self.airflow_pressure_filtered = 0.0

        # IPAP and EPAP current servo angles
        self.ipap_angle = 0.0
        self.epap_angle = 0.0

        # IPAP and EPAP memory servo angles
        self.iepap_table = [0 for _ in range(35)]
        self.iepap_index = [0 for _ in range(35)]

        # Transsition variables between operation modes
        self.operation = False
        self.airflow_trigger = None
        self.airflow_max = None

        # System mode ON or OFF
        self.mode = True

        # Alarms
        self.pressure_min = cfg["alarms"]["pressure"]["min"]
        self.pressure_max = cfg["alarms"]["pressure"]["max"]
        self.volume_min = cfg["alarms"]["volume"]["min"]
        self.volume_max = cfg["alarms"]["volume"]["max"]
        self.oxygen_min = cfg["alarms"]["oxygen"]["min"]
        self.oxygen_max = cfg["alarms"]["oxygen"]["max"]
        self.freq_max = cfg["alarms"]["freq"]["max"]

    def transitions(self) -> Dict[Event, State]:
        return {StartOperationAssisted: OperationAssisted}

    def run(self):
        # Inicializations
        insp_exp = False  # Start in inhalation
        self.time_saved = time.time()  # Get time reference
        self.operation = False  # Start in control operation mode
        self.__get_ie_durations()  # Obtain initial cycle, I and E durations

        while True:
            # GUI control actions: check if any message has been received and
            # update class attributes
            try:
                [topic, msg] = self.ctx.messenger.recv(block=False)
                if topic == topics.REQUEST_READING:
                    self.ctx.messenger.send(
                        topics.READING,
                        {
                            "pressure": self.gauge_pressure_filtered,
                            "airflow": self.airflow_pressure_filtered,
                            "volume": self.volume,
                            "timestamp": self.sensors_time_saved,
                        },
                    )

                if topic == topics.OPERATION_PARAMS:
                    logging.info("Received new operation parameters")

                    self.ipap = msg["ipap"]
                    self.epap = msg["epap"]
                    self.freq = msg["freq"]
                    self.inhale = msg["inhale"]
                    self.exhale = msg["exhale"]
                    self.__get_ie_durations()

                if topic == topics.OPERATION_ALARMS:
                    logging.info("Received new alarm ranges")

                    self.pressure_min = msg["pressure_min"]
                    self.pressure_max = msg["pressure_max"]
                    self.volume_min = msg["volume_min"]
                    self.volume_max = msg["volume_max"]
                    self.oxygen_min = msg["oxygen_min"]
                    self.oxygen_max = msg["oxygen_max"]
                    self.freq_max = msg["freq_max"]

            except zmq.Again:
                # No message available at the moment of checking
                pass

            # IE cycling transition: from Espiration to Inspiration
            # or from Inspiration to Espiration
            # Controlled Mode Operation: I, E transition. Time cycled mode
            # operation
            if not self.operation:
                if (
                    not insp_exp
                    and time.time() >= self.time_saved + self.insp_duration
                ) or (
                    insp_exp
                    and time.time() >= self.time_saved + self.esp_duration
                ):
                    insp_exp = not insp_exp

                    if (
                        insp_exp
                    ):  # Start espiration, save inspiration parameters
                        self.__start_espiration()
                        logging.info("Espiration Controlled")

                    else:  # Start inspiration, save espiration parameters
                        self.__start_inspiration()
                        logging.info("Inspiration Controlled")

            # Assisted Mode Operation: I, E transition. Triggered and airflow
            # mode operation
            else:
                if (
                    insp_exp
                ):  # Espiration. Detect trigger to change to inspiration.
                    if (
                        time.time()
                        > self.time_saved + self.esp_duration * 1.0 / 3.0
                    ):
                        if (
                            not self.airflow_trigger
                            or self.airflow_trigger
                            <= self.airflow_pressure_filtered
                        ):
                            self.airflow_trigger = (
                                self.airflow_pressure_filtered
                            )
                        elif (
                            self.airflow_trigger
                            - self.airflow_pressure_filtered
                            >= self.trigger
                            and self.airflow_pressure_filtered < 0
                        ):
                            # Start inspiration, save espiration parameters
                            insp_exp = not insp_exp
                            self.__start_inspiration()
                            logging.info("Inspiration Assisted")

                else:  # Inspiration. Detect 20 % airflow peak to change to espiration
                    if (
                        not self.airflow_max
                        or self.airflow_max < self.airflow_pressure_filtered
                    ):
                        self.airflow_max = self.airflow_pressure_filtered

                    elif (
                        self.airflow_max * AIRFLOW_PEAK_COEFFICIENT
                        >= self.airflow_pressure_filtered
                        and self.airflow_max > 0
                        and time.time() > self.time_saved + 1 * 1.0 / 3.0
                    ):
                        # Start espiration, save inspiration parameters
                        logging.info("Airflow max: %f", self.airflow_max)
                        logging.info(
                            "Airflow: %f", self.airflow_pressure_filtered
                        )
                        insp_exp = not insp_exp
                        self.__start_espiration()
                        logging.info("Espiration Assisted")

            ## IE cycling execution: Espiration or Inspiration
            if insp_exp:  # Espiration
                self.epap_read = (
                    (MEAN_IEPAP_LENGTH - 1) / MEAN_IEPAP_LENGTH
                ) * self.epap_read + (
                    1 / MEAN_IEPAP_LENGTH
                ) * self.gauge_pressure
                self.ctx.servo.set_angle(self.epap_angle)

                # Check operation mode change
                if (
                    not self.operation
                    and time.time()
                    >= self.time_saved + self.esp_duration * 1.0 / 3.0
                ):
                    if (
                        not self.airflow_trigger
                        or self.airflow_trigger
                        <= self.airflow_pressure_filtered
                    ):
                        self.airflow_trigger = self.airflow_pressure_filtered
                    elif (
                        self.airflow_trigger - self.airflow_pressure_filtered
                        >= self.trigger
                        and self.airflow_pressure_filtered < 0
                    ):
                        logging.info(
                            "Trigger difference %f",
                            self.airflow_trigger
                            - self.airflow_pressure_filtered,
                        )
                        self.operation = True
                        insp_exp = not insp_exp
                        self.__start_inspiration()
                        logging.info("Inspiration Assisted")

                elif (
                    self.operation
                    and time.time() >= self.time_saved + APNEA_TIME
                ):
                    self.operation = False
                    insp_exp = not insp_exp
                    self.__start_inspiration()
                    logging.info("Inspiration Controlled")
                    logging.info("Apnea: %f", time.time() - self.time_saved)

            else:  # Inspiration
                self.ipap_read = (
                    (MEAN_IEPAP_LENGTH - 1) / MEAN_IEPAP_LENGTH
                ) * self.ipap_read + (
                    1 / MEAN_IEPAP_LENGTH
                ) * self.gauge_pressure

                self.ctx.servo.set_angle(self.ipap_angle)

            # Read sensors and check alarms
            self.__read_sensors()
            self.__update_iepap_table()
            # self.__check_alarms(self.ctx.messenger)
            time.sleep(0.00001)

    def __detect_on_off(self):
        if (
            self.ipap_read < 3
            and self.epap_read < 3
            and abs(self.ipap_read - self.epap_read) < 1
        ):
            self.mode = False
        else:
            self.mode = True

        logging.info("Mode ON or OFF: " + str(self.mode))

    def __start_inspiration(self):
        """Save espiration parameters and obtain inspiration parameters."""

        self.esp_duration_read = time.time() - self.time_saved
        self.vc_out = self.vc_in - self.volume_filtered
        self.volume = 0
        self.volume_filtered = 0
        self.airflow_max = None
        self.__calculate_angle_ipap()
        self.__send_cycle()
        self.time_saved = time.time()
        self.__detect_on_off()
        logging.info("E: %f", self.esp_duration_read)

    def __start_espiration(self):
        """Save inspiration parameters and obtain espiration parameters."""

        self.insp_duration_read = time.time() - self.time_saved
        self.vc_in = (
            self.volume_filtered
        )  # * (310.15 /(self.temperature_air+273.15)) * ((self.atm_pressure - )/(self.atm_pressure - ) )
        self.volume_minute = self.vc_in * self.freq_read
        self.airflow_trigger = None
        self.__calculate_angle_epap()
        self.__send_cycle()
        self.time_saved = time.time()
        self.__detect_on_off()
        logging.info("I: %f", self.insp_duration_read)

    def __get_ie_durations(self):
        """Obtain desired cycle, inspiration and espiration durations."""

        self.cycle_duration = 60 / self.freq  # ms
        self.insp_duration = (
            self.cycle_duration / (self.inhale + self.exhale) * self.inhale
        )
        self.esp_duration = (
            self.cycle_duration / (self.exhale + self.inhale) * self.exhale
        )
        logging.info("I: %f", self.insp_duration)
        logging.info("E: %f", self.esp_duration)

    def __send_cycle(self):
        """Obtain respiration frequency and send cycle info."""

        if self.mode == True:
            self.freq_read = 60 / (
                self.insp_duration_read + self.esp_duration_read
            )
        else:
            self.freq_read = 0

        self.freq_mean = (
            (MEAN_FREQ_LENGTH - 1) / MEAN_FREQ_LENGTH
        ) * self.freq_mean + (1 / MEAN_FREQ_LENGTH) * self.freq_read

        self.ctx.messenger.send(
            topics.CYCLE,
            {
                "ipap": self.ipap_read,
                "epap": self.epap_read,
                "freq": self.freq_mean,
                "vc_in": self.vc_in,
                "vc_out": self.vc_out,
                "oxygen": self.oxygen_percentage,
            },
        )

    def __calculate_angle_ipap(self):
        """Get servo angle based on IPAP."""

        if self.ipap != self.ipap_old or not self.mode:
            if not self.iepap_index[int(self.ipap - 1)]:
                self.ipap_angle = 20.009 * np.log(float(self.ipap)) + 37.997
            else:
                self.ipap_angle = self.iepap_table[int(self.ipap - 1)]
            self.ipap_old = self.ipap
        else:
            difference = float(self.ipap - self.ipap_read)
            if difference > 0.5 or difference < -0.5:
                self.ipap_angle = self.ipap_angle + 0.5 * difference

        if self.ipap_angle > SERVO_MAX_ANGLE:
            self.ipap_angle = SERVO_MAX_ANGLE
        elif self.ipap_angle < SERVO_MIN_ANGLE:
            self.ipap_angle = SERVO_MIN_ANGLE
        logging.info("IPAP angle: %f", self.ipap_angle)

    def __calculate_angle_epap(self):
        """Get servo angle based on IPAP."""

        if self.epap != self.epap_old or not self.mode:
            if not self.iepap_index[int(self.epap - 1)]:
                self.epap_angle = 20.009 * np.log(float(self.epap)) + 37.997
            else:
                self.epap_angle = self.iepap_table[int(self.epap - 1)]
            self.epap_old = self.epap
        else:
            difference = float(self.epap - self.epap_read)
            if difference > 0.5 or difference < -0.5:
                difference = float(self.epap - self.epap_read)
                self.epap_angle = self.epap_angle + 0.5 * difference

        if self.epap_angle < SERVO_MIN_ANGLE:
            self.epap_angle = SERVO_MIN_ANGLE
        elif self.epap_angle > SERVO_MAX_ANGLE:
            self.epap_angle = SERVO_MAX_ANGLE

        logging.info("EPAP angle: %f", self.epap_angle)

    def __update_iepap_table(self):
        """Update pressure angle table based."""

        if abs(self.epap - self.epap_read) < 0.3:
            self.iepap_table[int(self.epap - 1)] = self.epap_angle
            self.iepap_index[int(self.epap - 1)] = 1
            # logging.info("I: %s", self.iepap_table)

        if abs(self.ipap - self.ipap_read) < 0.3:
            self.iepap_table[int(self.ipap - 1)] = self.ipap_angle
            self.iepap_index[int(self.ipap - 1)] = 1
            # logging.info("I: %s", self.iepap_table)

    def __read_sensors(self):
        """Fetch readings from all the sensors."""

        time_now = time.time()

        if time_now >= (self.sensors_time_saved + GAUGE_PRESSION_DIFF):
            self.gauge_pressure = self.ctx.gauge_ps.read()
            self.airflow_pressure_old = self.airflow_pressure
            self.airflow_pressure = self.ctx.airflow_ps.read()
            self.volume += (
                (time_now - self.sensors_time_saved)
                * (self.airflow_pressure + self.airflow_pressure_old)
                / 2
            )
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

            # logging.info("Period: %f", time_now - (self.sensors_time_saved + GAUGE_PRESSION_DIFF))
            self.sensors_time_saved = time_now

        if time_now >= self.oxygen_time_saved + OXYGEN_PRESSION_DIFF:
            self.oxygen_percentage = self.ctx.oxygen_sensor.read()

            self.oxygen_time_saved = time_now

        if time_now >= self.dht_time_saved + DHT_DIFF:
            self.atm_pressure = self.ctx.atm_ps.read()
            self.ctx.dht_box.trigger()
            self.ctx.dht_air.trigger()
            self.temperature_box = self.ctx.dht_box.temperature()
            self.humidity_box = self.ctx.dht_box.humidity()
            self.temperature_air = self.ctx.dht_air.temperature()
            self.humidity_air = self.ctx.dht_air.humidity()

            self.dht_time_saved = time_now

    def __check_alarms(self, msg: Messenger):
        """Check if any alarms triggered.

        Args:
            msg (Messenger): Utility for sending messages.
        """

        triggered = []

        if self.epap_read < self.pressure_min:
            triggered.append(
                {
                    "type": alarms.PRESSURE_MIN,
                    "criticality": "medium",
                    "timestamp": time.time(),
                }
            )
        elif self.ipap_read > self.pressure_max:
            triggered.append(
                {
                    "type": alarms.PRESSURE_MAX,
                    "criticality": "medium",
                    "timestamp": time.time(),
                }
            )

        if triggered:
            for alarm in triggered:
                msg.send(topics.ALARM, alarm)


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

        while True:
            pass
