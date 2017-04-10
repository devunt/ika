import asyncio

from ika.service import Command, Service
from ika.enums import Permission


class Help(Command):
    name = '도움말'
    aliases = (
        '도움',
        'HELP',
        '?'
    )
    syntax = '[명령어 이름]'
    regex = r'(?P<command>\S+)?'
    description = (
        '특정 서비스봇이나 명령에 대한 도움말을 보여줍니다.',
    )

    @asyncio.coroutine
    def execute(self, user, command):
        if command:
            command = command.upper()
            if command in self.service.commands:
                target = self.service.commands[command]
            else:
                self.service.msg(user, '해당 명령이 존재하지 않아 도움말을 찾을 수 없습니다. \x02/msg {} 도움말\x02 을 입력해보세요.', self.service.name)
                return
        else:
            target = self.service
        self.service.msg(user, '==== \x02{}\x02 도움말 ====', target.name)
        if isinstance(target, Command):
            self.service.msg(user, '사용법: \x02/msg {} {} {}\x02', self.service.name, target.name, target.syntax)
        self.service.msg(user, ' ')
        for description in target.description:
            self.service.msg(user, description)
        if isinstance(target, Service):
            self.service.msg(user, ' ')
            commands = list()
            for _, command in self.service.commands.items():
                if ((command.permission is Permission.LOGIN_REQUIRED) and ('accountname' not in user.metadata)) or \
                        ((command.permission is Permission.OPERATOR) and (not user.is_operator)):
                    continue
                if command not in commands:
                    commands.append(command)
                    self.service.msg(user, '\x02{:\u3000<10}\x02{}', command.name, command.description[0])
        if len(target.aliases) > 0:
            self.service.msg(user, ' ')
            self.service.msg(user, '다른 이름들: \x02{}\x02'.format('\x02, \x02'.join(target.aliases)))
