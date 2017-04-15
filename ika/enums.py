from collections import namedtuple
from enum import Enum, IntFlag

from ika.format import Color, colorize


class Permission(Enum):
    EVERYONE = 0
    LOGIN_REQUIRED = 1
    OPERATOR = 2


class Message(Enum):
    INVALID = 0
    HANDSHAKE = 1
    SERVER = 2
    USER = 3


class Flags(IntFlag):
    OWNER = 64
    FOUNDER = 32
    PROTECT = 4
    OP = 16
    HALFOP = 8
    VOICE = 2

    @property
    def modes(self):
        return set([v.mode for k, v in FlagsDefinition.MAP.items() if k in self])

    @property
    def modestring(self):
        return ''.join(self.modes)

    @property
    def coloredstring(self):
        return ''.join([colorize(v.character, v.color) for k, v in FlagsDefinition.MAP.items() if k in self])

    @classmethod
    def get_by_character(cls, character):
        for k, v in FlagsDefinition.MAP:
            if v.character == character:
                return k

    @classmethod
    def get_all_characters(cls):
        return [v.character for k, v in FlagsDefinition.MAP.items()]


class FlagsDefinition:
    _ = namedtuple('Definition', ['character', 'mode', 'color'])

    MAP = {
        Flags.OWNER:   _('Q', 'q', Color.PURPLE),
        Flags.FOUNDER: _('F', 'q', Color.PURPLE),
        Flags.PROTECT: _('A', 'a', Color.RED),
        Flags.OP:      _('O', 'o', Color.LIME),
        Flags.HALFOP:  _('H', 'h', Color.CYAN),
        Flags.VOICE:   _('V', 'v', Color.ORANGE),
    }
