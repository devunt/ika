import asyncio


class EventHook:
    def __init__(self):
        self.__handlers = list()

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **kwargs):
        for handler in self.__handlers:
            asyncio.async(handler(*args, **kwargs))


class EventHandler:
    events = (
        'FJOIN',
        'FMODE',
        'NICK',
        'OPERTYPE',
        'PART',
        'QUIT',
        'TOPIC',
        'UID',
    )

    def __init__(self):
        for event in self.events:
            hook = EventHook()
            setattr(self, event, hook)
