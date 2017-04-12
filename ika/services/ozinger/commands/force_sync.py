from ika.service import Command, Permission
from ika.models import Channel
from ika.enums import Flags


class ForceSynchronise(Command):
    name = '강제동기화'
    aliases = (
        'FSYNC',
    )
    syntax = '[채널명]'
    regex = r'(?P<name>\S+)?'
    permission = Permission.OPERATOR
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널들의 권한 상태를 강제로 데이터베이스와 동기화합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널들의 권한 상태를 강제로 데이터베이스와 동기화합니다.',
        '채널명을 지정할 시 해당 채널만, 지정하지 않을 시 네트워크에 등록되어 있는 모든 채널들을 동기화합니다.',
        '단, 기존에 추가되어 있는 권한은 회수되지 않으며 기존에 부여되지 않았던 권한만 추가적으로 부여됩니다.',
    )

    async def execute(self, user, name):
        if name is None:
            channels = Channel.objects.all()
        else:
            channel = Channel.get(name)
            if channel is None:
                self.err(user, '등록되지 않은 채널입니다.')
            channels = [channel]
        count = 0
        for channel in channels:
            irc_channel = self.server.channels.get(channel.name)
            if irc_channel is None:
                continue
            for uid in irc_channel.umodes.keys():
                joined_user = self.server.users[uid]
                flags = Flags(channel.get_flags_by_user(joined_user))
                if flags:
                    modestring = flags.modestring
                    self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, f'+{modestring}', *((uid,) * len(modestring)))
            count += 1
        self.msg(user, f'{count}개 채널에 권한이 동기화되었습니다.')
