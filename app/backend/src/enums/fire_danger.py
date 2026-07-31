from enum import Enum


class FireDanger(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very high"
