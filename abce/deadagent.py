

def nothing(*_, **__):
    pass

class DeadAgent:
    def __getattr__(self, *_, **__):
        return nothing

    def __setattr__(self, *_, **__):
        return nothing

    def _execute(self, command, incomming_messages):
        return []
