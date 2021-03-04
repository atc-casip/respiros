"""
Before starting operation, the system waits for the user to define the
necessary parameters.
"""

import logging
import time
from typing import Dict

import zmq
from common.ipc import Topic

from .events import Event, StartOperationControlled
from .operation import OperationControlled
from .state import State

MEAN_CALIBRATION_LENGTH = 200


class StandBy(State):
    """
    Waiting for the user to select an operation mode.
    """

    def transitions(self) -> Dict[Event, State]:
        return {StartOperationControlled: OperationControlled}

    def run(self) -> Event:
        airflow_offset = 0.0
        gauge_offset = 0.0
        self.ctx.servo.set_angle(60)
        time_saved = time.time()
        time_start = 10.0

        while True:
            # Airflow and gauge calibration
            airflow_offset = (
                (MEAN_CALIBRATION_LENGTH - 1) / MEAN_CALIBRATION_LENGTH
            ) * airflow_offset + (
                1 / MEAN_CALIBRATION_LENGTH
            ) * self.ctx.airflow_ps.read()

            gauge_offset = (
                (MEAN_CALIBRATION_LENGTH - 1) / MEAN_CALIBRATION_LENGTH
            ) * gauge_offset + (
                1 / MEAN_CALIBRATION_LENGTH
            ) * self.ctx.gauge_ps.read()

            try:
                [topic, msg] = self.ctx.sub.recv(block=False)
                if topic == Topic.OPERATION_PARAMS:
                    logging.info("Time: %f", time.time() - time_saved)
                    # Airflow and gauge continue calibration
                    while time.time() < time_saved + time_start:
                        airflow_offset = (
                            (MEAN_CALIBRATION_LENGTH - 1)
                            / MEAN_CALIBRATION_LENGTH
                        ) * airflow_offset + (
                            1 / MEAN_CALIBRATION_LENGTH
                        ) * self.ctx.airflow_ps.read()

                        gauge_offset = (
                            (MEAN_CALIBRATION_LENGTH - 1)
                            / MEAN_CALIBRATION_LENGTH
                        ) * gauge_offset + (
                            1 / MEAN_CALIBRATION_LENGTH
                        ) * self.ctx.gauge_ps.read()

                        time.sleep(0.0001)
                    break
            except zmq.Again:
                pass

            time.sleep(0.0001)

        airflow_voltage_offset = self.__calculate_voltage_airflow(
            airflow_offset
        )
        gauge_voltage_offset = self.__calculate_voltage_gauge(gauge_offset)

        self.ctx.airflow_ps.func = lambda v: (
            -19.269 * (v - (airflow_voltage_offset - 2.0963)) ** 2
            + 172.15 * (v - (airflow_voltage_offset - 2.0963))
            - 276.2
        )

        self.ctx.gauge_ps.func = lambda v: (
            10.971 * (v - (gauge_voltage_offset - 0.54269)) - 5.9539
        )

        logging.info("Airflow Voltage offset:  %f", airflow_voltage_offset)
        logging.info("Airflow offset: %f", airflow_offset)
        logging.info("Gauge Voltage offset:  %f", airflow_voltage_offset)
        logging.info("Gauge offset: %f", gauge_offset)

        logging.info("Starting operation in controlled mode")
        logging.info("IPAP -> %d", msg["ipap"])
        logging.info("EPAP -> %d", msg["epap"])
        logging.info("Frequency -> %d", msg["freq"])
        logging.info("Trigger -> %d", msg["trigger"])
        logging.info("I:E -> %d:%d", msg["inhale"], msg["exhale"])

        return StartOperationControlled(
            {
                "ipap": msg["ipap"],
                "epap": msg["epap"],
                "freq": msg["freq"],
                "inhale": msg["inhale"],
                "exhale": msg["exhale"],
                "trigger": msg["trigger"],
                "from_standby": True,
            }
        )

    def __calculate_voltage_airflow(self, airflow_offset):
        return (
            -172.15
            + (172.15 ** 2 - 4 * (-19.269) * (-276.2 - airflow_offset))
            ** (0.5)
        ) / (2 * (-19.269))

    def __calculate_voltage_gauge(self, gauge_offset):
        return (gauge_offset + 5.9539) / 10.971
