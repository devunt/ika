import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.utils import timeutils


class Mode(Command):
    name = 'MODE'
    aliases = (
    )
    syntax = '<채널 또는 유저> <모드>'
    regex = r'(?P<target>\S+) (?P<mode>.+)'
    permission = Permission.OPERATOR
    description = (
        '특정 채널이나 유저에 모드를 설정합니다.',
    )

    @asyncio.coroutine
    def execute(self, user, target, mode):
        try:
            if target.startswith('#'):
                _target = target
                timestamp = self.service.server.channels[target].timestamp
            else:
                for u in self.service.server.users.values():
                    if u.nick == target:
                        _target = u.uid
                        timestamp = u.timestamp
                        break
                else:
                    raise KeyError()
        except KeyError:
            self.service.msg(user, '\x02{}\x02 채널이나 유저가 존재하지 않습니다.', target)
        else:
            self.service.writesvsuserline('FMODE {} {} {}', target, timestamp, mode)
            self.service.msg(user, '\x02{}\x02에 \x02{}\x02모드를 설정했습니다.', target, mode)
