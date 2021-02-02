"""
This module contains classes for the digital devices connected to the PCB.
"""

import atexit
import logging
import time

import pigpio


# TODO: Simplify implementation.
class DHTSensor:
    """
    A DHT22 sensor for temperature and humidity reading.
    """

    def __init__(self, pi: pigpio.pi, gpio_pin: int):
        """
        Instantiate with the Pi and gpio to which the DHT22 output
        pin is connected.
        """

        self.pi = pi
        self.gpio_pin = gpio_pin

        self.cb = None

        atexit.register(self.__cleanup)

        self.bad_CS = 0  # Bad checksum count.
        self.bad_SM = 0  # Short message count.
        self.bad_MM = 0  # Missing message count.
        self.bad_SR = 0  # Sensor reset count.

        # Power cycle if timeout > MAX_TIMEOUTS.
        self.no_response = 0
        self.MAX_NO_RESPONSE = 2

        self.rhum = -999
        self.temp = -999

        self.tov = None

        self.high_tick = 0
        self.bit = 40

        pi.set_pull_up_down(gpio_pin, pigpio.PUD_OFF)

        pi.set_watchdog(gpio_pin, 0)  # Kill any watchdogs.

        self.cb = pi.callback(gpio_pin, pigpio.EITHER_EDGE, self.__cb)

    def __cleanup(self):
        """Clean up before dumping"""

        self.pi.set_watchdog(self.gpio_pin, 0)  # Kill all watchdogs.

        if self.cb is not None:
            self.cb.cancel()
            self.cb = None

        logging.info("Destroyed DHT sensor")

    def __cb(self, gpio_pin, level, tick):
        """
        Accumulate the 40 data bits.  Format into 5 bytes, humidity high,
        humidity low, temperature high, temperature low, checksum.
        """
        diff = pigpio.tickDiff(self.high_tick, tick)

        if level == 0:

            # Edge length determines if bit is 1 or 0.

            if diff >= 50:
                val = 1
                if diff >= 200:  # Bad bit?
                    self.CS = 256  # Force bad checksum.
            else:
                val = 0

            if self.bit >= 40:  # Message complete.
                self.bit = 40

            elif self.bit >= 32:  # In checksum byte.
                self.CS = (self.CS << 1) + val

                if self.bit == 39:

                    # 40th bit received.

                    self.pi.set_watchdog(self.gpio_pin, 0)

                    self.no_response = 0

                    total = self.hH + self.hL + self.tH + self.tL

                    if (total & 255) == self.CS:  # Is checksum ok?

                        self.rhum = ((self.hH << 8) + self.hL) * 0.1

                        if self.tH & 128:  # Negative temperature.
                            mult = -0.1
                            self.tH = self.tH & 127
                        else:
                            mult = 0.1

                        self.temp = ((self.tH << 8) + self.tL) * mult

                        self.tov = time.time()

                    else:

                        self.bad_CS += 1

            elif self.bit >= 24:  # in temp low byte
                self.tL = (self.tL << 1) + val

            elif self.bit >= 16:  # in temp high byte
                self.tH = (self.tH << 1) + val

            elif self.bit >= 8:  # in humidity low byte
                self.hL = (self.hL << 1) + val

            elif self.bit >= 0:  # in humidity high byte
                self.hH = (self.hH << 1) + val

            else:  # header bits
                pass

            self.bit += 1

        elif level == 1:
            self.high_tick = tick
            if diff > 250000:
                self.bit = -2
                self.hH = self.hL = self.tH = self.tL = self.CS = 0

        else:  # level == pigpio.TIMEOUT:
            self.pi.set_watchdog(self.gpio_pin, 0)
            if self.bit < 8:  # Too few data bits received.
                self.bad_MM += 1  # Bump missing message count.
                self.no_response += 1
                if self.no_response > self.MAX_NO_RESPONSE:
                    self.no_response = 0
                    self.bad_SR += 1  # Bump sensor reset count.
            elif self.bit < 39:  # Short message receieved.
                self.bad_SM += 1  # Bump short message count.
                self.no_response = 0

            else:  # Full message received.
                self.no_response = 0

    def temperature(self):
        """Return current temperature."""
        return self.temp

    def humidity(self):
        """Return current relative humidity."""
        return self.rhum

    def staleness(self):
        """Return time since measurement made."""
        if self.tov is not None:
            return time.time() - self.tov
        else:
            return -999

    def bad_checksum(self):
        """Return count of messages received with bad checksums."""
        return self.bad_CS

    def short_message(self):
        """Return count of short messages."""
        return self.bad_SM

    def missing_message(self):
        """Return count of missing messages."""
        return self.bad_MM

    def sensor_resets(self):
        """Return count of power cycles because of sensor hangs."""
        return self.bad_SR

    def trigger(self):
        """Trigger a new relative humidity and temperature reading."""

        self.pi.write(self.gpio_pin, pigpio.LOW)
        time.sleep(0.017)  # 17 ms
        self.pi.set_mode(self.gpio_pin, pigpio.INPUT)
        self.pi.set_watchdog(self.gpio_pin, 200)
