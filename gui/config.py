from common.config import BaseConfig


class Config(BaseConfig):
    """Base configuration for the GUI application."""

    FONT_FAMILY = "Helvetica"
    FONT_SIZE_BIG = 20
    FONT_SIZE_MEDIUM = 15
    FONT_SIZE_SMALL = 12


class DevelopmentConfig(Config):
    """Configuration for the development environment."""

    DEBUG = True
