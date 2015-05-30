import asyncio

from ika.classes import Command


class Help(Command):
    name = '도움말'
    aliases = [
        '도움'
    ]
    syntax = '[명령어 이름]'
    description = [
        '특정 서비스봇이나 명령에 대한 도움말을 보여줍니다.',
    ]

    @asyncio.coroutine
    def execute(self, uid, *params):
        if len(params) == 0:
            target = self.service
        else:
            command = params[0]
            if command in self.service.commands:
                target = self.service.commands[command]
            else:
                self.service.msg(uid, '해당 명령이 존재하지 않아 도움말을 찾을 수 없습니다. \x02/msg {} 도움말\x02 을 입력해보세요.', self.service.name)
                return
        self.service.msg(uid, '==== \x02{}\x02 도움말 ====', target.name)
        if isinstance(target, Command):
            self.service.msg(uid, '사용법: \x02/msg {} {} {}\x02', self.service.name, target.name, target.syntax)
        self.service.msg(uid, ' ')
        for description in target.description:
            self.service.msg(uid, description)
        self.service.msg(uid, ' ')

        commands = list()
        for _, command in self.service.commands.items():
            if command not in commands:
                commands.append(command)
                self.service.msg(uid, '\x02{:\u3000<10}\x02{}', command.name, command.description[0])
