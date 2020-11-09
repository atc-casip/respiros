"""
This module provides a class to work with servos.
"""

import atexit

import pigpio

from respiros.pcb import pi


class Servo:
    """A continuous servo that moves between 0 and 180 degrees."""

    def __init__(self, pi: pigpio.pi, gpio: int, min_width: int, max_width: int):
        """
        Instantiate a new servo connected to the Pi on the given GPIO pin.

        The minimum and maximum pulse widths must be specified.
        """

        self.pi = pi
        self.gpio = gpio
        self.min_width = min_width
        self.max_width = max_width

        atexit.register(self.cleanup)

    def set_angle(self, angle: int):
        """Move the servo to a given angle between 0 and 180 degrees."""

        if angle < 0 or angle > 180:
            raise ValueError('The angle must be between 0 and 180 degrees.')

        width = (angle / 180) * (self.max_width - self.min_width)
        self.pi.set_servo_pulsewidth(self.gpio, width)

    def cleanup(self):
        """Clean things up before dumping."""

        self.pi.set_servo_pulsewidth(self.gpio, 0)
