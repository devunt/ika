from ika.service import Command, Service, Permission


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

    async def execute(self, user, command):
        target = None
        if command:
            if command in self.service.commands:
                target = self.service.commands[command]
            else:
                self.err(user, f'해당 명령이 존재하지 않아 도움말을 찾을 수 없습니다. \x02/msg {self.service.name} 도움말\x02 을 입력해보세요.')
        else:
            target = self.service
        self.msg(user, f'==== \x02{target.name}\x02 도움말 ====')
        if isinstance(target, Command):
            self.msg(user, f'사용법: \x02/msg {self.service.name} {target.name} {target.syntax}\x02')
        self.msg(user, ' ')
        for description in target.description:
            self.msg(user, description)
        if isinstance(target, Service):
            self.msg(user, ' ')
            commands = set()
            for _, command in self.service.commands.items():
                if ((command.permission is Permission.LOGIN_REQUIRED) and (user.account is None)) or \
                        ((command.permission is Permission.OPERATOR) and (not user.is_operator)):
                    continue
                if command not in commands:
                    commands.add(command)
                    self.msg(user, f'\x02{command.name:\u3000<10}\x02{command.description[0]}')
        if len(target.aliases) > 0:
            self.msg(user, ' ')
            self.msg(user, '다른 이름들: \x02{}\x02', '\x02, \x02'.join(target.aliases))
