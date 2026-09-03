# Severity of fire for notifications

import enum


class Severity(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    extreme = "extreme"
