"""
This module contains classes for the digital devices connected to the PCB.
"""

import atexit
import time

import pigpio

from respiros.pcb import pi


class DHT:
    """A DHT22 sensor for temperature and humidity reading."""

    def __init__(self, pi: pigpio.pi, gpio: int):
        """
        Instantiate a new sensor connected to the Pi on the given GPIO
        pin.
        """

        self.pi = pi
        self.gpio = gpio

        atexit.register(self.cleanup)

        self.cb = None   # Read callback.

        self.bad_CS = 0  # Bad checksum count.
        self.bad_SM = 0  # Short message count.
        self.bad_MM = 0  # Missing message count.

        self.rhum = -999
        self.temp = -999

        self.tov = None

        self.high_tick = 0
        self.bit = 40

        pi.set_pull_up_down(gpio, pigpio.PUD_OFF)

        pi.set_watchdog(gpio, 0)  # Kill any watchdogs.

        self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cb)

    def _cb(self, gpio, level, tick):
        """
        Accumulate the 40 data bits and format into 5 bytes: humidity high,
        humidity low, temperature high, temperature low and checksum.
        """

        diff = pigpio.tickDiff(self.high_tick, tick)

        if level == 0:
            # Edge length determines if bit is 1 or 0.
            if diff >= 50:
                val = 1
                if diff >= 200:     # Bad bit?
                    self.CS = 256   # Force bad checksum.
            else:
                val = 0

            if self.bit >= 40:      # Message complete.
                self.bit = 40

            elif self.bit >= 24:    # Temp low byte.
                self.tL = (self.tL << 1) + val

            elif self.bit >= 16:    # Temp high byte.
                self.tH = (self.tH << 1) + val

            elif self.bit >= 8:     # Humidity low byte.
                self.hL = (self.hL << 1) + val

            elif self.bit >= 0:     # Humidity high byte.
                self.hH = (self.hH << 1) + val

            elif self.bit >= 32:    # Checksum byte.
                self.CS = (self.CS << 1) + val

                if self.bit == 39:   # 40th bit received.
                    self.pi.set_watchdog(self.gpio, 0)

                    total = self.hH + self.hL + self.tH + self.tL

                    if (total & 255) == self.CS:    # Is checksum ok?
                        self.rhum = ((self.hH << 8) + self.hL) * 0.1

                        if self.tH & 128:
                            mult = -0.1
                            self.tH = self.tH & 127
                        else:
                            mult = 0.1

                        self.temp = ((self.tH << 8) + self.tL) * mult
                        self.tov = time.time()
                    else:
                        self.bad_CS += 1

            else:   # Header bits
                pass

            self.bit += 1

        elif level == 1:
            self.high_tick = tick
            if diff > 250000:
                self.bit = -1
                self.hH = self.hL = self.tH = self.tL = self.CS = 0

        else:   # Timeout
            self.pi.set_watchdog(self.gpio, 0)

            if self.bit < 8:        # Too few data bits received.
                self.bad_MM += 1    # Bump missing message count.

            elif self.bit < 39:     # Short message received.
                self.bad_SM += 1    # Bump short message count.

            else:                   # Full message received.
                pass

    def temperature(self):
        """Return current temperature in celsius."""

        return self.temp

    def humidity(self):
        """Return current relative humidity."""

        return self.humidity

    def staleness(self):
        """Return time since measurement made."""

        if self.tov is not None:
            return time.time() - self.tov
        else:
            return -999

    def bad_checksums(self):
        """Return count of messages received with bad checksums."""

        return self.bad_CS

    def short_messages(self):
        """Return count of short messages."""

        return self.bad_SM

    def missing_messages(self):
        """Return count of missing messages."""

        return self.bad_MM

    def trigger(self):
        """Trigger a new relative humidity and temperature reading."""

        self.pi.write(self.gpio, pigpio.LOW)
        time.sleep(0.017)  # 17 ms
        self.pi.set_mode(self.gpio, pigpio.INPUT)
        self.pi.set_watchdog(self.gpio, 200)

    def cleanup(self):
        """Clean things up before dumping."""

        self.pi.set_watchdog(self.gpio, 0)  # Kill all watchdogs.

        if self.cb is not None:
            self.cb.cancel()
            self.cb = None
