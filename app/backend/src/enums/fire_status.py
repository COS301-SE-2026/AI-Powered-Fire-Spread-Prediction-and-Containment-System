from enum import Enum

class FireStatus(str, Enum):
    active = "active"
    contained = "contained"
    extinguished = "extinguished"
    
# higher wins when 2 fires merge
fire_status_severity = {
    FireStatus.active: 2,
    FireStatus.contained: 1,
    FireStatus.extinguished: 0,
}

