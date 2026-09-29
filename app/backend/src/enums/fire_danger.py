from enum import Enum


class FireDanger(str, Enum):
    low = "LOW"
    moderate = "MODERATE"
    dangerous = "DANGEROUS"
    very_dangerous = "VERY DANGEROUS"
    extremely_dangerous = "EXTREMELY DANGEROUS"
