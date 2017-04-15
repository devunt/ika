from ika.service import Command, Permission
from ika.models import Channel


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

            modestring = irc_channel.generate_synchronizing_modestring()
            if modestring:
                self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, modestring)
                count += 1

        self.msg(user, f'총 {count}개 채널에 권한이 동기화되었습니다.')
