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
    for token in (' +', ' -'):
        if token in middle_n_trailing[0]:
            middle, semi_trailing = middle_n_trailing[0].split(token, 1)
            semi_trailing = token[1:] + semi_trailing
            break
    else:
        middle = middle_n_trailing[0]
        semi_trailing = None
    command, *params = middle.split(' ')
    if semi_trailing:
        params.append(semi_trailing)
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


def apply_modes(cmodes, mdict, mlist):
    modes = mlist[0]
    params = mlist[1:]
    remove = False
    for m in modes:
        if m == '+':
            remove = False
        elif m == '-':
            remove = True
        if remove:
            if m in cmodes[0]:
                mdict[m].remove(params.pop(0))
                if len(mdict[m]):
                    del mdict[m]
            elif m in cmodes[1]:
                del mdict[m]
                del params[0]
            elif m in (cmodes[2] + cmodes[3]):
                del mdict[m]
        else:
            if m in cmodes[0]:
                if m not in mdict:
                    mdict[m] = list()
                mdict[m].append(params.pop(0))
            elif m in (cmodes[1] + cmodes[2]):
                mdict[m] = params.pop(0)
            elif m in cmodes[3]:
                mdict[m] = None
    return mdict


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

