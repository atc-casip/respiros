"""
Perform control system initialization.
"""

import atexit
import logging

import pigpio

import controls.pcb as pcb
import controls.states as states
import controls.test_pcb as test_pcb
from controls.context import Context

SERVO_GPIO = 15
SERVO_MIN_WIDTH = 500
SERVO_MAX_WIDTH = 2500

DHT_BOX_GPIO = 16
DHT_AIR_GPIO = 16

ADC_CHANNEL = 0
BAUD_RATE = 96000
VOLTAGE_REFERENCE = 5

GAUGE_CHANNEL = 4
AIRFLOW_CHANNEL = 1
ATMOSPHERIC_CHANNEL = 5
OXYGEN_CHANNEL = 2


if __name__ == "__main__":
    # TODO: Use different configurations for dev and prod environments
    logging.basicConfig(
        filename="logs/controls.log", filemode="w", level=logging.INFO
    )
    from .ipc import pub, sub

    """
    # Create Pi instance
    pi = pigpio.pi()
    atexit.register(pi.stop)
    if not pi.connected:
        logging.fatal('Can\'t find pigpiod')
        sys.exit()

    # Initialize PCB elements
    servo = pcb.Servo(pi, SERVO_GPIO, SERVO_MIN_WIDTH, SERVO_MAX_WIDTH)
    dht_box = pcb.DHTSensor(pi, DHT_BOX_GPIO)
    dht_air = pcb.DHTSensor(pi, DHT_AIR_GPIO)
    adc = pcb.AnalogConverter(pi, ADC_CHANNEL, BAUD_RATE, VOLTAGE_REFERENCE)
    atm_ps = pcb.AnalogSensor(
        adc, ATMOSPHERIC_CHANNEL, lambda v: (v-0.21)/(4.6/100)+15)
    airflow_ps = pcb.AnalogSensor(
        adc, AIRFLOW_CHANNEL, lambda v: (-19.269 * v**2 + 172.15*v - 276.2))
    gauge_ps = pcb.AnalogSensor(
        adc, GAUGE_CHANNEL, lambda v: (10.971*v - 5.9539))
    oxygen_sensor = pcb.AnalogSensor(
        adc, OXYGEN_CHANNEL, lambda v: (74-21)/(0.0425-0.01)*v)
    """

    servo = test_pcb.TestServo()
    dht_box = test_pcb.TestDHT()
    dht_air = test_pcb.TestDHT()
    atm_ps = test_pcb.TestATM()
    airflow_ps = test_pcb.TestAirflow()
    gauge_ps = test_pcb.TestGauge()
    oxygen_sensor = test_pcb.TestOxygen()

    # Create system context
    ctx = Context(
        pub,
        sub,
        servo,
        dht_box,
        dht_air,
        atm_ps,
        airflow_ps,
        gauge_ps,
        oxygen_sensor,
    )

    current_state = states.SelfCheck(ctx)
    while True:
        event = current_state.run()
        current_state = current_state.next(event)

        logging.info("Transitioned to state <%s>", type(current_state))
