from enum import Enum, IntEnum


class Permission(Enum):
    EVERYONE = 0
    LOGIN_REQUIRED = 1
    OPERATOR = 2


class Flags(IntEnum):
    OWNER = 64
    FOUNDER = 32
    PROTECT = 4
    OP = 16
    HALFOP = 8
    VOICE = 2
