---
title: "External events communication"
type: docs
weight: 1
description: >
    Integrate external applications with the respirator.
---

Respir-OS publishes the events that take place during its operation so the
system's functionality can be extended and integrated with other platforms.
These events are published using WebSockets. Clients can connect to the socket
using libraries like [Socket.IO](https://socket.io/) and start receiving events
and their data.

All the events that external applications can listen to are published on the
`/respir-os` namespace. In this section, these events and their data are
explained in detail.

## `parameters`

This event contains the respirator's current parameters of operation. Whenever
these parameters change, a new event is published with the updated values. Also,
when a new client connects to the socket, it automatically receives an event of
this type, so it can have the current parameters from the get-go.

Along with the event, a JSON document is sent with the following variables:

- `mode`: It's the respirator's operation mode. It can be either `VCP`
  (controlled mode) or `VPS` (assisted mode).
- `ipap`: Inspiratory Positive Airway Pressure. Air is insufflated into the
  patient's lungs at this pressure. Measured in centimeters of water (cmH<sub>2</sub>O).
- `epap`: Expiratory Positive Airway Pressure. Air is exhaled out of the lungs
  at this pressure. Measured in centimeters of water (cmH<sub>2</sub>O).
- `breathing_freq`: The breathing frequency, measured in breaths per minute.
- `ie_relation`: It's the ratio between the time spent during inhalation and
  the time spent during exhalation. For example, a 3:1 relation means that, for
  each time unit spent inhaling, 3 are spent exhaling.
- `trigger`: The flow trigger determines when we assume exhalation has finished
  and inhalation must begin. It is indicated in liters per minute (l/m).

__Example__
```JSON
{
    "mode": "VPS",
    "ipap": 20.0,
    "epap": 26.0,
    "breathing_freq": 15.0,
    "ie_relation": "1:3",
    "trigger": 5.0
}
```

## `cycle`

When a new breathing cycle begins, the system calculates the monitoring values
for the cycle that just ended and triggers an event. These values are sent in a
JSON document, wich contains the following variables:

- `ipap`: It's the maximum pressure achieved during the cycle. Measured in
  centimeters of water (cmH<sub>2</sub>O).
- `epap`: It's the pressure when the breathing flow is zero. Measured in
  centimeters of water (cmH<sub>2</sub>O).
- `breathing_freq`: The measured breathing frequency. As it changes shows very
  little change from cycle to cycle, the value given is the mean value of the
  last 3 cycles. Measured in breaths per minute.
- `tidal_volume`: The tidal volume is the amount of air insufflated into the
  patient. Measured in mililiters (ml).
- `volume_per_minute`: As the name suggests, it's the amount of air insufflated
  into the patient in a minute. Measured in liters (l).
- `oxygen_percentage`: The percentage of oxygen in the inhaled air.

__Example__
```JSON
{
  "ipap": 22.4,
  "epap": 23.6,
  "breathing_freq": 11.2,
  "tidal_volume": 26.2,
  "volume_per_minute": 35.3,
  "oxygen_percentage": 34.2
}
```

## `readings`

The system reads the values given by the sensors with very high frequency. These
readings are published in events with much lower frequency so the system doesn't
overload. Each reading has the following variables:

- `timestamp`: Unix time in which the reading was made.
- `flow`: Air flow, in liters per minute (l/m).
- `pressure`: Air pressure, in centimeters of water (cmH<sub>2</sub>O).
- `volume`: Air volume, in mililiters (ml).

__Example__
```JSON
[
  {
    "timestamp": "2020-11-12T12:51:00+00:00",
    "flow": -12.8,
    "pressure": 14.3,
    "volume": 3.0
  },
  {
    "timestamp": "2020-11-12T12:51:00+00:02",
    "flow": -10.3,
    "pressure": 10.2,
    "volume": 0.0
  }
]
```

## `alarm`

As part of the respirator's control system, there are a bunch of alarms that can
be triggered when certain values exceed their limits or other conditions take
place. When these alarms are triggered, an event of this type is also sent with
the following information about the alarm:

- `type`: The type of alarma, which can be either `apnea`, `disconnect`, `min_pressure`,
  `max_pressure`, `min_volume`, `max_volume`, `max_frequency` or `oxygen`.
- `criticality`: The level of criticality of the alarm, which can be either
  `normal` or `high`.

__Example__
```JSON
{
  "type": "apnea",
  "criticality": "normal"
}
