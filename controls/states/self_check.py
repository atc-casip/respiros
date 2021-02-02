"""
System checks that are performed to validate its health.
"""

import logging
import time
from typing import Dict, Tuple

from .events import ChecksSuccessful, ChecksUnsuccessful, Event
from .failure import Failure
from .stand_by import StandBy
from .state import State

BOX_TMP_MIN = 10  # ºC
BOX_TMP_MAX = 50  # ºC
BOX_HUM_MIN = 0  # %
BOX_HUM_MAX = 100  # %
AIR_TMP_MIN = 10  # ºC
AIR_TMP_MAX = 50  # ºC
ATM_MIN = 33.3  # KPa
ATM_MAX = 106.0  # KPa
OXYGEN_MIN = 16  # %
OXYGEN_MAX = 95  # %
GAUGE_MIN = 407  # cmH2O
GAUGE_MAX = 510  # cmH2O
AIRFLOW_MIN = 0  # l/min
AIRFLOW_MAX = 40  # l/min


class SelfCheck(State):
    """
    Initial state where the device's status is checked.
    """

    def transitions(self) -> Dict[Event, State]:
        return {ChecksSuccessful: StandBy, ChecksUnsuccessful: Failure}

    def run(self) -> Event:
        # TODO: Call the actual functions instead of using static values

        dht_box_ok = True
        logging.info(
            "Box DHT sensor status: %s", "OK" if dht_box_ok else "FAIL"
        )

        dht_air_ok = True
        logging.info(
            "Air DHT sensor status: %s", "OK" if dht_air_ok else "FAIL"
        )

        gauge_ok, airflow_ok, servo_ok = (True, True, True)
        logging.info(
            "Gauge pressure sensor status: %s", "OK" if dht_air_ok else "FAIL"
        )
        logging.info(
            "Airflow pressure sensor status: %s",
            "OK" if dht_air_ok else "FAIL",
        )
        logging.info("Servo status: %s", "OK" if dht_air_ok else "FAIL")

        oxygen_ok = True
        logging.info(
            "Oxygen sensor status: %s", "OK" if dht_air_ok else "FAIL"
        )

        atm_ok = True
        logging.info(
            "Atmospheric pressure sensor status: %s",
            "OK" if dht_air_ok else "FAIL",
        )

        # We need to wait a bit so the GUI application can catch up
        time.sleep(2)

        self.ctx.messenger.send(
            "check",
            {
                "dht_box": dht_box_ok,
                "dht_air": dht_air_ok,
                "gauge": gauge_ok,
                "airflow": airflow_ok,
                "servo": servo_ok,
                "oxygen": oxygen_ok,
                "atmospheric": atm_ok,
            },
        )

        if all(
            [
                dht_box_ok,
                dht_air_ok,
                gauge_ok,
                airflow_ok,
                servo_ok,
                oxygen_ok,
                atm_ok,
            ]
        ):
            return ChecksSuccessful(None)
        return ChecksUnsuccessful(None)

    def __check_dht_box(self) -> bool:
        """
        Check temperature and humidity sensor.
        """

        for _ in range(3):
            self.ctx.dht_box.trigger()
            tmp = self.ctx.dht_box.temperature()
            hum = self.ctx.dht_box.humidity()
            if (
                BOX_TMP_MIN <= tmp <= BOX_TMP_MAX
                or BOX_HUM_MIN <= hum <= BOX_HUM_MAX
            ):
                return True
            time.sleep(2)

        return False

    def __check_dht_air(self) -> bool:
        """
        Check temperature and humidity sensor.
        """

        for _ in range(3):
            self.ctx.dht_air.trigger()
            tmp = self.ctx.dht_air.temperature()
            if AIR_TMP_MIN <= tmp <= AIR_TMP_MAX:
                return True
            time.sleep(2)

        return False

    # TODO: Simplify this function's implementation
    def __check_operation(self) -> Tuple[bool, bool, bool]:
        """
        Check pressure and airflow sensors, along with servo operation.
        """

        flag_check_gauge = False
        flag_check_airflow = False
        flag_check_servo = False
        flag_gauge_0_ok = False
        flag_flow_0_ok = False
        flag_gauge_180_ok = False
        flag_flow_180_ok = False
        angles = [0, 180]
        for _ in range(3):
            for angle in angles:
                self.ctx.servo.set_angle(angle)
                time.sleep(0.5)
                gauge_pressure = self.ctx.gauge_pressure_sensor.read()
                airflow_pressure = self.ctx.airflow_pressure_sensor.read()

                if (
                    angle == 0
                    and GAUGE_MIN * 0.95 < gauge_pressure < GAUGE_MIN * 1.05
                ):
                    flag_gauge_0_ok = True
                if (
                    angle == 0
                    and AIRFLOW_MAX * 0.9
                    < airflow_pressure
                    < AIRFLOW_MIN * 1.05
                ):
                    flag_flow_0_ok = True

                if (
                    angle == 180
                    and GAUGE_MAX * 0.95 < gauge_pressure < GAUGE_MAX * 1.05
                ):
                    flag_gauge_180_ok = True
                if (
                    angle == 180
                    and AIRFLOW_MAX * 0.95
                    < airflow_pressure
                    < AIRFLOW_MIN * 1.05
                ):
                    flag_flow_180_ok = True

            if flag_gauge_0_ok and flag_gauge_180_ok:
                flag_check_gauge = True
            if flag_flow_0_ok and flag_flow_180_ok:
                flag_check_airflow = True

            # If check GAUGE and AIRFLOW are OK, SERVO OK and stop attempting
            if flag_check_gauge and flag_check_airflow:
                flag_check_servo = True
                break

        return flag_check_gauge, flag_check_airflow, flag_check_servo

    def __check_oxygen(self) -> bool:
        """
        Check oxygen sensor.
        """

        oxygen_percentage = self.ctx.oxygen_sensor.read()
        if OXYGEN_MIN <= oxygen_percentage <= OXYGEN_MAX:
            return True

        return False

    def __check_atmospheric(self) -> bool:
        """
        Check ambient pressure sensor.
        """

        atm_pressure = self.ctx.atm_ps.read()
        if ATM_MIN <= atm_pressure <= ATM_MAX:
            return True

        return False
