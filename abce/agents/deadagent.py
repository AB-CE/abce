from builtins import object


def nothing(*_, **__):
    pass


class SilentDeadAgent(object):
    inbox = []

    def __getattr__(self, *_, **__):
        return nothing

    def __setattr__(self, *_, **__):
        return nothing

    def _execute(self, command):
        return []


class LoudDeadAgent(object):
    inbox = []

    def __getattr__(self, *_, **__):
        return nothing

    def __setattr__(self, *_, **__):
        return nothing

    def _execute(self, command):
        if self.inbox:
            print(self.inbox)
            raise Exception("Message to dead agent")
        return []
