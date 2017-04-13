from ika.service import Command, Permission
from ika.ircobjects import IRCChannel
from ika.utils import tokenize_modestring


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

    async def execute(self, user, target, mode):
        try:
            modestring = mode
            if target.startswith('#'):
                target_uid_or_cname = target
                timestamp = self.server.channels[target].timestamp
                t = tokenize_modestring(IRCChannel.umodesdef, *mode.split())
                for d in t:
                    for s in d.values():
                        for v in s:
                            try:
                                modestring = modestring.replace(v, self.server.nicks[v].uid)
                            except KeyError:
                                target = v
                                raise
            else:
                target_user = self.server.nicks[target]
                target_uid_or_cname = target_user.uid
                timestamp = target_user.timestamp
        except KeyError:
            self.msg(user, f'\x02{target}\x02 채널이나 유저가 존재하지 않습니다.')
        else:
            self.writesvsuserline('FMODE', target_uid_or_cname, timestamp, modestring)
            self.msg(user, f'\x02{target}\x02에 \x02{mode}\x02모드를 설정했습니다.')
