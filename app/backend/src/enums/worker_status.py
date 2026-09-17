from enum import Enum

class WorkerStatus(str, Enum):
    # machine found not capable after pen test
    rejected = "rejected" 

    # approved, waiting for user to "activate" their machine
    pending = "pending"

    # machine can be used to run a simulation
    # on graph page
    active = "active"

    # machine powered off or not connected to network
    idle = "idle"

    # user deactivated their machine, does not want it to be used anymore
    deactivated = "deactivated"

    # admin removed for some reason, was idle for long, or unable to complete runs or something
    removed = "removed"