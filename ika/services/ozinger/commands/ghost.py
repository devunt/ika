import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.database import Account


class Ghost(Command):
    name = '고스트'
    aliases = (
    )
    syntax = '<닉네임>'
    regex = r'(?P<nick>\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록된 계정에 연결된 닉네임을 사용중인 사용자의 연결을 강제로 끊습니다.',
        ' ',
        '오징어 IRC 네트워크에 등록되어 있는 계정에 연결된 닉네임을 사용중인 사용자의 연결을 강제로 종료합니다.',
        '기존에 연결되어 있는 본인의 접속 세션을 끊을 수도 있고,',
        '본인이 등록한 닉네임을 허락 없이 쓰고 있는 사용자의 연결을 강제로 종료시킬 수도 있습니다.',
    )

    @asyncio.coroutine
    def execute(self, user, nick):
        account = Account.find_by_nick(nick)
        if account is not user.account:
            self.service.msg(user, '해당 닉네임이 \x02{}\x02 계정에 속해 있지 않습니다.', user.account.name.name)
            return
        for target in self.service.server.users.values():
            if target.nick == nick:
                self.service.writesvsuserline('KILL {} :{}!{}@{} 에 의한 고스트', target.uid, user.nick, user.ident, user.dhost)
