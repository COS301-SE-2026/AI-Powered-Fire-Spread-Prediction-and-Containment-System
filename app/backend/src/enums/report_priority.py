from enum import Enum

class ReportPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"

priority_level = {
    ReportPriority.low: 0,
    ReportPriority.normal: 1,
    ReportPriority.high: 2,
}