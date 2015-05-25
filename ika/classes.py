class Channel:
    users = dict()

    def __init__(self, *params):
        self.name = params[0]
        self.timestamp = int(params[1])
        self.modes = params[2]
        for user in params[3].split():
            mode, uid = user.split(b',')
            self.users[uid] = mode

        print(self.name)
        print(self.timestamp)
        print(self.modes)
        print(self.users)

    def update(self, *params):
        pass
