from ika.service import Command, Permission


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
            if target.startswith('#'):
                target_uid_or_cname = target
                timestamp = self.server.channels[target].timestamp

                params = mode.split()
                if len(params) == 2:
                    users = {v.nick.lower(): k for k, v in self.server.users.items()}
                    user = users.get(params[2].lower())
                    if user is not None:
                        method = 'update' if params[0][0] == '+' else 'difference_update'
                        getattr(self.server.channels[target.lower()].usermodes[user.uid], method)(params[0][1:])
            else:
                for user in self.server.users.values():
                    if user.nick.lower() == target.lower():
                        target_uid_or_cname = user.uid
                        timestamp = user.timestamp
                        break
                else:
                    raise KeyError
        except KeyError:
            self.msg(user, f'\x02{target}\x02 채널이나 유저가 존재하지 않습니다.')
        else:
            self.writesvsuserline('FMODE', target_uid_or_cname, timestamp, mode)
            self.msg(user, f'\x02{target}\x02에 \x02{mode}\x02모드를 설정했습니다.')
