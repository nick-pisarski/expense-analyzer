from enum import Enum


class Source(Enum):
    """Enum for the source of a transaction"""

    BANK_OF_AMERICA = "bank_of_america"
    UNKNOWN = "unknown"
