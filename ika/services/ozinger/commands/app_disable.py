from ika.service import Command, Permission
from ika.models import Application, Channel
from ika.enums import Flags


class EnableApp(Command):
    name = '앱비활성화'
    aliases = (
        '앱떼기',
        'disableapp',
        'detachapp',
    )
    syntax = '<#채널명> <앱 이름>'
    regex = r'(?P<cname>#\S+) (?P<appname>\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널에 앱을 비활성화합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널에 특정 앱을 비활성화할 수 있습니다.',
        '채널에 앱을 비활성화할 시 해당 앱의 개발자가 더 이상 해당 앱을 이용해 본 채널의 메시지를 읽거나 쓸 수 없습니다.',
        ' ',
        '본 명령을 이용하기 위해서는 해당 채널에 운영자 (+Q) 이상의 권한이 필요합니다.',
    )

    async def execute(self, user, cname, appname):
        channel = Channel.get(cname)

        if channel is None:
            if user.is_operator:
                self.err(user, f'해당 채널 \x02{cname}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')
            else:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        if Flags.OWNER not in channel.get_flags_by_user(user):
            if not user.is_operator:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        app = Application.objects.filter(name__iexact=appname).first()
        if app is None or not channel.apps.filter(pk=app.pk).exists():
            self.err(user, f'해당 채널 \x02{channel.name}\x02에 \x02{appname}\x02 앱이 활성화되어있지 않습니다.')

        channel.apps.remove(app)

        self.msg(user, f'해당 채널 \x02{channel.name}\x02에 \x02{app.name}\x02 앱이 비활성화되었습니다.')
        self.writesvsuserline(f'NOTICE {channel.name} : {user.nick} 님이 채널에서 {app.name} 앱을 제거했습니다.')
