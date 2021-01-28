import random


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
    def read(self):
        return random.randint(0, 40)


class TestAirflow:
    def read(self):
        return random.randint(-50, 120)
