import inspect
from importlib import import_module, reload as reload_module
from time import time

from ika.enums import Message


def import_class_from_module(name):
    try:
        _module = reload_module(import_module(name))
    except ImportError:
        from ika.logger import logger
        logger.exception(f'Missing module!: {name}')
    else:
        _, cls = inspect.getmembers(_module, lambda member: inspect.isclass(member)
            and member.__module__ == name)[0]
        return cls


def tokenize_modestring(modesdef, modestring, *params) -> (dict, dict):
    params = list(params)
    adds = dict()
    removes = dict()
    target = adds
    for c in modestring:
        if c == '+':
            target = adds
        elif c == '-':
            target = removes
        else:
            if (c in modesdef.get('A', '')) or (c in modesdef.get('B', '')) or ((c in modesdef.get('C', '')) and (target is adds)):
                target[c] = params.pop(0)
            elif c in modesdef.get('D', ''):
                target[c] = None
    return adds, removes


def parseline(line: str) -> (Message, str, str, list):
    prefix = None
    message_type = Message.INVALID
    if line[0] == ':':
        prefix, line = line.split(' ', 1)
        prefix = prefix[1:]
        if len(prefix) == 3:
            message_type = Message.SERVER
        elif len(prefix) == 9:
            message_type = Message.USER
    else:
        message_type = Message.HANDSHAKE
    middle_n_trailing = line.split(' :', 1)
    command, *params = middle_n_trailing[0].split(' ')
    if len(middle_n_trailing) == 2:
        params.append(middle_n_trailing[1])
    return message_type, prefix, command, params


def base36encode(number):
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36 or alphabet[0]


def unixtime():
    return int(time())


class Map(dict):
    __getattr__ = dict.get

    def __init__(self, data=(lambda: {})()):
        super().__init__()
        for k, v in data.items():
            if isinstance(v, dict):
                v = Map(v)
            self[k] = v


class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __delitem__(self, key):
        return super().__delitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())

    def get(self, k, *args, **kwargs):
        return super().get(k.lower(), *args, **kwargs)

