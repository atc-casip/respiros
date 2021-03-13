from common.config import BaseConfig


class Config(BaseConfig):
    """Base configuration for the control application."""

    DHT_BOX_GPIO = 16
    DHT_AIR_GPIO = 16

    SERVO_GPIO = 15
    SERVO_MIN_WIDTH = 500
    SERVO_MAX_WIDTH = 2500

    ADC_SPI_CHANNEL = 0
    ADC_BAUD_RATE = 96000
    ADC_REF_VOLTAGE = 5
    ADC_GAUGE_CHANNEL = 4
    ADC_AIRFLOW_CHANNEL = 1
    ADC_ATM_CHANNEL = 5
    ADC_OXYGEN_CHANNEL = 2


class DevelopmentConfig(Config):
    """Configuration for the development environment."""

    DEBUG = True
