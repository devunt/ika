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
    FOUNDER = 32
    OWNER = 64
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
    def get_by_character_for_mutation(cls, character):
        for k, v in FlagsDefinition.MAP.items():
            if v.mutable and (v.character == character):
                return k
        return 0

    @classmethod
    def get_all_characters(cls):
        return [v.character for k, v in FlagsDefinition.MAP.items()]


class FlagsDefinition:
    _ = namedtuple('Definition', ['character', 'mode', 'mutable', 'color'])
    N = False
    Y = True

    MAP = {
        Flags.FOUNDER: _('F', 'q', N, Color.PURPLE),
        Flags.OWNER:   _('Q', 'q', Y, Color.PURPLE),
        Flags.PROTECT: _('A', 'a', Y, Color.RED),
        Flags.OP:      _('O', 'o', Y, Color.LIME),
        Flags.HALFOP:  _('H', 'h', Y, Color.CYAN),
        Flags.VOICE:   _('V', 'v', Y, Color.ORANGE),
    }
