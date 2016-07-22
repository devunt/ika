import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.database import Channel


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

    @asyncio.coroutine
    def execute(self, user, name):
        if name is None:
            channels = Channel.query.all();
        else:
            channels = (Channel.find_by_name(name),)
        for channel in channels:
            real_channel = self.service.server.channels.get(channel.name.lower())
            for uid, user in real_channel.users.items():
                flags = channel.get_flags_by_user(user)
                modes = str()
                for flag, mode in self.modemap.items():
                    if (flags & flag) != 0:
                        modes += mode
                if len(modes) > 0:
                    self.service.writesvsuserline('FMODE {} {} +{} {}', real_channel.name, real_channel.timestamp, modes,
                                                  ' '.join((user.uid,) * len(modes)))
