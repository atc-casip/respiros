"""
System context.
"""

from dataclasses import dataclass

import controls.pcb as pcb
from controls.sockets import Messenger


@dataclass
class Context:
    """
    Necessary context for system operation.
    """

    messenger: Messenger
    servo: pcb.Servo
    dht_box: pcb.DHTSensor
    dht_air: pcb.DHTSensor
    atm_ps: pcb.AnalogSensor
    airflow_ps: pcb.AnalogSensor
    gauge_ps: pcb.AnalogSensor
    oxygen_sensor: pcb.AnalogSensor
