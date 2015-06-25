import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.database import Nick, Session


class Ungroup(Command):
    name = '그룹해제'
    aliases = (
        '닉네임제거',
        '닉제거',
        'UNGROUP',
    )
    syntax = '[제거할 닉네임]'
    regex = r'(?P<name>\S+)?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정에서 닉네임을 제거합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정에서 닉네임을 제거할 수 있습니다.',
        '제거할 닉네임이 지정되지 않을 시 현재 사용중인 닉네임으로 시도합니다.',
    )

    @asyncio.coroutine
    def execute(self, user, name):
        if name is None:
            name = user.nick
        session = Session()
        nick = Nick.find_by_name(name)
        if nick is None:
            self.service.msg(user, '\x02{}\x02 계정에 \x02{}\x02 닉네임이 등록되어 있지 않습니다.', user.account.name.name, name)
        elif user.account.name is nick:
            self.service.msg(user, '\x02{}\x02 닉네임이 해당 계정의 기본 닉네임으로 지정되어 있어 제거할 수 없습니다. 기본 닉네임을 수정해주세요.', name)
        else:
            account = user.account
            account.aliases.remove(nick)
            session.delete(nick)
            session.commit()
            self.service.msg(user, '\x02{}\x02 계정에서 \x02{}\x02 닉네임을 제거했습니다.', user.account.name.name, name)
