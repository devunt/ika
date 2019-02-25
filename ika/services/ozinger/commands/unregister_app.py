from ika.service import Command, Permission
from ika.models import Application


class UnregisterApp(Command):
    name = '앱등록해제'
    aliases = (
        '앱삭제',
        'DELETEAPP',
        'UNREGISTERAPP',
    )
    syntax = '<앱 이름> YES'
    regex = r'(?P<appname>\S+) (?P<confirmed>YES)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 앱의 등록을 해제합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 앱의 \x02등록을 해제\x02하며,',
        '그 뒤로는 네트워크에서 제공하는 여러 앱 전용 기능들을 이용하실 수 없습니다.',
        ' ',
        '실수로 명령을 실행하는 것을 방지하기 위해 명령 맨 뒤에 \x02YES\x02 를 붙여야 합니다.',
    )

    async def execute(self, user, appname, confirmed):
        if confirmed != 'YES':
            return

        app = Application.objects.filter(name__iexact=appname).first()
        if (not app) or app.developer != user:
            self.err(user, f'해당 앱 \x02{appname}\x02 의 등록을 해제할 수 있는 권한이 없습니다.')

        app.delete()

        self.msg(user, f'해당 앱 \x02{appname}\x02 의 등록이 해제되었습니다.')
        self.notify_admins(f'App `{appname}` ({app.slug}) deregisterd by {app.developer}')
