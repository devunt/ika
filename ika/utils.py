from time import time
from easydict import EasyDict as edict


class ircutils:
    @staticmethod
    def parseline(line):
        params = line.split()
        retparams = list()
        for x in range(0, len(params)):
            if params[x].startswith(b':'):
                retparams.append(b' '.join(params[x:])[1:])
                break
            retparams.append(params[x])
        return retparams


def unixtime():
    return int(time())


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
