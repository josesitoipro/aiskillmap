from dataclasses import dataclass

@dataclass(frozen=True)
class CoreMessages:
    INTERNAL_SERVER_ERROR:  str = "Internal server error occurred. Check the log_system table for more details."
    UNAUTHORIZED:           str = "You are not authorized to perform this action."
    BAD_REQUEST:            str = "Bad request."