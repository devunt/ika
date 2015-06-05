import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.database import Account, Nick, Session


class ForceChangeVirtualHost(Command):
    name = '강제가상호스트변경'
    aliases = (
    )
    syntax = '<계정명> [새 가상 호스트]'
    regex = r'(?P<name>\S+)( (?P<new_vhost>\S+))?'
    permission = Permission.OPERATOR
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 계정의 가상 호스트를 강제로 설정하거나 삭제합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 계정의 가상 호스트를 강제로 설정하거나 삭제할 수 있습니다.',
    )

    @asyncio.coroutine
    def execute(self, user, name, new_vhost):
        session = Session()
        account = session.query(Account).filter(Nick.name == name).first()
        if account is None:
            self.service.msg(user, '등록되지 않은 계정입니다.')
            return
        account.vhost = new_vhost
        session.commit()
        self.service.writesvsuserline('CHGHOST {} {}', user.uid, account.vhost or user.host)
        self.service.msg(user, '\x02{}\x02 계정의 가상 호스트가 \x02{}\x02 로 변경되었습니다.', user.account.name.name, new_vhost or '(없음)')
