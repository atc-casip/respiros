"""
System context.
"""

from dataclasses import dataclass

from common.ipc import Publisher, Subscriber

import controls.pcb as pcb


@dataclass
class Context:
    """
    Necessary context for system operation.
    """

    pub: Publisher
    sub: Subscriber
    servo: pcb.Servo
    dht_box: pcb.DHTSensor
    dht_air: pcb.DHTSensor
    atm_ps: pcb.AnalogSensor
    airflow_ps: pcb.AnalogSensor
    gauge_ps: pcb.AnalogSensor
    oxygen_sensor: pcb.AnalogSensor
