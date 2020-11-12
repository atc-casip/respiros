---
title: "Comunicación externa de eventos"
type: docs
weight: 1
description: >
    Integrar aplicaciones externas con el respirador.
---

Para permitir la extensión de la funcionalidad del sistema y su integración con
otras plataformas, Respir-OS publica los eventos que tienen lugar durante su
funcionamiento mediante WebSockets. Los clientes pueden conectarse al socket
usando librerías como [Socket.IO](https://socket.io/) para recibir los eventos
cuando sucedan y poder trabajar sobre sus datos.

En concreto, los eventos se publican en el espacio de nombres `/respir-os`. En
esta sección, se detallan todos los eventos que genera el respirador y sus datos
asociados.

## `parameters`

Este evento contiene los parámetros de operación actuales del respirador. Se
publica un nuevo evento cuando alguno de estos parámetros cambia, proporcionando
los valores actualizados. Además, cuando un nuevo cliente se conecta al socket,
recibe también este evento de inmediato para que sepa los parámetros actuales
del dispositivo.

Junto con el evento, se envía un documento JSON con las siguientes variables:

- `mode`: El modo de operación del respirador. Puede ser `VCP` (modo controlado) o
  `VPS` (modo asistido).
- `ipap`: _Inspiratory Positive Airway Pressure_. Es la presión con la que se
  insufla aire en los pulmones del paciente. Se mide en centímetros de agua
  (cmH<sub>2</sub>O).
- `epap`: _Expiratory Positive Airway Pressure_. Es la presión entrante bajo la
  cual se exhala el aire de los pulmones. Se mide en centímetros de agua
  (cmH<sub>2</sub>O).
- `breathing_freq`: La frecuencia respiratoria, indicada en número de
  respiraciones por minuto.
- `ie_relation`: La relación I:E es el ratio entre el tiempo que se tarda en
  inhalar y el tiempo que se tarda en exhalar. Por ejemplo, una relación 3:1
  implica que, por cada unidad de tiempo dedicada a exhalar, se dedican 3 a
  inhalar.
- `trigger`: El _trigger_ de flujo es lo que nos permite saber que el paciente
  ha terminado de exhalar y puede pasar a inhalar. Se indica en litros por
  minuto (l/m), es decir, se basa en el volumen de aire.

__Ejemplo__
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

Cuando comienza un nuevo ciclo, el sistema obtiene los valores de monitorización
del ciclo que acaba de terminar y los envía en un evento. Estos valores se
envían en un documento JSON junto con el evento, que contiene las siguientes
variables:

- `ipap`: La máxima presión alcanzada en el ciclo. Se mide en centímetros de
  agua (cmH<sub>2</sub>O).
- `epap`: La presión cuando el flujo espiratorio pasa por cero. Se mide en
  centímetros de agua (cmH<sub>2</sub>O).
- `breathing_freq`: Se trata de la frecuencia real. Al variar muy poco entre
  ciclos, el valor que se da es el promedio de los 3 últimos ciclos. Se mide en
  respiraciones por minuto.
- `tidal_volume`: El volumen corriente o volumen tidal. Es la cantidad de aire
  que se le inserta al paciente en el insuflado. Se mide en mililitros.
- `volume_per_minute`: El volumen por minuto. Es la cantidad de aire que se le
  insufla al paciente al cabo de un minuto. Se mide en litros.
- `oxygen_percentage`: El porcentaje de oxígeno del aire inspirado.

__Ejemplo__
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

## `reading`

El sistema realiza lecturas de los distintos sensores que posee con una
frecuencia muy alta. Con menor frecuencia, el sistema lanza un evento con las
lecturas realizadas en el último periodo, contenidas en un documento JSON. Cada
lectura posee las siguientes variables:

- `timestamp`: Marca temporal en la que se realizó la lectura, en tiempo Unix.
- `flow`: Flujo de aire, expresado en litros por minuto (l/m).
- `pressure`: Presión del aire, expresada en centímetros de agua
  (cmH<sub>2</sub>).
- `volume`: Volumen de aire, expresado en mililitros (ml).

__Ejemplo__
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

Como parte del control de la operación del respirador, el sistema lanza alarmas
cuando se exceden ciertos rangos para los parámetros u ocurren otras situaciones
no deseadas. Cuando sucede una alarma, el sistema lanza un evento de este tipo,
junto con un documento JSON con los siguientes valores:

- `type`: El tipo de alarma. Puede ser: `apnea`, `disconnect`, `min_pressure`,
  `max_pressure`, `min_volume`, `max_volume`, `max_frequency` u `oxygen`.
- `criticality`: Nivel de criticalidad, puede ser `normal` o `high`.

__Ejemplo__
```JSON
{
  "type": "apnea",
  "criticality": "normal"
}
