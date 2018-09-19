from ika.service import Command, Permission
from ika.models import Application


class RegisterApp(Command):
    name = '앱등록'
    aliases = (
        '새앱',
        'NEWAPP',
        'REGISTERAPP',
    )
    syntax = '<앱 이름> <앱 약어 (최대 4자)>'
    regex = r'(?P<appname>\S+) (?P<appslug>[a-z]{1,4})'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 앱을 등록합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 해당 앱을 등록하며,',
        '그 뒤로 네트워크에서 제공하는 여러 앱 전용 기능등을 이용하실 수 있습니다.',
        ' ',
        '앱 약어는 영문 소문자 최소 1글자에서 최대 4글자까지 입력하실 수 있습니다.',
        '앱 이름과 앱 약어는 모두 고유하며, 공백은 허용되지 않습니다.',
    )

    async def execute(self, user, appname, appslug):
        if Application.objects.filter(name__iexact=appname).exists():
            self.err(user, f'해당 앱 이름 \x02{appname}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.')

        if Application.objects.filter(slug__iexact=appslug).exists():
            self.err(user, f'해당 앱 약어 \x02{appslug}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.')

        app = Application()
        app.name = appname
        app.slug = appslug
        app.developer = user.account
        app.save()

        self.msg(user, f'해당 앱 \x02{appname}\x02 의 등록이 완료되었습니다. '
                       f'API 토큰은 다음과 같습니다: [ \x02{app.token}\x02 ]')
