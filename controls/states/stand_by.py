import logging
import time

from common.ipc import Topic

from .operation import OperationState
from .state import State

MEAN_CALIBRATION_LENGTH = 200


class StandByState(State):
    """In this state, the system is waiting for the user to introduce the
    initial operation parameters.
    """

    def run(self):
        airflow_offset = 0.0
        gauge_offset = 0.0
        self.app.pcb.servo.set_angle(60)
        time_saved = time.time()
        time_start = 10.0

        while True:
            # Airflow and gauge calibration
            airflow_offset = (
                (MEAN_CALIBRATION_LENGTH - 1) / MEAN_CALIBRATION_LENGTH
            ) * airflow_offset + (
                1 / MEAN_CALIBRATION_LENGTH
            ) * self.app.pcb.airflow_ps.read()

            gauge_offset = (
                (MEAN_CALIBRATION_LENGTH - 1) / MEAN_CALIBRATION_LENGTH
            ) * gauge_offset + (
                1 / MEAN_CALIBRATION_LENGTH
            ) * self.app.pcb.gauge_ps.read()

            topic, body = self.app.ipc.recv(block=False)
            if topic == Topic.OPERATION_PARAMS:
                self.app.ctx.ipap = body["ipap"]
                self.app.ctx.epap = body["epap"]
                self.app.ctx.freq = body["freq"]
                self.app.ctx.trigger = body["trigger"]
                self.app.ctx.inhale = body["inhale"]
                self.app.ctx.exhale = body["exhale"]

                logging.info("Time: %f", time.time() - time_saved)
                # Airflow and gauge continue calibration
                while time.time() < time_saved + time_start:
                    airflow_offset = (
                        (MEAN_CALIBRATION_LENGTH - 1) / MEAN_CALIBRATION_LENGTH
                    ) * airflow_offset + (
                        1 / MEAN_CALIBRATION_LENGTH
                    ) * self.app.pcb.airflow_ps.read()

                    gauge_offset = (
                        (MEAN_CALIBRATION_LENGTH - 1) / MEAN_CALIBRATION_LENGTH
                    ) * gauge_offset + (
                        1 / MEAN_CALIBRATION_LENGTH
                    ) * self.app.pcb.gauge_ps.read()

                    time.sleep(0.0001)
                break

            time.sleep(0.0001)

        airflow_voltage_offset = self.__calculate_voltage_airflow(
            airflow_offset
        )
        gauge_voltage_offset = self.__calculate_voltage_gauge(gauge_offset)

        self.app.pcb.airflow_ps.func = lambda v: (
            -19.269 * (v - (airflow_voltage_offset - 2.0963)) ** 2
            + 172.15 * (v - (airflow_voltage_offset - 2.0963))
            - 276.2
        )

        self.app.pcb.gauge_ps.func = lambda v: (
            10.971 * (v - (gauge_voltage_offset - 0.54269)) - 5.9539
        )

        logging.info("Airflow Voltage offset:  %f", airflow_voltage_offset)
        logging.info("Airflow offset: %f", airflow_offset)
        logging.info("Gauge Voltage offset:  %f", airflow_voltage_offset)
        logging.info("Gauge offset: %f", gauge_offset)

        logging.info("Starting operation in controlled mode")
        logging.info("IPAP -> %d", body["ipap"])
        logging.info("EPAP -> %d", body["epap"])
        logging.info("Frequency -> %d", body["freq"])
        logging.info("Trigger -> %d", body["trigger"])
        logging.info("I:E -> %d:%d", body["inhale"], body["exhale"])

        self.app.transition_to(OperationState)

    def __calculate_voltage_airflow(self, airflow_offset):
        return (
            -172.15
            + (172.15 ** 2 - 4 * (-19.269) * (-276.2 - airflow_offset))
            ** (0.5)
        ) / (2 * (-19.269))

    def __calculate_voltage_gauge(self, gauge_offset):
        return (gauge_offset + 5.9539) / 10.971
