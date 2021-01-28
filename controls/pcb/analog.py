"""
This module contains utilites for working with analog devices, including a basic
analog-to-digital converter.
"""

import atexit
from typing import Callable

import pigpio


class AnalogConverter:
    """
    An MCP3008 analog to digital converter.
    """

    def __init__(self, pi: pigpio.pi, channel: int, baud_rate: int, voltage: float):
        """
        Instantiate a new ADC connected to the Pi.

        The device is connected by SPI on the given channel. Data transfer
        depends on the baud rate.

        The ADC's supply voltage is also necessary for the conversion
        calculations.
        """

        self.pi = pi
        self.channel = channel
        self.baud_rate = baud_rate
        self.voltage = voltage

        atexit.register(self.__cleanup)

        self.spi = pi.spi_open(channel, baud_rate)

    def __cleanup(self):
        """
        Clean things up before dumping.
        """

        self.pi.spi_close(self.spi)

    def read(self, channel: int) -> float:
        """
        Return the voltage value on the given channel.
        """

        _, data = self.pi.spi_xfer(self.spi, [1, (8 + channel) << 4, 0])
        raw_value = ((data[1] & 3) << 8) + data[2]
        value = (self.voltage / (2 ** 10 - 1)) * raw_value
        return value


class AnalogSensor:
    """
    A sensor connected to an analog-to-digital converter.
    """

    def __init__(self, adc: AnalogConverter, channel: int, func: Callable[[float], float]):
        """
        Create a new instance of an analog sensor.

        The ADC it is connected to and the channel must be given, along with the function used to
        convert the voltage to the actual reading.
        """

        self.adc = adc
        self.channel = channel
        self.func = func

    def read(self) -> float:
        """
        Trigger a new reading of the sensor.
        """

        voltage = self.adc.read(self.channel)
        return self.func(voltage)
