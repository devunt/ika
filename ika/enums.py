from enum import Enum


class Permission(Enum):
    EVERYONE = 0
    LOGIN_REQUIRED = 1
    OPERATOR = 2
