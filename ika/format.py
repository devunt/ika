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


class Formatter:
    @staticmethod
    def bold(msg: str) -> str:
        return '\x02{}\x02'.format(msg)

    @staticmethod
    def underline(msg: str) -> str:
        return '\x1f{}\x1f'.format(msg)

    @staticmethod
    def color(msg: str, color: Color) -> str:
        return '\x03{:02}{}\x03'.format(color.value, msg)
