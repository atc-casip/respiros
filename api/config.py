from common.config import BaseConfig


class Config(BaseConfig):
    """Configuration for the Flask server."""

    PORT = 8000


class DevelopmentConfig(Config):
    """Configuration for the development environment."""

    DEBUG = True
