"""
Application configuration.
"""

import yaml

with open("config.yaml") as file:
    cfg = yaml.full_load(file)
