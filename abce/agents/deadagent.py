from builtins import object


def nothing(*_, **__):
    pass


class SilentDeadAgent(object):
    def __getattr__(self, *_, **__):
        return nothing

    def __setattr__(self, *_, **__):
        return nothing

    def _execute(self, command, incomming_messages):
        return []


class LoudDeadAgent(object):
    def __getattr__(self, *_, **__):
        return nothing

    def __setattr__(self, *_, **__):
        return nothing

    def _execute(self, command, incomming_messages):
        if incomming_messages:
            print(incomming_messages)
            raise Exception("Message to dead agent")
        return []
