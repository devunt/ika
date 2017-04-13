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
        return set([v[1] for k, v in self.get_map() if k in self])

    @property
    def modestring(self):
        return ''.join(self.modes)

    @property
    def coloredstring(self):
        return ''.join([colorize(v[0], v[2]) for k, v in self.get_map() if k in self])

    @classmethod
    def get_by_character(cls, character):
        for k, v in cls.get_map():
            if v[0] == character:
                return k

    @classmethod
    def get_all_characters(cls):
        return [v[0] for k, v in cls.get_map()]

    @classmethod
    def get_map(cls):
        return {
            cls.OWNER:   ('Q', 'q', Color.PURPLE),
            cls.FOUNDER: ('F', 'q', Color.PURPLE),
            cls.PROTECT: ('A', 'a', Color.RED),
            cls.OP:      ('O', 'o', Color.LIME),
            cls.HALFOP:  ('H', 'h', Color.CYAN),
            cls.VOICE:   ('V', 'v', Color.ORANGE),
        }.items()
