"""
Utilities for working with analog devices.

This module includes classes for different sensors and a basic analog-to-digital
converter.
"""

import atexit

import pigpio

from respiros.pcb import pi


class ADC:
    """An MCP3008 analog to digital converter."""

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

        atexit.register(self.cleanup)

        self.spi = pi.spi_open(channel, baud_rate)

    def read_value(self, channel):
        """Return the voltage value on the given channel."""

        _, data = pi.spi_xfer(self.spi, [1, (8 + channel) << 4, 0])
        raw_value = ((data[1] & 3) << 8) + data[2]
        value = (self.voltage / (2 ** 10 - 1)) * raw_value
        return value

    def cleanup(self):
        """Clean things up before dumping."""

        self.pi.spi_close(self.spi)


class PressureSensor():
    """An analog pressure sensor connected to an ADC for value reading."""

    def __init__(self, adc: ADC, channel: int):
        """
        Instantiate a new pressure sensor.

        The sensor is connected to the given ADC on the specified channel.
        """

        self.adc = adc
        self.channel = channel

    def pressure(self):
        """Return the current pressure in kilopascals."""

        voltage = self.adc.read_value(self.channel)
