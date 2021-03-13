import atexit
import logging
import sys

import pigpio

from .analog import AnalogConverter, AnalogSensor
from .digital import DHTSensor
from .servo import Servo

from .mock import (
    MockServo,
    MockDHTSensor,
    MockAnalogSensorRandom,
    MockAnalogSensorSignal,
)
from .mock.signals import flux, pressure


class PCBController:
    """Helper class that wraps all the PCB components for easy use.

    This class also handles device initialization.
    """

    def __init__(self, app=None):
        self.dht_box = None
        self.dht_air = None
        self.servo = None
        self.airflow_ps = None
        self.atm_ps = None
        self.gauge_ps = None
        self.oxygen_sensor = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if app.config["DEBUG"]:
            # Create mock components
            self.dht_box = MockDHTSensor((10, 50), (0, 100))
            self.dht_air = MockDHTSensor((10, 50), (0, 100))

            self.servo = MockServo()

            self.oxygen_sensor = MockAnalogSensorRandom((16, 95))
            self.atm_ps = MockAnalogSensorRandom((34, 105))
            self.gauge_ps = MockAnalogSensorSignal(pressure)
            self.airflow_ps = MockAnalogSensorSignal(flux)
        else:
            # Create normal components
            pi = pigpio.pi()
            atexit.register(pi.stop)
            if not pi.connected:
                logging.fatal("Can't find pigpiod")
                sys.exit()

            self.dht_box = DHTSensor(pi, app.config["DHT_BOX_GPIO"])
            self.dht_air = DHTSensor(pi, app.config["DHT_AIR_GPIO"])

            self.servo = Servo(
                pi,
                app.config["SERVO_GPIO"],
                app.config["SERVO_MIN_WIDTH"],
                app.config["SERVO_MAX_WIDTH"],
            )

            adc = AnalogConverter(
                pi,
                app.config["ADC_SPI_CHANNEL"],
                app.config["ADC_BAUD_RATE"],
                app.config["ADC_REF_VOLTAGE"],
            )
            self.atm_ps = AnalogSensor(
                adc,
                app.config["ADC_ATM_CHANNEL"],
                lambda v: (v - 0.21) / (4.6 / 100) + 15,
            )
            self.airflow_ps = AnalogSensor(
                adc,
                app.config["ADC_AIRFLOW_CHANNEL"],
                lambda v: (-19.269 * v ** 2 + 172.15 * v - 276.2),
            )
            self.gauge_ps = AnalogSensor(
                adc,
                app.config["ADC_GAUGE_CHANNEL"],
                lambda v: (10.971 * v - 5.9539),
            )
            self.oxygen_sensor = AnalogSensor(
                adc,
                app.config["ADC_OXYGEN_CHANNEL"],
                lambda v: (74 - 21) / (0.0425 - 0.01) * v,
            )

        app.pcb = self


pcb = PCBController()
