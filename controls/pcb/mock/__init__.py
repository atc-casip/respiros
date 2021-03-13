import random
from typing import List, Tuple


class MockServo:
    """Mock implementation for the servo."""

    def set_angle(self, angle: int):
        return


class MockDHTSensor:
    """Mock implementation for the DHT sensors."""

    def __init__(self, tmp_range: Tuple[int, int], hum_range: Tuple[int, int]):
        self.tmp_range = tmp_range
        self.hum_range = hum_range

    def trigger(self):
        return

    def temperature(self):
        return random.randint(self.tmp_range[0], self.tmp_range[1])

    def humidity(self):
        return random.randint(self.hum_range[0], self.hum_range[1])


class MockAnalogSensorRandom:
    """Mock implementation for an analog sensor that returns a random
    integer.
    """

    def __init__(self, range: Tuple[int, int]):
        self.range = range
        self.func = None

    def read(self):
        return random.randint(self.range[0], self.range[1])


class MockAnalogSensorSignal:
    """Mock implementation for an analog sensor that simulates a real
    signal."""

    def __init__(self, signal: List[float]):
        self.signal = signal
        self.counter = 0
        self.func = None

    def read(self):
        value = self.signal[self.counter]
        self.counter += 1
        if self.counter == len(self.signal):
            self.counter = 0
        return value
