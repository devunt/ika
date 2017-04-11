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

    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            coroutine = handler(*args, **kwargs)
            if asyncio.iscoroutine(coroutine):
                asyncio.ensure_future(coroutine)


class EventListener:
    def __init__(self):
        self.__hooks = dict()

    def __getattr__(self, item):
        if item in self.__hooks.keys():
            hook = self.__hooks[item]
        else:
            hook = EventHook()
            self.__hooks[item] = hook
        return hook
