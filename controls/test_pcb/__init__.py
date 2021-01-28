import random

from .signals import flux, pressure


class TestServo:
    def set_angle(self, angle: int):
        return


class TestDHT:
    def trigger(self):
        return

    def temperature(self):
        return random.randint(10, 50)

    def humidity(self):
        return random.randint(0, 100)


class TestATM:
    def read(self):
        return random.randint(34, 105)


class TestOxygen:
    def read(self):
        return random.randint(16, 95)


class TestGauge:

    counter = 0

    def read(self):
        value = pressure[self.counter]
        self.counter += 1
        if self.counter == len(pressure):
            self.counter = 0
        return value


class TestAirflow:

    counter = 0

    def read(self):
        value = flux[self.counter]
        self.counter += 1
        if self.counter == len(flux):
            self.counter = 0
        return value
