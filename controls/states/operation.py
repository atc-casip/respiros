from datetime import datetime
import logging
import time
from typing import Dict

import numpy as np
import zmq
from common.alarms import Alarm, Criticality, Type
from common.ipc import Topic
from controls.context import Context

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


class OperationState(State):
    """
    Controlled ventilation.
    """

    def __init__(self, app):
        super().__init__(app)

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
        # FIXME: Possibly needs to be initialized
        # on first execution of the state
        self.sensors_time_saved = 0.0
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

        # Transition variables between operation modes
        self.operation = False
        self.airflow_trigger = None
        self.airflow_max = None

        # System mode ON or OFF
        self.mode = True

    def run(self):
        # Initializations
        insp_exp = False  # Start in inhalation
        self.time_saved = time.time()  # Get time reference
        self.sensors_time_saved = time.time()
        self.operation = False  # Start in control operation mode
        self.__get_ie_durations()  # Obtain initial cycle, I and E durations

        while True:
            # IPC communication
            topic, body = self.app.ipc.recv(block=False)
            if topic == Topic.REQUEST_READING:
                self.app.ipc.send(
                    Topic.READING,
                    {
                        "pressure": self.gauge_pressure_filtered,
                        "airflow": self.airflow_pressure_filtered,
                        "volume": self.volume,
                        "timestamp": self.sensors_time_saved,
                    },
                )
            elif topic == Topic.OPERATION_PARAMS:
                logging.info("Received new operation parameters")
                self.app.ctx.ipap = body["ipap"]
                self.app.ctx.epap = body["epap"]
                self.app.ctx.freq = body["freq"]
                self.app.ctx.inhale = body["inhale"]
                self.app.ctx.exhale = body["exhale"]
                self.__get_ie_durations()
            elif topic == Topic.OPERATION_ALARMS:
                logging.info("Received new alarm ranges")
                self.app.ctx.pressure_min = body["pressure_min"]
                self.app.ctx.pressure_max = body["pressure_max"]
                self.app.ctx.volume_min = body["volume_min"]
                self.app.ctx.volume_max = body["volume_max"]
                self.app.ctx.oxygen_min = body["oxygen_min"]
                self.app.ctx.oxygen_max = body["oxygen_max"]
                self.app.ctx.freq_max = body["freq_max"]

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
                            >= self.app.ctx.trigger
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

            # IE cycling execution: Espiration or Inspiration
            if insp_exp:  # Espiration
                self.epap_read = (
                    (MEAN_IEPAP_LENGTH - 1) / MEAN_IEPAP_LENGTH
                ) * self.epap_read + (
                    1 / MEAN_IEPAP_LENGTH
                ) * self.gauge_pressure
                self.app.pcb.servo.set_angle(self.epap_angle)

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
                        >= self.app.ctx.trigger
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

                self.app.pcb.servo.set_angle(self.ipap_angle)

            # Read sensors and check alarms
            self.__read_sensors()
            self.__update_iepap_table()
            self.__check_alarms()
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

        self.cycle_duration = 60 / self.app.ctx.freq  # ms
        self.insp_duration = (
            self.cycle_duration
            / (self.app.ctx.inhale + self.app.ctx.exhale)
            * self.app.ctx.inhale
        )
        self.esp_duration = (
            self.cycle_duration
            / (self.app.ctx.exhale + self.app.ctx.inhale)
            * self.app.ctx.exhale
        )

        logging.info("Inhale duration: %f", self.insp_duration)
        logging.info("Exhale duration: %f", self.esp_duration)

    def __send_cycle(self):
        """Obtain respiration frequency and send cycle info."""

        if self.mode:
            self.freq_read = 60 / (
                self.insp_duration_read + self.esp_duration_read
            )
        else:
            self.freq_read = 0

        self.freq_mean = (
            (MEAN_FREQ_LENGTH - 1) / MEAN_FREQ_LENGTH
        ) * self.freq_mean + (1 / MEAN_FREQ_LENGTH) * self.freq_read

        self.app.ipc.send(
            Topic.CYCLE,
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

        if self.app.ctx.ipap != self.ipap_old or not self.mode:
            if not self.iepap_index[int(self.app.ctx.ipap - 1)]:
                self.ipap_angle = (
                    20.009 * np.log(float(self.app.ctx.ipap)) + 37.997
                )
            else:
                self.ipap_angle = self.iepap_table[int(self.app.ctx.ipap - 1)]
            self.ipap_old = self.app.ctx.ipap
        else:
            difference = float(self.app.ctx.ipap - self.ipap_read)
            if difference > 0.5 or difference < -0.5:
                self.ipap_angle = self.ipap_angle + 0.5 * difference

        if self.ipap_angle > SERVO_MAX_ANGLE:
            self.ipap_angle = SERVO_MAX_ANGLE
        elif self.ipap_angle < SERVO_MIN_ANGLE:
            self.ipap_angle = SERVO_MIN_ANGLE
        logging.info("IPAP angle: %f", self.ipap_angle)

    def __calculate_angle_epap(self):
        """Get servo angle based on IPAP."""

        if self.app.ctx.epap != self.epap_old or not self.mode:
            if not self.iepap_index[int(self.app.ctx.epap - 1)]:
                self.epap_angle = (
                    20.009 * np.log(float(self.app.ctx.epap)) + 37.997
                )
            else:
                self.epap_angle = self.iepap_table[int(self.app.ctx.epap - 1)]
            self.epap_old = self.app.ctx.epap
        else:
            difference = float(self.app.ctx.epap - self.epap_read)
            if difference > 0.5 or difference < -0.5:
                difference = float(self.app.ctx.epap - self.epap_read)
                self.epap_angle = self.epap_angle + 0.5 * difference

        if self.epap_angle < SERVO_MIN_ANGLE:
            self.epap_angle = SERVO_MIN_ANGLE
        elif self.epap_angle > SERVO_MAX_ANGLE:
            self.epap_angle = SERVO_MAX_ANGLE

        logging.info("EPAP angle: %f", self.epap_angle)

    def __update_iepap_table(self):
        """Update pressure angle table based."""

        if abs(self.app.ctx.epap - self.epap_read) < 0.3:
            self.iepap_table[int(self.app.ctx.epap - 1)] = self.epap_angle
            self.iepap_index[int(self.app.ctx.epap - 1)] = 1
            # logging.info("I: %s", self.iepap_table)

        if abs(self.app.ctx.ipap - self.ipap_read) < 0.3:
            self.iepap_table[int(self.app.ctx.ipap - 1)] = self.ipap_angle
            self.iepap_index[int(self.app.ctx.ipap - 1)] = 1
            # logging.info("I: %s", self.iepap_table)

    def __read_sensors(self):
        """Fetch readings from all the sensors."""

        time_now = time.time()

        if time_now >= (self.sensors_time_saved + GAUGE_PRESSION_DIFF):
            self.gauge_pressure = self.app.pcb.gauge_ps.read()
            self.airflow_pressure_old = self.airflow_pressure
            self.airflow_pressure = self.app.pcb.airflow_ps.read()
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
            self.oxygen_percentage = self.app.pcb.oxygen_sensor.read()

            self.oxygen_time_saved = time_now

        if time_now >= self.dht_time_saved + DHT_DIFF:
            self.atm_pressure = self.app.pcb.atm_ps.read()
            self.app.pcb.dht_box.trigger()
            self.app.pcb.dht_air.trigger()
            self.temperature_box = self.app.pcb.dht_box.temperature()
            self.humidity_box = self.app.pcb.dht_box.humidity()
            self.temperature_air = self.app.pcb.dht_air.temperature()
            self.humidity_air = self.app.pcb.dht_air.humidity()

            self.dht_time_saved = time_now

    def __check_alarms(self):
        """Check if any alarms triggered."""

        outbound = []
        timestamp = datetime.now()
        for alarm in self.app.ctx.alarms:
            if alarm.type == Type.PRESSURE_MIN:
                if self.epap_read < self.app.ctx.pressure_min:
                    if alarm.criticality == Criticality.NONE:
                        alarm.criticality = Criticality.MEDIUM
                        alarm.timestamp = timestamp
                        outbound.append(alarm)
                    elif alarm.criticality == Criticality.MEDIUM:
                        pass
                elif alarm.criticality in {
                    Criticality.MEDIUM,
                    Criticality.HIGH,
                }:
                    alarm.criticality = Criticality.NONE
                    alarm.timestamp = timestamp
                    outbound.append(alarm)
            elif alarm.type == Type.PRESSURE_MAX:
                if self.ipap_read > self.app.ctx.pressure_max:
                    if alarm.criticality == Criticality.NONE:
                        alarm.criticality = Criticality.MEDIUM
                        alarm.timestamp = timestamp
                        outbound.append(alarm)
                    elif alarm.criticality == Criticality.MEDIUM:
                        pass
                elif alarm.criticality in {
                    Criticality.MEDIUM,
                    Criticality.HIGH,
                }:
                    alarm.criticality = Criticality.NONE
                    alarm.timestamp = timestamp
                    outbound.append(alarm)

        for alarm in outbound:
            self.app.ipc.send(
                Topic.ALARM,
                {
                    "type": alarm.type.name,
                    "criticality": alarm.criticality.name,
                    "timestamp": alarm.timestamp.timestamp(),
                },
            )
