class BaseConfig:
    """Common configuration for all processes."""

    DEBUG = False
    TESTING = False

    ZMQ_MONITOR_ADDR = "ipc:///tmp/monitor"
    ZMQ_OPERATION_ADDR = "ipc:///tmp/operation"
    ZMQ_SYNC_CONTROLS_ADDR = "ipc:///tmp/sync-controls"
    ZMQ_SYNC_GUI_ADDR = "ipc:///tmp/sync-gui"
    ZMQ_SYNC_API_ADDR = "ipc:///tmp/sync-api"

    IPAP_DEFAULT = 15
    EPAP_DEFAULT = 5
    FREQ_DEFAULT = 15
    TRIGGER_DEFAULT = 5
    INHALE_DEFAULT = 1
    EXHALE_DEFAULT = 2

    IPAP_MIN = 3
    EPAP_MIN = 2
    FREQ_MIN = 2
    TRIGGER_MIN = 2

    IPAP_MAX = 35
    EPAP_MAX = 34
    FREQ_MAX = 30
    TRIGGER_MAX = 12
    INHALE_MAX = 5
    EXHALE_MAX = 5

    ALARM_PRESSURE_MIN = 2
    ALARM_VOLUME_MIN = 2
    ALARM_OXYGEN_MIN = 21
    ALARM_FREQ_MIN = 2

    ALARM_PRESSURE_MAX = 35
    ALARM_VOLUME_MAX = 12
    ALARM_OXYGEN_MAX = 100
    ALARM_FREQ_MAX = 40
