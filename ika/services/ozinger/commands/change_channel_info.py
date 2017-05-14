from ika.service import Command, Permission
from ika.enums import Flags
from ika.models import Channel


class ChangeChannelInfo(Command):
    name = '채널정보변경'
    aliases = (
        '채널정보',
        'CHANNELINFO',
        'CHANGECHANNELINFO',
    )
    syntax = '<#채널명> <변경할 정보 이름> [지정 문구]'
    regex = r'(?P<cname>#\S+) (?P<name>\S+)( (?P<value>.*))?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 정보를 설정하거나 제거합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 채널의 정보를 설정하거나 제거할 수 있습니다.',
        '지정 문구가 있을 시 해당 인자로 해당 정보를 설정하며, 문구가 없을 시 해당 정보를 제거합니다.',
        ' ',
        '현재 변경할 수 있는 정보의 목록은 다음과 같습니다:',
    )

    keymap = {
        '진입글': 'entrymsg',
        '웹사이트': 'url',
        '이메일': 'email',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        descriptions = list()
        for k in self.keymap.keys():
            descriptions.append(f'  - {k}')
        self.description += tuple(descriptions)

    async def execute(self, user, cname, name, value):
        channel = Channel.get(cname)

        if channel is None:
            if user.is_operator:
                self.err(user, f'해당 채널 \x02{cname}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')
            else:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        if Flags.OWNER not in channel.get_flags_by_user(user):
            if not user.is_operator:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        key = self.keymap.get(name)
        if not key:
            self.err(user, f'\x02{name}\x02 은 지원하지 않는 정보입니다. 자세한 내용은 {self.refer_command(self, "?")} 를 참조하세요.')

        if value:
            channel.data[key] = value
        else:
            channel.data.pop(key, None)

        channel.save()

        self.msg(cname, f'\x02{user.nick}\x02 사용자가 \x02{channel}\x02 채널의 \x02{name}\x02 정보를 \x02{value or "(없음)"}\x02 (으)로 변경했습니다.')
        self.msg(user, f'\x02{channel}\x02 채널의 \x02{name}\x02 정보가 \x02{value or "(없음)"}\x02 (으)로 변경되었습니다.')
