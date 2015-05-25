import asyncio

from ika.conf import settings


class Channel:
    users = dict()

    def __init__(self, *params):
        self.name = params[0]
        self.timestamp = int(params[1])
        self.modes = params[2]
        for user in params[3].split():
            mode, uid = user.split(b',')
            self.users[uid] = mode

    def update(self, *params):
        pass


class Service:
    aliases = []

    @property
    def uid(self):
        return '{0}{1}'.format(settings.server.sid, self.id)

    @property
    def ident(self):
        if 'ident' in self.__class__.__dict__:
            return self.ident
        else:
            return self.__class__.__name__.lower()

    @property
    def description(self):
        if 'description' in self.__class__.__dict__:
            return self.description
        else:
            return '사용법: /msg {0} 도움말'.format(self.name)

    @asyncio.coroutine
    def execute(self, future, line):
        future.set_exception(RuntimeError('You must override `execute` method of service class'))
