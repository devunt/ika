import asyncio
from datetime import datetime
from sqlalchemy.sql import exists

from ika.classes import Command
from ika.database import Nick, Account, Session


class Group(Command):
    name = '그룹'
    aliases = (
        '닉네임추가',
        '닉추가',
    )
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정에 현재 사용중인 닉네임을 추가합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정에 현재 사용중인 닉네임을 추가합니다.',
        '계정 1개에는 최대 3개의 닉네임을 추가적으로 등록할 수 있습니다.',
    )

    @asyncio.coroutine
    def execute(self, uid):
        user = self.service.server.users[uid]
        accountname = user.metadata.get('accountname')
        if accountname is None:
            self.service.msg(uid, '로그인되어 있지 않습니다. \x02/msg {} 로그인\x02 명령을 이용해 로그인해주세요.', self.service.name)
            return
        session = Session()
        account = session.query(Account).filter(Nick.name == accountname).first()
        if len(account.aliases) >= 3:
            self.service.msg(uid, '\x02{}\x02 계정에 등록할 수 있는 닉네임 제한을 초과했습니다 (3개).', account.name.name)
            return
        if session.query(exists().where(Nick.name == user.nick)).scalar():
            self.service.msg(uid, '이미 등록되어 있는 닉네임입니다.')
            return
        nick = Nick()
        nick.name = user.nick
        nick.last_use = datetime.now()
        session.add(nick)
        session.commit()
        account.aliases.append(nick)
        session.add(account)
        session.commit()
        self.service.msg(uid, '\x02{}\x02 계정에 \x02{}\x02 닉네임을 추가했습니다.', account.name.name, nick.name)
