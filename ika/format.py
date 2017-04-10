from enum import IntEnum


class Color(IntEnum):
    WHITE = 0
    BLACK = 1
    NAVY = 2
    GREEN = 3
    RED = 4
    BROWN = 5
    PURPLE = 6
    ORANGE = 7
    YELLOW = 8
    LIME = 9
    TEAL = 10
    CYAN = 11
    BLUE = 12
    PINK = 13
    GREY = 14
    SILVER = 15


def bold(msg: str) -> str:
    return f'\x02{msg}\x02'


def underline(msg: str) -> str:
    return f'\x1f{msg}\x1f'


def colorize(msg: str, color: Color) -> str:
    return f'\x03{color.value:02}{msg}\x03'
