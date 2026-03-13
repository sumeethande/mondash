from enum import Enum, auto

class DashboardState(Enum):

    NOT_READY = auto()
    COMPUTING = auto()
    READY = auto()
    ERROR = auto()
    
class DashboardType(Enum):
    OVERVIEW = auto()
    PRODUCT = auto()
    FORCAST = auto()

class ValidationError(Enum):
    COLUMN_UNMAPPED = "COLUMN UNMAPPED"
    COLUMN_MULTIMAPPED = "COLUMN MULTI-MAPPED"
    DATA_TYPE_MISMATCH = "DATA-TYPE MISMATCH"
    NULL_OKAY_FAILED = "NULL TEST FAILED"

    @property
    def err_text(self) -> str:
        return self.value
