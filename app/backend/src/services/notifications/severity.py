# How serious the fire is (how big is it)
from decimal import Decimal

from app.backend.src.enums.severity import Severity

# Note: boundary_radius is stored as Numeric(5,2) on FireReports.
# Adjust these thesholds to match how boundary_radius is actually set in reporting flow (eg. estimated automatically vs fixed default)

LOW_MAX_KM = 0.5
MODERATE_MAX_KM = 2.0
HIGH_MAX_KM = 5.0
# Anything higher than HIGH_MAX_KM is 'extreme'


def severity_from_boundary_radius(boundary_radius: Decimal | float) -> Severity:
    radius = float(boundary_radius)

    if radius <= LOW_MAX_KM:
        return Severity.low
    if radius <= MODERATE_MAX_KM:
        return Severity.moderate
    if radius <= HIGH_MAX_KM:
        return Severity.high
    return Severity.extreme
