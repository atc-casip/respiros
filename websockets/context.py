"""
System context.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Context:
    """Necessary context for system operation."""

    # Operational parameters
    ipap: int = None
    epap: int = None
    freq: int = None
    trigger: int = None
    inhale: int = None
    exhale: int = None

    # Readings' buffer
    readings: List[Dict] = field(default_factory=list)
